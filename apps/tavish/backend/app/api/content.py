from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ContentExample, User
from app.schemas.api import ContentExampleIn, ContentExampleOut

router = APIRouter(prefix="/content-examples", tags=["content examples"])


@router.get("", response_model=list[ContentExampleOut])
async def list_examples(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentExample).where(ContentExample.user_id == user.id).order_by(ContentExample.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=ContentExampleOut)
async def create_example(payload: ContentExampleIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    row = ContentExample(user_id=user.id, **payload.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
