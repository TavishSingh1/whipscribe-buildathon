from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, connections, content, episodes, profiles
from app.core.config import get_settings
from app.db.session import engine
from app.models import Base

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"ok": True, "environment": settings.environment}


app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(content.router)
app.include_router(connections.router)
app.include_router(episodes.router)
