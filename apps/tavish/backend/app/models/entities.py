from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class CreatorProfile(IdMixin, TimestampMixin, Base):
    __tablename__ = "creator_profiles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    podcast_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    niche: Mapped[str] = mapped_column(String(160), default="")
    target_audience: Mapped[str] = mapped_column(Text, default="")
    audience_level: Mapped[str] = mapped_column(String(120), default="")
    brand_voice: Mapped[str] = mapped_column(Text, default="")
    tone: Mapped[str] = mapped_column(String(160), default="")
    communication_style: Mapped[str] = mapped_column(Text, default="")
    content_goals: Mapped[str] = mapped_column(Text, default="")
    preferred_platforms: Mapped[list] = mapped_column(JSON, default=list)
    clip_style: Mapped[str] = mapped_column(String(160), default="")
    preferred_topics: Mapped[list] = mapped_column(JSON, default=list)
    excluded_topics: Mapped[list] = mapped_column(JSON, default=list)
    cta_style: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(80), default="English")
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    social_handles: Mapped[dict] = mapped_column(JSON, default=dict)
    brand_guidelines: Mapped[str] = mapped_column(Text, default="")


class ContentExample(IdMixin, TimestampMixin, Base):
    __tablename__ = "content_examples"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    platform: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(240))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(80), default="manual")


class ConnectedAccount(IdMixin, TimestampMixin, Base):
    __tablename__ = "connected_accounts"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    account_name: Mapped[str] = mapped_column(String(200))
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(40), default="connected")


class Episode(IdMixin, TimestampMixin, Base):
    __tablename__ = "episodes"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(120))
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    storage_url: Mapped[str] = mapped_column(String(800))
    status: Mapped[str] = mapped_column(String(40), default="uploaded", index=True)
    transcript: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    guest: Mapped[str | None] = mapped_column(String(200), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(240), nullable=True)
    additional_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    clip_goal: Mapped[str] = mapped_column(String(80), default="Balanced")
    social_goal: Mapped[str] = mapped_column(String(80), default="Engagement")
    jobs: Mapped[list["ProcessingJob"]] = relationship(back_populates="episode")


class ProcessingJob(IdMixin, TimestampMixin, Base):
    __tablename__ = "processing_jobs"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    current_step: Mapped[str] = mapped_column(String(80), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    episode: Mapped[Episode] = relationship(back_populates="jobs")


class Clip(IdMixin, TimestampMixin, Base):
    __tablename__ = "clips"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    video_url: Mapped[str | None] = mapped_column(String(800), nullable=True)
    score_reason: Mapped[str] = mapped_column(Text, default="")


class ShowNotes(IdMixin, TimestampMixin, Base):
    __tablename__ = "show_notes"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    summary: Mapped[str] = mapped_column(Text)
    chapters: Mapped[list] = mapped_column(JSON, default=list)


class SocialPost(IdMixin, TimestampMixin, Base):
    __tablename__ = "social_posts"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    platform: Mapped[str] = mapped_column(String(80), index=True)
    content: Mapped[str] = mapped_column(Text)


class UsageRecord(IdMixin, TimestampMixin, Base):
    __tablename__ = "usage_records"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    episode_id: Mapped[str | None] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    processing_minutes: Mapped[float] = mapped_column(Float, default=0)
    llm_tokens_estimated: Mapped[int] = mapped_column(Integer, default=0)
    clips_generated: Mapped[int] = mapped_column(Integer, default=0)
