from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr


class CreatorProfileIn(BaseModel):
    podcast_name: str
    description: str = ""
    niche: str = ""
    target_audience: str = ""
    audience_level: str = ""
    brand_voice: str = ""
    tone: str = ""
    communication_style: str = ""
    content_goals: str = ""
    preferred_platforms: list[str] = []
    clip_style: str = ""
    preferred_topics: list[str] = []
    excluded_topics: list[str] = []
    cta_style: str = ""
    language: str = "English"
    website: str | None = None
    social_handles: dict = {}
    brand_guidelines: str = ""


class CreatorProfileOut(CreatorProfileIn):
    id: str
    user_id: str

    class Config:
        from_attributes = True


class ContentExampleIn(BaseModel):
    platform: str
    title: str
    content: str
    source: str = "manual"


class ContentExampleOut(ContentExampleIn):
    id: str

    class Config:
        from_attributes = True


class EpisodeCreate(BaseModel):
    title: str | None = None
    description: str | None = None
    guest: str | None = None
    topic: str | None = None
    additional_instructions: str | None = None
    clip_goal: str = "Balanced"
    social_goal: str = "Engagement"


class EpisodeOut(BaseModel):
    id: str
    file_name: str
    file_type: str
    status: str
    title: str | None = None
    description: str | None = None
    clip_goal: str
    social_goal: str

    class Config:
        from_attributes = True


class JobOut(BaseModel):
    id: str
    episode_id: str
    current_step: str
    progress: int
    error_message: str | None = None

    class Config:
        from_attributes = True


class SocialPostUpdate(BaseModel):
    content: str


class ConnectionIn(BaseModel):
    provider: str
    account_name: str
    access_token: str | None = None
    refresh_token: str | None = None
    metadata_json: dict = {}
    scopes: list[str] = []


class ConnectionOut(BaseModel):
    id: str
    provider: str
    account_name: str
    metadata_json: dict
    scopes: list[str]
    status: str

    class Config:
        from_attributes = True
