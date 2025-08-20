# toolkit/tools/advanced_math_tool.py

from typing import Literal

from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel, Field, ValidationError
from toolkit.tools.tool_types import ToolProtocol


class Operand(BaseModel):
    value: float = Field(..., description="The numeric value")


class AdvancedMathInput(BaseModel):
    operation: Literal["add", "subtract", "multiply", "divide", "power", "modulo"]
    a: float = Field(..., description="First numeric input")
    b: float = Field(..., description="Second numeric input")


class AdvancedMathTool(ToolProtocol):
    @property
    def name(self) -> str:
        return "advanced_math_operation"

    @property
    def description(self) -> str:
        return "Perform a binary math operation between two numeric inputs."

    def tool_spec(self) -> ChatCompletionToolParam:
        return ChatCompletionToolParam(
            type="function",
            function={
                "name": self.name,
                "description": self.description,
                "parameters": AdvancedMathInput.model_json_schema(),
            },
        )

    def tool_intent_prompt(self) -> str:
        return ""

    def tool_system_prompt(self) -> str:
        return (
            "You are a helpful assistant that can perform basic math operations. "
            "You will receive two numeric inputs and an operation to perform on them."
            "You must use `advanced_math_operation` tool to complete the task."
        )

    def execute(self, input_data: AdvancedMathInput) -> str:
        a_val = input_data.a
        b_val = input_data.b
        op = input_data.operation

        match op:
            case "add":
                result = a_val + b_val
            case "subtract":
                result = a_val - b_val
            case "multiply":
                result = a_val * b_val
            case "divide":
                result = a_val / b_val if b_val != 0 else "undefined"
            case "power":
                result = a_val**b_val
            case "modulo":
                result = a_val % b_val if b_val != 0 else "undefined"
            case _:
                return f"Unsupported operation: {op}"

        if isinstance(result, str):
            return result
        return (
            str(int(result)) if isinstance(result, float) and result.is_integer() else str(result)
        )

    def run_from_json(self, raw_json: str) -> str:
        return self.execute(AdvancedMathInput.model_validate_json(raw_json))

    def validate_tool_call(self, raw_json: str) -> bool:
        try:
            AdvancedMathInput.model_validate_json(raw_json)
            return True
        except ValidationError:
            return False
