import json
import os
from typing import TypedDict, List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langgraph.graph import StateGraph, START, END

from .whipscribe_client import WhipScribeClient
from .prompts import RANK_MOMENTS_PROMPT, CHAPTERS_PROMPT, SUMMARY_PROMPT, SOCIAL_POSTS_PROMPT


class PodcastState(TypedDict):
    audio_path: str
    job_id: str
    transcript: Dict[str, Any]
    transcript_text: str
    selected_moments: List[Dict[str, Any]]
    clips: List[Dict[str, Any]]
    chapters: List[Dict[str, Any]]
    episode_summary: str
    social_posts: Dict[str, str]
    errors: List[str]


def format_transcript(transcript: Dict[str, Any]) -> str:
    """Format transcript segments into readable text with timestamps and speakers."""
    segments = transcript.get("segments", [])
    lines = []
    for seg in segments:
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        speaker = seg.get("speaker", "Unknown")
        text = seg.get("text", "").strip()
        if text:
            lines.append(f"[{start:.1f}s - {end:.1f}s] {speaker}: {text}")
    return "\n".join(lines)


async def transcribe_node(state: PodcastState) -> dict:
    """Upload audio and get the transcript."""
    client = WhipScribeClient(os.getenv("WHIPSCRIBE_API_KEY"))
    try:
        job_id = await client.upload_file(state["audio_path"])
        job_info = await client.poll_job(job_id)

        if job_info.get("status") == "failed":
            return {"errors": [f"Transcription failed: {job_info.get('error', 'Unknown error')}"]}

        transcript = await client.get_transcript(job_id)
        transcript_text = format_transcript(transcript)

        return {
            "job_id": job_id,
            "transcript": transcript,
            "transcript_text": transcript_text,
        }
    except Exception as e:
        return {"errors": [f"Transcription error: {e}"]}


async def find_moments_node(state: PodcastState) -> dict:
    """Use GPT to analyze the transcript and pick the best clip-worthy moments."""
    if state.get("errors"):
        return {}

    transcript_text = state.get("transcript_text", "")
    if not transcript_text:
        return {"errors": ["No transcript text available."]}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()
    chain = RANK_MOMENTS_PROMPT | llm | parser

    try:
        # Limit transcript to ~8000 chars to stay within token limits
        trimmed = transcript_text[:8000]
        selected = await chain.ainvoke({
            "transcript_text": trimmed,
            "num_clips": 3,
        })
        return {"selected_moments": selected}
    except Exception as e:
        return {"errors": [f"Moment ranking failed: {e}"]}


async def render_clips_node(state: PodcastState) -> dict:
    """Render 9:16 vertical MP4 clips via the WhipScribe Clips API."""
    if state.get("errors"):
        return {}

    client = WhipScribeClient(os.getenv("WHIPSCRIBE_API_KEY"))
    job_id = state["job_id"]
    selected = state.get("selected_moments", [])
    clips = []

    for moment in selected:
        try:
            clip_id = await client.create_clip(
                job_id=job_id,
                start_s=float(moment["start_s"]),
                end_s=float(moment["end_s"]),
                title=str(moment.get("title", "Clip"))[:120],
                caption_style="bold-yellow",
            )
            clip_info = await client.poll_clip(clip_id)
            if clip_info.get("status") == "done":
                moment["video_url"] = clip_info.get("video_url", "")
                moment["clip_id"] = clip_id
                clips.append(moment)
            else:
                print(f"Clip rendering failed for moment: {moment.get('title')}")
        except Exception as e:
            # Log but don't crash — continue rendering other clips
            print(f"Error rendering clip '{moment.get('title', '?')}': {e}")

    return {"clips": clips}


async def generate_show_notes_node(state: PodcastState) -> dict:
    """Generate chapters, episode summary, and social media posts."""
    if state.get("errors"):
        return {}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    transcript_text = state.get("transcript_text", "")[:8000]

    # Chapters
    try:
        chapters_chain = CHAPTERS_PROMPT | llm | JsonOutputParser()
        chapters = await chapters_chain.ainvoke({"transcript_text": transcript_text})
    except Exception as e:
        print(f"Chapter generation failed: {e}")
        chapters = []

    # Episode Summary
    try:
        summary_chain = SUMMARY_PROMPT | llm | StrOutputParser()
        episode_summary = await summary_chain.ainvoke({"transcript_text": transcript_text})
    except Exception as e:
        print(f"Summary generation failed: {e}")
        episode_summary = ""

    # Social Posts
    try:
        social_chain = SOCIAL_POSTS_PROMPT | llm | JsonOutputParser()
        social_posts = await social_chain.ainvoke({
            "summary": episode_summary or "Podcast episode"
        })
    except Exception as e:
        print(f"Social post generation failed: {e}")
        social_posts = {}

    return {
        "chapters": chapters,
        "episode_summary": episode_summary,
        "social_posts": social_posts,
    }


async def publish_results_node(state: PodcastState) -> dict:
    """Push results to Notion and send a Slack notification."""
    if state.get("errors"):
        return {}

    from .notion_client import NotionClient
    from .slack_client import SlackClient

    title = os.path.basename(state.get("audio_path", "Podcast Episode"))
    summary = state.get("episode_summary", "")
    chapters = state.get("chapters", [])
    social_posts = state.get("social_posts", {})
    clips = state.get("clips", [])

    # 1. Push to Notion
    notion = NotionClient()
    notion_msg = notion.push_episode(title, summary, chapters, social_posts, clips)
    print(notion_msg)

    # 2. Send Slack notification
    slack = SlackClient()
    slack_msg = slack.send_notification(title, summary, clips, social_posts)
    print(slack_msg)

    return {}


def create_workflow():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(PodcastState)

    workflow.add_node("transcribe", transcribe_node)
    workflow.add_node("find_moments", find_moments_node)
    workflow.add_node("render_clips", render_clips_node)
    workflow.add_node("generate_show_notes", generate_show_notes_node)
    workflow.add_node("publish_results", publish_results_node)

    # Sequential pipeline
    workflow.add_edge(START, "transcribe")
    workflow.add_edge("transcribe", "find_moments")
    workflow.add_edge("find_moments", "render_clips")
    workflow.add_edge("render_clips", "generate_show_notes")
    workflow.add_edge("generate_show_notes", "publish_results")
    workflow.add_edge("publish_results", END)

    return workflow.compile()
