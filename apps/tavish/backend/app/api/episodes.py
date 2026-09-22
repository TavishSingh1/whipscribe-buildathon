import asyncio
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.core.config import get_settings
from app.db.session import SessionLocal, get_db
from app.models import Clip, Episode, ProcessingJob, ShowNotes, SocialPost, User
from app.schemas.api import EpisodeOut, JobOut, SocialPostUpdate
from app.worker.processor import run_episode_job

router = APIRouter(prefix="/episodes", tags=["episodes"])
ALLOWED_TYPES = {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "video/mp4", "audio/ogg", "audio/webm", "audio/flac"}


async def _run_job_in_new_session(job_id: str):
    async with SessionLocal() as db:
        await run_episode_job(db, job_id)


@router.get("", response_model=list[EpisodeOut])
async def list_episodes(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Episode).where(Episode.user_id == user.id).order_by(Episode.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=JobOut)
async def create_episode(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(None),
    description: str | None = Form(None),
    guest: str | None = Form(None),
    topic: str | None = Form(None),
    additional_instructions: str | None = Form(None),
    clip_goal: str = Form("Balanced"),
    social_goal: str = Form("Engagement"),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported media type")
    suffix = Path(file.filename or "episode").suffix.lower()
    upload_root = Path(settings.upload_dir) / user.id
    upload_root.mkdir(parents=True, exist_ok=True)
    target = upload_root / f"{Path(file.filename or 'episode').stem}-{int(asyncio.get_running_loop().time())}{suffix}"
    size = 0
    with target.open("wb") as handle:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File too large")
            handle.write(chunk)
    episode = Episode(
        user_id=user.id,
        file_name=file.filename or target.name,
        file_type=file.content_type or "application/octet-stream",
        storage_url=str(target),
        title=title,
        description=description,
        guest=guest,
        topic=topic,
        additional_instructions=additional_instructions,
        clip_goal=clip_goal,
        social_goal=social_goal,
    )
    db.add(episode)
    await db.flush()
    job = ProcessingJob(user_id=user.id, episode_id=episode.id, current_step="queued", progress=0)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    background_tasks.add_task(_run_job_in_new_session, job.id)
    return job


@router.get("/{episode_id}")
async def get_episode(episode_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    episode = await db.get(Episode, episode_id)
    if not episode or episode.user_id != user.id:
        raise HTTPException(status_code=404, detail="Episode not found")
    clips = (await db.execute(select(Clip).where(Clip.user_id == user.id, Clip.episode_id == episode_id))).scalars().all()
    notes = (await db.execute(select(ShowNotes).where(ShowNotes.user_id == user.id, ShowNotes.episode_id == episode_id))).scalar_one_or_none()
    posts = (await db.execute(select(SocialPost).where(SocialPost.user_id == user.id, SocialPost.episode_id == episode_id))).scalars().all()
    return {"episode": episode, "clips": clips, "show_notes": notes, "social_posts": posts, "personalized_using": ["Creator profile", "Episode metadata", "Previous content examples when available"]}


@router.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(job_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    job = await db.get(ProcessingJob, job_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/social-posts/{post_id}")
async def update_social_post(post_id: str, payload: SocialPostUpdate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    post = await db.get(SocialPost, post_id)
    if not post or post.user_id != user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    post.content = payload.content
    await db.commit()
    return post
