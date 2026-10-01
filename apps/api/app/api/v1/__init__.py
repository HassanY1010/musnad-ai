"""
MUSNAD AI - API v1 Router
Combines all v1 endpoint routers.
"""
from fastapi import APIRouter
from app.api.v1.endpoints.analyses import router as analyses_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.sources import router as sources_router
from app.api.v1.endpoints.auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(analyses_router)
api_router.include_router(sources_router)
api_router.include_router(auth_router)
