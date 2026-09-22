from typing import Any, TypedDict

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.core.config import get_settings
from app.services.prompt_builders import build_moment_selection_prompt, build_show_notes_prompt, build_social_prompt
from app.services.whipscribe_client import WhipScribeClient


class PodcastState(TypedDict, total=False):
    user_id: str
    episode_id: str
    audio_path: str
    job_id: str
    transcript: dict[str, Any]
    transcript_text: str
    creator_profile: dict[str, Any] | None
    historical_examples: list[dict[str, Any]]
    episode_metadata: dict[str, Any]
    selected_moments: list[dict[str, Any]]
    clips: list[dict[str, Any]]
    chapters: list[dict[str, Any]]
    episode_summary: str
    social_posts: dict[str, str]
    personalization_sources: list[str]
    errors: list[str]


def format_transcript(transcript: dict[str, Any]) -> str:
    segments = transcript.get("segments", [])
    lines = []
    for segment in segments:
        text = str(segment.get("text", "")).strip()
        if text:
            lines.append(f"[{float(segment.get('start', 0)):.1f}s - {float(segment.get('end', 0)):.1f}s] {segment.get('speaker', 'Speaker')}: {text}")
    return "\n".join(lines)


async def transcribe_node(state: PodcastState) -> dict:
    settings = get_settings()
    if not settings.whipscribe_api_key:
        return {"errors": ["WhipScribe is not configured on the backend."]}
    try:
        client = WhipScribeClient(settings.whipscribe_api_key)
        job_id = await client.upload_file(state["audio_path"])
        job_info = await client.poll_job(job_id)
        if job_info.get("status") == "failed":
            return {"errors": [f"Transcription failed: {job_info.get('error', 'Unknown error')}"]}
        transcript = await client.get_transcript(job_id)
        return {"job_id": job_id, "transcript": transcript, "transcript_text": format_transcript(transcript)}
    except Exception as exc:
        return {"errors": [f"Transcription error: {exc}"]}


async def find_moments_node(state: PodcastState) -> dict:
    if state.get("errors"):
        return {}
    prompt = build_moment_selection_prompt(state.get("creator_profile"), state.get("historical_examples"), state.get("episode_metadata"))
    chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | JsonOutputParser()
    try:
        selected = await chain.ainvoke({"transcript_text": state.get("transcript_text", "")[:10000], "num_clips": 3})
        return {"selected_moments": selected}
    except Exception as exc:
        return {"errors": [f"Moment selection failed: {exc}"]}


async def render_clips_node(state: PodcastState) -> dict:
    if state.get("errors"):
        return {}
    settings = get_settings()
    client = WhipScribeClient(settings.whipscribe_api_key or "")
    clips = []
    for moment in state.get("selected_moments", []):
        try:
            clip_id = await client.create_clip(state["job_id"], float(moment["start_s"]), float(moment["end_s"]), str(moment.get("title", "Clip"))[:120])
            clip_info = await client.poll_clip(clip_id)
            if clip_info.get("status") == "done":
                clips.append({**moment, "clip_id": clip_id, "video_url": clip_info.get("video_url")})
        except Exception as exc:
            clips.append({**moment, "video_url": None, "error": f"Clip render failed: {exc}"})
    return {"clips": clips}


async def generate_show_notes_node(state: PodcastState) -> dict:
    if state.get("errors"):
        return {}
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    prompt = build_show_notes_prompt(state.get("creator_profile"), state.get("historical_examples"), state.get("episode_metadata"))
    try:
        notes = await (prompt | llm | JsonOutputParser()).ainvoke({"transcript_text": state.get("transcript_text", "")[:10000]})
    except Exception:
        notes = {"summary": "", "chapters": [], "key_takeaways": []}
    return {"episode_summary": notes.get("summary", ""), "chapters": notes.get("chapters", []), "key_takeaways": notes.get("key_takeaways", [])}


async def generate_social_node(state: PodcastState) -> dict:
    if state.get("errors"):
        return {}
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    posts = {}
    for platform in ["x", "linkedin", "instagram"]:
        prompt = build_social_prompt(state.get("creator_profile"), state.get("historical_examples"), state.get("episode_metadata"), platform)
        posts[platform] = await (prompt | llm | StrOutputParser()).ainvoke(
            {
                "show_notes": state.get("episode_summary", ""),
                "transcript_text": state.get("transcript_text", "")[:5000],
            }
        )
    return {"social_posts": posts}


async def finalize_node(state: PodcastState) -> dict:
    sources = ["Creator profile", "Episode metadata"]
    if state.get("historical_examples"):
        sources.append(f"{len(state['historical_examples'])} previous examples")
    return {"personalization_sources": sources}


def create_workflow():
    workflow = StateGraph(PodcastState)
    workflow.add_node("transcribe", transcribe_node)
    workflow.add_node("find_moments", find_moments_node)
    workflow.add_node("render_clips", render_clips_node)
    workflow.add_node("generate_show_notes", generate_show_notes_node)
    workflow.add_node("generate_social_content", generate_social_node)
    workflow.add_node("finalize", finalize_node)
    workflow.add_edge(START, "transcribe")
    workflow.add_edge("transcribe", "find_moments")
    workflow.add_edge("find_moments", "render_clips")
    workflow.add_edge("render_clips", "generate_show_notes")
    workflow.add_edge("generate_show_notes", "generate_social_content")
    workflow.add_edge("generate_social_content", "finalize")
    workflow.add_edge("finalize", END)
    return workflow.compile()
