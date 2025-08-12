# api/handlers/logic_runner.py

import asyncio
import json
from typing import Any, Dict, List, Union

from fastapi.responses import Response, StreamingResponse
from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call import (
    Function as ToolCallFunction,
)
from toolkit.tools.get_weather_tool import GetWeatherTool
from toolkit.tools.tool_types import ToolProtocol
from toolkit.utils.multi_tool_call_parts import MultiToolCallParts
from toolkit.utils.tool_registry import ToolRegistry
from toolkit.utils.tool_response_builder import build_tool_response_messages_multi


async def run_tool_logic(
    base_url: str,
    model_name: str,
    stream: bool,
    max_tokens: int,
    temperature: float,
) -> Union[Dict[str, Any], Response]:
    client = AsyncOpenAI(base_url=base_url, api_key="dummy")

    tool_instances: List[ToolProtocol] = [GetWeatherTool()]
    registry = ToolRegistry(tool_instances)
    tools = registry.all_specs()

    system_msg: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": registry.concat_tool_system_prompt(),
    }

    user_msg: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": registry.concat_user_prompt(),
    }

    if stream:

        async def event_stream():
            try:
                multi_tool_call_parts = MultiToolCallParts()

                stream_resp = await client.chat.completions.create(
                    model=model_name,
                    messages=[system_msg, user_msg],
                    tools=tools,
                    tool_choice="auto",
                    temperature=0,
                    stream=True,
                    max_tokens=max_tokens,
                    extra_body={"options": {"num_predict": max_tokens}},
                )

                async for chunk in stream_resp:
                    multi_tool_call_parts.add_chunk(chunk)
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"

                tool_calls = multi_tool_call_parts.to_message_tool_calls()
                tool_call_map = multi_tool_call_parts.to_message_tool_call_map()

                validation = registry.validate_all_tool_calls(tool_call_map)
                if not all(result["valid"] for result in validation.values()):
                    yield f"event: error\ndata: {json.dumps({'error': 'validation failed', 'details': validation})}\n\n"
                    return

                tool_results = registry.execute_all_tool_calls(tool_call_map)

                followup_messages = build_tool_response_messages_multi(
                    system_msg, user_msg, tool_calls, tool_results
                )

                second_stream = await client.chat.completions.create(
                    model=model_name,
                    messages=followup_messages,
                    temperature=temperature,
                    stream=True,
                    max_tokens=max_tokens,
                    extra_body={"options": {"num_predict": max_tokens}},
                )

                async for chunk in second_stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield f"data: {json.dumps({'content': delta.content})}\n\n"

                yield "event: done\ndata: {}\n\n"

            except asyncio.CancelledError:
                yield "event: cancel\ndata: {}\n\n"
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # ---------- Non-Streaming Mode ----------
    try:
        resp = await client.chat.completions.create(
            model=model_name,
            messages=[system_msg, user_msg],
            tools=tools,
            tool_choice="auto",
            temperature=0,
            stream=False,
            max_tokens=max_tokens,
            extra_body={"options": {"num_predict": max_tokens}},
        )

        tool_calls = resp.choices[0].message.tool_calls or []

        # --- Qwen-style fallback ---
        if not tool_calls:
            content: str = getattr(resp.choices[0].message, "content", "")
            try:
                parsed: dict[str, Any] = json.loads(content)
                tool_calls = [
                    ChatCompletionMessageToolCall(
                        id="tool_0",
                        type="function",
                        function=ToolCallFunction(
                            name=parsed["name"],  # ✅ must be raw string
                            arguments=json.dumps(parsed["arguments"]),  # ✅ still serialized
                        ),
                    )
                ]
            except json.JSONDecodeError:
                pass  # ignore

        if not tool_calls:
            return {
                "final_response": "",
                "tool_results": {},
                "validation": {"__global__": {"valid": False, "reason": "No tool calls returned"}},
            }

        tool_call_map = MultiToolCallParts.from_completed(tool_calls)
        validation = registry.validate_all_tool_calls(tool_call_map)
        if not all(result["valid"] for result in validation.values()):
            return {
                "final_response": "",
                "tool_results": {},
                "validation": {
                    "__global__": {
                        "valid": False,
                        "reason": "One or more tool calls failed validation",
                    },
                    **validation,
                },
            }

        tool_results = registry.execute_all_tool_calls(tool_call_map)

        followup_messages = build_tool_response_messages_multi(
            system_msg, user_msg, tool_calls, tool_results
        )

        second_resp = await client.chat.completions.create(
            model=model_name,
            messages=followup_messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
            stream=False,
            max_tokens=max_tokens,
            extra_body={"options": {"num_predict": max_tokens}},
        )

        return {
            "final_response": second_resp.choices[0].message.content or "",
            "tool_results": tool_results,
            "validation": validation,
        }

    except Exception as e:
        return {
            "final_response": "",
            "tool_results": {},
            "validation": {"error": str(e)},
        }
