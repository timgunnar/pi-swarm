from fastapi import APIRouter, Depends

from app.k8s.client import K8sClient
from app.schemas.model import ModelInfo
from app.services.model_service import ModelService

router = APIRouter(prefix="/models", tags=["models"])


def get_model_service() -> ModelService:
    return ModelService(K8sClient())


@router.get("", response_model=list[ModelInfo])
async def list_models(service: ModelService = Depends(get_model_service)):
    return await service.list_models()
