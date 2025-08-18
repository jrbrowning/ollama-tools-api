# File: api/dispatch/toolchain_completion.py

from fastapi import HTTPException
from fastapi.responses import Response
from models.llm_request import LLMRequest

# from api.handlers.mcp.toolchain_completion import mcp_toolchain_completion_sync
from api.handlers.openai.toolchain_completion import openai_toolchain_completion_sync


async def dispatch_toolchain_completion(
    payload: LLMRequest,
    model_name: str,
    base_url: str,
    protocol: str,
) -> Response:
    if protocol == "openai":
        return await openai_toolchain_completion_sync(
            stage_id=payload.stage_id,
            base_url=base_url,
            model_name=model_name,
            user_prompt=payload.user_prompt,
            system_prompt=payload.system_prompt,
            max_tokens=payload.max_tokens,
            temperature=payload.temperature,
            synthesis=payload.synthesis,
        )

    # if protocol == "mcp":
    #     return await mcp_toolchain_completion_sync(
    #         stage_id=payload.stage_id,
    #         base_url=base_url,
    #         model_name=model_name,
    #         user_prompt=payload.user_prompt,
    #         system_prompt=payload.system_prompt,
    #         max_tokens=payload.max_tokens,
    #         temperature=payload.temperature,
    #         synthesis=payload.synthesis,
    #     )

    raise HTTPException(status_code=501, detail=f"Unsupported protocol: {protocol}")
