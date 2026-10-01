"""
MUSNAD AI - Health & System Status Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, check_db_health
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    db_ok = await check_db_health()
    return {
        "status": "healthy" if db_ok else "degraded",
        "app": "MUSNAD AI",
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "disconnected",
        "kb_version": settings.KB_VERSION,
        "demo_mode": settings.DEMO_MODE,
    }
