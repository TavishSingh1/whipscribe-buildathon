from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_db
from app.models import CreatorProfile, User
from app.schemas.api import CreatorProfileIn, CreatorProfileOut

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=CreatorProfileOut | None)
async def get_profile(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CreatorProfile).where(CreatorProfile.user_id == user.id))
    return result.scalar_one_or_none()


@router.put("", response_model=CreatorProfileOut)
async def upsert_profile(payload: CreatorProfileIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CreatorProfile).where(CreatorProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if profile:
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)
    else:
        profile = CreatorProfile(user_id=user.id, **payload.model_dump())
        db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile
