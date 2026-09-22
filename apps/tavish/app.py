import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from src.graph import create_workflow

load_dotenv()

st.set_page_config(page_title="Podcast Clip Factory", page_icon="🎙️", layout="wide")
st.title("🎙️ Podcast Clip Factory")
st.markdown(
    """
Upload your podcast episode. The legacy prototype transcribes it, finds high-signal moments,
renders vertical MP4 shorts with captions, and generates show notes and social posts.

Production Notion and Slack publishing now lives in the FastAPI app as user-scoped connections.
"""
)

missing_keys = []
if not os.getenv("WHIPSCRIBE_API_KEY"):
    missing_keys.append("WHIPSCRIBE_API_KEY")
if not os.getenv("OPENAI_API_KEY"):
    missing_keys.append("OPENAI_API_KEY")

if missing_keys:
    st.error(f"Missing required API keys: {', '.join(missing_keys)}. Please set them in your local `.env` file.")
    st.stop()

st.info("Legacy mode: optional publishing is disabled here. Use the production web app for user-scoped Notion and Slack connections.")
st.divider()

uploaded_file = st.file_uploader("Upload Podcast Audio", type=["mp3", "wav", "m4a", "mp4", "ogg", "webm", "flac"])

if uploaded_file is not None:
    st.audio(uploaded_file)
    temp_dir = "output"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_file.name)

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Generate Clips & Show Notes", type="primary"):

        async def run_workflow():
            workflow = create_workflow()
            initial_state = {"audio_path": temp_path, "errors": []}
            final_state = {}
            with st.status("Processing Podcast...", expanded=True) as status:
                async for output in workflow.astream(initial_state):
                    for node_name, node_state in output.items():
                        if node_name == "transcribe":
                            st.write("Transcription complete.")
                        elif node_name == "find_moments":
                            st.write(f"Found {len(node_state.get('selected_moments', []))} high-signal moments.")
                        elif node_name == "render_clips":
                            st.write(f"Rendered {len(node_state.get('clips', []))} clips.")
                        elif node_name == "generate_show_notes":
                            st.write("Generated show notes and social posts.")
                        final_state.update(node_state)
                status.update(label="Processing complete", state="complete", expanded=True)
            return final_state

        final_state = asyncio.run(run_workflow())

        for err in final_state.get("errors", []):
            st.error(err)

        tab1, tab2, tab3 = st.tabs(["Vertical Clips", "Show Notes", "Social Posts"])

        with tab1:
            for i, clip in enumerate(final_state.get("clips", []), start=1):
                st.markdown(f"### {i}. {clip.get('title', 'Clip')}")
                if clip.get("video_url"):
                    st.video(clip["video_url"])
                    st.link_button("Download MP4", clip["video_url"])
                st.caption(clip.get("why", ""))

        with tab2:
            st.subheader("Episode Summary")
            st.write(final_state.get("episode_summary", "N/A"))
            st.subheader("Chapters")
            for chapter in final_state.get("chapters", []):
                st.markdown(f"**{chapter.get('timestamp_s', 0)}s** - {chapter.get('title', '')}")
                st.write(chapter.get("summary", ""))

        with tab3:
            for platform, post in final_state.get("social_posts", {}).items():
                st.subheader(platform)
                st.code(post, language="markdown")
