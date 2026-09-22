from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.core.security import encrypt_secret
from app.db.session import get_db
from app.models import ConnectedAccount, User
from app.schemas.api import ConnectionIn, ConnectionOut

router = APIRouter(prefix="/connections", tags=["connections"])


@router.get("", response_model=list[ConnectionOut])
async def list_connections(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ConnectedAccount).where(ConnectedAccount.user_id == user.id))
    return result.scalars().all()


@router.post("", response_model=ConnectionOut)
async def connect(payload: ConnectionIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    row = ConnectedAccount(
        user_id=user.id,
        provider=payload.provider,
        account_name=payload.account_name,
        access_token_encrypted=encrypt_secret(payload.access_token) if payload.access_token else None,
        refresh_token_encrypted=encrypt_secret(payload.refresh_token) if payload.refresh_token else None,
        metadata_json=payload.metadata_json,
        scopes=payload.scopes,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.delete("/{connection_id}")
async def disconnect(connection_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(ConnectedAccount).where(ConnectedAccount.id == connection_id, ConnectedAccount.user_id == user.id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"ok": True}
