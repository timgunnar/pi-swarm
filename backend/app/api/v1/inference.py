import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.k8s.client import K8sClient
from app.schemas.inference import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ModelDeployRequest,
    ModelDeployResponse,
)
from app.services.inference_service import InferenceService

router = APIRouter(prefix="/inference", tags=["inference"])


def get_inference_service() -> InferenceService:
    return InferenceService(K8sClient())


@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completion(req: ChatRequest, service: InferenceService = Depends(get_inference_service)):
    if req.stream:
        async def stream():
            async for token in service.chat_stream(
                req.model, [m.model_dump() for m in req.messages],
                temperature=req.temperature, top_p=req.top_p, num_predict=req.max_tokens,
            ):
                chunk = {"choices": [{"delta": {"content": token}, "index": 0}]}
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(stream(), media_type="text/event-stream")

    try:
        result = await service.chat(
            req.model, [m.model_dump() for m in req.messages],
            temperature=req.temperature, top_p=req.top_p, num_predict=req.max_tokens,
        )
        return ChatResponse(
            model=result["model"],
            message=ChatMessage(
                role=result["message"].get("role", "assistant"),
                content=result["message"].get("content", ""),
            ),
            total_duration=result.get("total_duration", 0),
            eval_count=result.get("eval_count", 0),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_inference_models(service: InferenceService = Depends(get_inference_service)):
    return await service.list_models()


@router.post("/models/deploy", response_model=ModelDeployResponse)
async def deploy_model(req: ModelDeployRequest, service: InferenceService = Depends(get_inference_service)):
    result = await service.deploy_model(req.name, req.node_names or None)
    return ModelDeployResponse(**result)
