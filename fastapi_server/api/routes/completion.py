# File: api/routes/completion.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from models.llm_request import LLMRequest

from api.config.model_routes import model_map, model_service_map, protocol_map
from api.dispatch.chat_completion import dispatch_chat_completion

router = APIRouter(prefix="/completion/v1")


@router.post("/chat", response_model=None)
async def chat_completion_handler(payload: LLMRequest) -> Response:
    model_id = payload.model_container

    if model_id not in model_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {model_id}. Available models: {list(model_map.keys())}",
        )

    model_name = model_map[model_id]
    base_url = model_service_map.get(model_id)
    protocol = protocol_map.get(model_id, "")

    if not model_name:
        raise HTTPException(
            status_code=400,
            detail=f"Model {model_id} is not configured. Check environment variables.",
        )

    if not base_url:
        raise HTTPException(
            status_code=400,
            detail=f"No service configured for model: {model_id}",
        )

    return await dispatch_chat_completion(
        payload=payload,
        model_name=model_name,
        base_url=f"{base_url}/v1",
        protocol=protocol,
    )
