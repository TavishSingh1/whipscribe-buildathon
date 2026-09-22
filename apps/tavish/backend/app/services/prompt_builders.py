from langchain_core.prompts import ChatPromptTemplate


def _profile_block(profile: dict | None) -> str:
    if not profile:
        return "No creator profile supplied. Use neutral, useful podcast defaults."
    return "\n".join(
        [
            f"Podcast: {profile.get('podcast_name', '')}",
            f"Description: {profile.get('description', '')}",
            f"Niche: {profile.get('niche', '')}",
            f"Audience: {profile.get('target_audience', '')}",
            f"Audience level: {profile.get('audience_level', '')}",
            f"Brand voice: {profile.get('brand_voice', '')}",
            f"Tone: {profile.get('tone', '')}",
            f"Communication style: {profile.get('communication_style', '')}",
            f"Goals: {profile.get('content_goals', '')}",
            f"Clip style: {profile.get('clip_style', '')}",
            f"Preferred topics: {', '.join(profile.get('preferred_topics') or [])}",
            f"Topics to avoid: {', '.join(profile.get('excluded_topics') or [])}",
            f"CTA style: {profile.get('cta_style', '')}",
            f"Language: {profile.get('language', 'English')}",
            f"Brand guidelines: {profile.get('brand_guidelines', '')[:1200]}",
        ]
    )


def _examples_block(examples: list[dict] | None) -> str:
    if not examples:
        return "No historical writing examples supplied."
    lines = []
    for example in examples[:5]:
        lines.append(f"{example.get('platform', 'unknown')} - {example.get('title', 'Untitled')}:\n{example.get('content', '')[:900]}")
    return "\n\n".join(lines)


def build_moment_selection_prompt(profile: dict | None, examples: list[dict] | None, episode: dict | None) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a senior podcast producer. Select clips that fit this specific creator, audience, and goal.
Prioritize current episode substance first, then episode instructions, then creator profile, then historical style examples.
Avoid excluded topics. Do not optimize for generic virality when the profile calls for education, thought leadership, or trust.""",
            ),
            (
                "user",
                """Creator profile:
{profile}

Historical style/context:
{examples}

Episode metadata and overrides:
{episode}

Transcript:
{transcript_text}

Return ONLY valid JSON: a list of {num_clips} objects with start_s, end_s, title, why, and score.
Each clip must be 15-60 seconds and must explain why it fits this creator's goals.""",
            ),
        ]
    ).partial(profile=_profile_block(profile), examples=_examples_block(examples), episode=str(episode or {}))


def build_show_notes_prompt(profile: dict | None, examples: list[dict] | None, episode: dict | None) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You write podcast show notes in the creator's own positioning, tone, and audience language."),
            (
                "user",
                """Creator profile:
{profile}

Relevant previous examples:
{examples}

Episode metadata:
{episode}

Transcript:
{transcript_text}

Return ONLY valid JSON with keys summary, key_takeaways, chapters.
chapters must be a list of objects with timestamp_s, title, summary.""",
            ),
        ]
    ).partial(profile=_profile_block(profile), examples=_examples_block(examples), episode=str(episode or {}))


def build_social_prompt(profile: dict | None, examples: list[dict] | None, episode: dict | None, platform: str) -> ChatPromptTemplate:
    platform_rules = {
        "x": "Concise, sharp, skimmable. Stay under 280 characters unless a thread is clearly requested.",
        "linkedin": "Professional, story-driven, useful for the target audience. Use short paragraphs.",
        "instagram": "Caption-first, emotionally accessible, with tasteful hashtags only when helpful.",
    }
    return ChatPromptTemplate.from_messages(
        [
            ("system", f"You create {platform} content. {platform_rules.get(platform, '')} Match the creator profile and historical style."),
            (
                "user",
                """Creator profile:
{profile}

Historical examples:
{examples}

Episode metadata:
{episode}

Show notes:
{show_notes}

Transcript excerpt:
{transcript_text}

Return plain text only. Include a call to action that fits the creator's CTA preference.""",
            ),
        ]
    ).partial(profile=_profile_block(profile), examples=_examples_block(examples), episode=str(episode or {}))
