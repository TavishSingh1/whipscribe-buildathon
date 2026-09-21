# Podcast Clip Factory (Track 4 + Track 3)

## The Problem

**The Person:** An independent podcaster who publishes weekly, has 500–5,000 listeners, and does everything themselves. They record, edit, write show notes, clip highlights, caption them, and post to 3 platforms.
**What they do today:** The clipping alone takes 2–3 hours because they re-listen to the entire episode hunting for the best 30-second moments, manually edit them, and add captions.
**What it costs them:** 5 hours of post-production per episode, burnout, and delayed publishing.
**The result they want:** Automatic discovery of viral moments, rendered as vertical short clips, plus generated show notes and social posts.
**Where the result should land:** A dashboard containing downloadable MP4 clips, and ready-to-copy markdown text.

## The Workflow

1. The podcaster uploads the episode audio file.
2. The WhipScribe API transcribes the audio and generates topics/summaries.
3. WhipScribe's Signal Classification API analyzes the transcript to find high-signal moments (hooks, questions, high energy).
4. A LangGraph workflow uses OpenAI to rank the moments and select the top 3.
5. WhipScribe's Clips API renders these moments into 9:16 vertical MP4s with captions.
6. The LLM simultaneously generates chapters, a summary, and social media posts.
7. Finally, all generated content (clips, show notes, and posts) is automatically synced to a **Notion Episode Database** as a rich document, and an instant review notification is sent to the team via **Slack**.

## How to Run

1. Copy `.env.example` to `.env` and fill in your `WHIPSCRIBE_API_KEY` and `OPENAI_API_KEY`.
2. Install dependencies: `pip install -r pyproject.toml` (or use `uv`, `poetry`, etc.)
3. Run the Streamlit app: `streamlit run app.py`

## Vision
In the future, this tool could ingest directly from RSS feeds, remember the brand's unique voice for social posts, and generate cross-episode highlight reels automatically.

