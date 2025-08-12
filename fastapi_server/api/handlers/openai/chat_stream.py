# File: api/handlers/openai/chat_stream.py

import asyncio
from typing import List, Union

from fastapi.responses import StreamingResponse
from models.events import (
    CancelPayload,
    ChatCompletionStreamPayload,
    DonePayload,
    ErrorPayload,
    serialize_sse_event,
)
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from api.handlers.openai.chat_common import (
    build_system_message,
    build_user_message,
    get_openai_client,
    get_token_settings,
)


async def _stream_chat_response(
    stage_id: str,
    client: AsyncOpenAI,
    messages: List[Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]],
    model_name: str,
    temperature: float,
    max_tokens: int,
):
    try:
        stream_resp = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            stream=True,
            max_tokens=max_tokens,
            extra_body={"options": {"num_predict": max_tokens}},
        )

        chunk_id = 0
        async for chunk in stream_resp:
            payload = ChatCompletionStreamPayload(stage_id=stage_id, chunk=chunk)
            yield serialize_sse_event(
                id=f"{stage_id}-chunk-{chunk_id}", event="chat_completion_chunk", data=payload
            )
            chunk_id += 1

        yield serialize_sse_event(
            id=str(chunk_id), event="done", data=DonePayload(stage_id=stage_id)
        )

    except asyncio.CancelledError:
        yield serialize_sse_event(id="0", event="cancel", data=CancelPayload(stage_id=stage_id))
    except Exception as e:
        yield serialize_sse_event(
            id="0", event="error", data=ErrorPayload(stage_id=stage_id, error=str(e))
        )


async def openai_chat_completion_stream(
    stage_id: str,
    base_url: str,
    model_name: str,
    user_prompt: str,
    system_prompt: str,
    max_tokens: list[int],
    temperature: list[float],
) -> StreamingResponse:
    client = get_openai_client(base_url)
    system = build_system_message(system_prompt)
    user = build_user_message(user_prompt)
    messages: List[Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]] = [
        system,
        user,
    ]
    max_tokens_val, temperature_val = get_token_settings(max_tokens, temperature)

    return StreamingResponse(
        _stream_chat_response(
            stage_id,
            client,
            messages,
            model_name,
            temperature_val,
            max_tokens_val,
        ),
        media_type="text/event-stream",
    )
