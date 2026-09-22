from abc import ABC, abstractmethod


class BaseIntegration(ABC):
    provider: str

    def __init__(self, user_id: str, metadata: dict | None = None):
        self.user_id = user_id
        self.metadata = metadata or {}

    async def get_user_context(self) -> list[dict]:
        return []

    @abstractmethod
    async def publish(self, payload: dict) -> dict:
        raise NotImplementedError


class NotionIntegration(BaseIntegration):
    provider = "notion"

    async def publish(self, payload: dict) -> dict:
        return {"status": "preview_only", "message": "OAuth publishing adapter is ready for token-backed implementation."}


class SlackIntegration(BaseIntegration):
    provider = "slack"

    async def publish(self, payload: dict) -> dict:
        return {"status": "preview_only", "message": "Slack publishing requires explicit user confirmation."}


def integration_for(provider: str, user_id: str, metadata: dict | None = None) -> BaseIntegration:
    if provider == "notion":
        return NotionIntegration(user_id, metadata)
    if provider == "slack":
        return SlackIntegration(user_id, metadata)
    raise ValueError(f"Unsupported provider: {provider}")
