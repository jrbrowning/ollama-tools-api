# utils/tool_call_router.py

from typing import Dict, List, Optional

from openai.types.chat import ChatCompletionMessageToolCall


class ToolCallRouter:
    def __init__(self) -> None:
        self.tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None

    def set_tool_calls(self, tool_calls: List[ChatCompletionMessageToolCall]) -> None:
        self.tool_calls = tool_calls

    def to_name_map(self) -> Dict[str, ChatCompletionMessageToolCall]:
        if not self.tool_calls:
            raise ValueError("Tool calls not set")
        return {call.function.name: call for call in self.tool_calls}

    def __getitem__(self, tool_name: str) -> ChatCompletionMessageToolCall:
        return self.to_name_map()[tool_name]

    def __iter__(self):
        if not self.tool_calls:
            return iter([])
        return iter(self.tool_calls)
