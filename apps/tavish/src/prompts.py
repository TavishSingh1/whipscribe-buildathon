from langchain_core.prompts import ChatPromptTemplate

RANK_MOMENTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert podcast producer and social media manager. 
Your task is to analyze a podcast transcript and identify the top {num_clips} most viral-worthy, 
engaging moments to turn into short video clips (TikTok, Reels, Shorts).

Look for:
- Strong hooks or bold statements that grab attention
- Surprising facts or numbers  
- Emotionally charged or high-energy moments
- Thought-provoking questions
- Funny or relatable quotes

Each clip must be 15-60 seconds long."""),
    ("user", """Here is the full podcast transcript with timestamps and speaker labels:

{transcript_text}

Select the top {num_clips} moments. Return ONLY a valid JSON list (no markdown, no explanation) 
of objects, each containing:
- 'start_s': start time in seconds (number)
- 'end_s': end time in seconds (number, must be 15-60s after start_s)  
- 'title': a catchy title for the clip (string, max 120 chars)
- 'why': a brief explanation of why this clip would go viral (string)

Example format:
[{{"start_s": 45.2, "end_s": 78.5, "title": "The moment everything changed", "why": "Strong emotional hook"}}]""")
])

CHAPTERS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert podcast producer. Create YouTube-style chapter markers for this podcast episode."),
    ("user", """Transcript:
{transcript_text}

Create logical chapters. Return ONLY a valid JSON list (no markdown) of objects with:
- 'timestamp_s': number (seconds into the episode)
- 'title': string (chapter title)
- 'summary': string (1-sentence description)""")
])

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a professional podcast copywriter. Write a compelling, SEO-friendly summary for this episode."),
    ("user", """Transcript:
{transcript_text}

Write a 2-3 paragraph summary that hooks the listener and explains what they'll learn. 
Return plain text only, no JSON.""")
])

SOCIAL_POSTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a social media manager for a podcast. Write engaging promotional posts for the episode."),
    ("user", """Episode Summary:
{summary}

Create 3 posts. Return ONLY a valid JSON object (no markdown) with keys:
- 'twitter': short, punchy post for X/Twitter (max 280 chars)
- 'linkedin': professional, story-driven post for LinkedIn
- 'instagram': engaging caption for Instagram""")
])
