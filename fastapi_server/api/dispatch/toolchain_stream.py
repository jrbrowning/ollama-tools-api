# File: api/dispatch/toolchain_stream.py

from fastapi import HTTPException
from fastapi.responses import Response
from models.llm_request import LLMRequest

from api.handlers.openai.toolchain_stream import openai_toolchain_completion_stream

# from api.handlers.mcp.toolchain_stream import mcp_toolchain_completion_stream


async def dispatch_toolchain_stream(
    payload: LLMRequest,
    model_name: str,
    base_url: str,
    protocol: str,
) -> Response:
    if protocol == "openai":
        return await openai_toolchain_completion_stream(
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
    #     return await mcp_toolchain_completion_stream(
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
