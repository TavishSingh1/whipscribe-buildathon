from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Clip, Episode, ProcessingJob, ShowNotes, SocialPost, UsageRecord
from app.services.context import load_creator_context
from app.worker.graph import create_workflow


STEP_PROGRESS = {
    "transcribe": 20,
    "find_moments": 40,
    "render_clips": 60,
    "generate_show_notes": 75,
    "generate_social_content": 90,
    "finalize": 100,
}


async def run_episode_job(db: AsyncSession, job_id: str) -> None:
    job = await db.get(ProcessingJob, job_id)
    if not job:
        return
    episode = await db.get(Episode, job.episode_id)
    if not episode or episode.user_id != job.user_id:
        return

    profile, examples = await load_creator_context(db, job.user_id, ["x", "linkedin", "instagram", "show_notes"])
    episode.status = "processing"
    job.current_step = "transcribe"
    job.started_at = datetime.utcnow()
    await db.commit()

    state = {
        "user_id": job.user_id,
        "episode_id": episode.id,
        "audio_path": episode.storage_url,
        "creator_profile": profile,
        "historical_examples": examples,
        "episode_metadata": {
            "title": episode.title,
            "description": episode.description,
            "guest": episode.guest,
            "topic": episode.topic,
            "additional_instructions": episode.additional_instructions,
            "clip_goal": episode.clip_goal,
            "social_goal": episode.social_goal,
        },
        "errors": [],
    }

    final_state = {}
    try:
        async for output in create_workflow().astream(state):
            for node_name, node_state in output.items():
                final_state.update(node_state)
                job.current_step = node_name
                job.progress = STEP_PROGRESS.get(node_name, job.progress)
                await db.commit()
        if final_state.get("errors"):
            episode.status = "failed"
            job.error_message = "; ".join(final_state["errors"])
        else:
            episode.status = "completed"
            episode.transcript = final_state.get("transcript")
            for clip in final_state.get("clips", []):
                db.add(
                    Clip(
                        user_id=job.user_id,
                        episode_id=episode.id,
                        title=clip.get("title", "Clip"),
                        start_time=float(clip.get("start_s", 0)),
                        end_time=float(clip.get("end_s", 0)),
                        video_url=clip.get("video_url"),
                        score_reason=clip.get("why", ""),
                    )
                )
            db.add(ShowNotes(user_id=job.user_id, episode_id=episode.id, summary=final_state.get("episode_summary", ""), chapters=final_state.get("chapters", [])))
            for platform, content in final_state.get("social_posts", {}).items():
                db.add(SocialPost(user_id=job.user_id, episode_id=episode.id, platform=platform, content=content))
            db.add(UsageRecord(user_id=job.user_id, episode_id=episode.id, clips_generated=len(final_state.get("clips", [])), llm_tokens_estimated=12000))
        job.progress = 100
        job.completed_at = datetime.utcnow()
        await db.commit()
    except Exception as exc:
        episode.status = "failed"
        job.error_message = "Processing failed. Please retry."
        job.completed_at = datetime.utcnow()
        await db.commit()
        raise exc
