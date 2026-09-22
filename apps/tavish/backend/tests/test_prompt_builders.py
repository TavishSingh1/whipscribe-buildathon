from app.services.prompt_builders import build_moment_selection_prompt, build_social_prompt


def test_creator_profile_is_injected_into_moment_prompt():
    prompt = build_moment_selection_prompt(
        {"podcast_name": "The Startup Grind", "target_audience": "early-stage founders", "content_goals": "grow LinkedIn", "excluded_topics": ["clickbait"]},
        [{"platform": "linkedin", "title": "Past post", "content": "Practical, blunt founder advice."}],
        {"additional_instructions": "Prioritize clips about AI agents."},
    )
    rendered = prompt.format(transcript_text="Founder lesson at 12 seconds", num_clips=3)
    assert "The Startup Grind" in rendered
    assert "early-stage founders" in rendered
    assert "AI agents" in rendered
    assert "clickbait" in rendered


def test_platform_specific_social_prompt_rules_differ():
    x_prompt = build_social_prompt({}, [], {}, "x").format(show_notes="notes", transcript_text="transcript")
    linkedin_prompt = build_social_prompt({}, [], {}, "linkedin").format(show_notes="notes", transcript_text="transcript")
    assert "under 280 characters" in x_prompt
    assert "story-driven" in linkedin_prompt
