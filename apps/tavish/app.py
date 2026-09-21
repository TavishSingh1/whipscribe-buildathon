import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

from src.graph import create_workflow

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Podcast Clip Factory", page_icon="🎙️", layout="wide")

st.title("🎙️ Podcast Clip Factory")
st.markdown("""
Upload your podcast episode. We'll transcribe it, find the best viral moments, 
render vertical MP4 shorts with captions, and generate your show notes & social media posts — 
then push everything to **Notion** and **Slack** automatically.
""")

# API Key Warning
missing_keys = []
if not os.getenv("WHIPSCRIBE_API_KEY"):
    missing_keys.append("WHIPSCRIBE_API_KEY")
if not os.getenv("OPENAI_API_KEY"):
    missing_keys.append("OPENAI_API_KEY")

if missing_keys:
    st.error(f"⚠️ Missing required API keys: {', '.join(missing_keys)}. Please set them in your `.env` file.")
    st.stop()

# Optional integrations status
col1, col2 = st.columns(2)
with col1:
    if os.getenv("NOTION_API_KEY"):
        st.success("✅ Notion connected")
    else:
        st.info("ℹ️ Notion not configured (optional)")
with col2:
    if os.getenv("SLACK_WEBHOOK_URL"):
        st.success("✅ Slack connected")
    else:
        st.info("ℹ️ Slack not configured (optional)")

st.divider()

uploaded_file = st.file_uploader("Upload Podcast Audio", type=["mp3", "wav", "m4a", "mp4", "ogg", "webm", "flac"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    # Save uploaded file temporarily
    temp_dir = "output"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_file.name)

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Generate Clips & Show Notes", type="primary"):

        async def run_workflow():
            workflow = create_workflow()
            initial_state = {"audio_path": temp_path, "errors": []}

            with st.status("Processing Podcast...", expanded=True) as status:
                final_state = {}
                async for output in workflow.astream(initial_state):
                    for node_name, node_state in output.items():
                        if node_name == "transcribe":
                            if node_state.get("errors"):
                                st.error(f"❌ {node_state['errors'][-1]}")
                            else:
                                st.write(f"✅ Transcription complete! Job ID: `{node_state.get('job_id')}`")
                        elif node_name == "find_moments":
                            moments = node_state.get("selected_moments", [])
                            st.write(f"🧠 Found {len(moments)} high-signal moments to render.")
                        elif node_name == "render_clips":
                            clips = node_state.get("clips", [])
                            st.write(f"🎬 Rendered {len(clips)} vertical MP4 clips!")
                        elif node_name == "generate_show_notes":
                            st.write("📝 Generated show notes & social posts.")
                        elif node_name == "publish_results":
                            if os.getenv("NOTION_API_KEY"):
                                st.write("✅ Pushed content to Notion episode database!")
                            if os.getenv("SLACK_WEBHOOK_URL"):
                                st.write("🔔 Sent instant review notification to Slack!")
                        final_state.update(node_state)
                status.update(label="✅ Processing Complete!", state="complete", expanded=True)
            return final_state

        final_state = asyncio.run(run_workflow())

        if final_state.get("errors"):
            for err in final_state["errors"]:
                st.error(err)

        # Display Results in Tabs
        tab1, tab2, tab3 = st.tabs(["🎬 Vertical Clips", "📝 Show Notes", "📱 Social Posts"])

        with tab1:
            st.subheader("Your Viral Shorts")
            clips = final_state.get("clips", [])
            if not clips:
                st.warning("No clips were rendered. The Clips API may require uploaded files (not URLs).")
            else:
                for i, clip in enumerate(clips):
                    st.markdown(f"### {i+1}. {clip.get('title', 'Clip')}")
                    video_url = clip.get("video_url")
                    if video_url:
                        st.video(video_url)
                        st.link_button("⬇️ Download MP4", video_url)
                    st.caption(f"**Why this works:** {clip.get('why', '')}")
                    st.caption(f"Timestamp: {clip.get('start_s', 0):.1f}s – {clip.get('end_s', 0):.1f}s")
                    st.divider()

        with tab2:
            st.subheader("Episode Summary")
            st.write(final_state.get("episode_summary", "N/A"))

            st.subheader("Chapters")
            chapters = final_state.get("chapters", [])
            if chapters:
                for chapter in chapters:
                    ts = chapter.get("timestamp_s", 0)
                    mins, secs = divmod(int(ts), 60)
                    st.markdown(f"**{mins:02d}:{secs:02d}** — {chapter.get('title', '')}")
                    st.write(chapter.get("summary", ""))
            else:
                st.info("No chapters generated.")

        with tab3:
            social = final_state.get("social_posts", {})
            if social:
                st.subheader("🐦 Twitter / X")
                st.code(social.get("twitter", "N/A"), language="markdown")

                st.subheader("💼 LinkedIn")
                st.code(social.get("linkedin", "N/A"), language="markdown")

                st.subheader("📸 Instagram")
                st.code(social.get("instagram", "N/A"), language="markdown")
            else:
                st.info("No social posts generated.")
