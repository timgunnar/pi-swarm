from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/info")
async def system_info():
    return {
        "app": settings.app_name,
        "version": "0.0.1",
        "api_versions": ["v1"],
    }


@router.get("/healthz")
async def healthz():
    return {"status": "healthy"}
