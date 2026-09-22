from pathlib import Path


def test_episode_queries_are_user_scoped():
    source = Path("app/api/episodes.py").read_text()
    assert "episode.user_id != user.id" in source
    assert "Clip.user_id == user.id" in source
    assert "SocialPost.user_id == user.id" in source


def test_connections_do_not_return_tokens():
    source = Path("app/schemas/api.py").read_text()
    connection_out = source.split("class ConnectionOut", 1)[1]
    assert "access_token" not in connection_out
    assert "refresh_token" not in connection_out
