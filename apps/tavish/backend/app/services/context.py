from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ContentExample, CreatorProfile


async def load_creator_context(db: AsyncSession, user_id: str, platforms: list[str] | None = None) -> tuple[dict | None, list[dict]]:
    profile_result = await db.execute(select(CreatorProfile).where(CreatorProfile.user_id == user_id))
    profile = profile_result.scalar_one_or_none()
    profile_dict = {column.name: getattr(profile, column.name) for column in CreatorProfile.__table__.columns} if profile else None

    query = select(ContentExample).where(ContentExample.user_id == user_id).order_by(ContentExample.created_at.desc()).limit(5)
    if platforms:
        query = select(ContentExample).where(ContentExample.user_id == user_id, ContentExample.platform.in_(platforms)).order_by(ContentExample.created_at.desc()).limit(5)
    examples_result = await db.execute(query)
    examples = [
        {column.name: getattr(row, column.name) for column in ContentExample.__table__.columns}
        for row in examples_result.scalars().all()
    ]
    return profile_dict, examples
