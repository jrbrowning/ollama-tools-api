import json

from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel, Field, ValidationError
from toolkit.tools.tool_types import ToolProtocol


class TreeGenInput(BaseModel):
    seed: int = Field(
        ...,
        ge=1,
        le=100,
        description="Integer seed used to initialize deterministic tree generation.",
    )

    trunk: dict[str, int] = Field(
        ...,
        description="Defines the main vertical structure of the tree (the trunk).",
        json_schema_extra={
            "type": "object",
            "properties": {
                "diameter": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "The diameter of the trunk base. Avoid width or radius-related variations.",
                },
                "height": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Total vertical height of the trunk.",
                },
            },
            "required": ["diameter", "height"],
            "additionalProperties": False,
        },
    )

    branch: dict[str, object] = Field(
        ...,
        description="Describes primary branch parameters including shape or orientation.",
        json_schema_extra={
            "type": "object",
            "properties": {
                "angle": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 180,
                    "description": "Angle at which primary branches extend from the trunk (degrees).",
                },
                "growth_rate": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Rate of branch extension over time.",
                },
            },
            "required": ["angle", "growth_rate"],
            "additionalProperties": False,
        },
    )

    secondaryBranch: dict[str, object] = Field(
        ...,
        description="Describes secondary branches extending from primary branches.",
        json_schema_extra={
            "type": "object",
            "properties": {
                "angle": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 180,
                    "description": "Angle of secondary branches relative to parent branch.",
                },
                "growth_rate": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Rate of secondary branch expansion.",
                },
            },
            "required": ["angle", "growth_rate"],
            "additionalProperties": False,
        },
    )

    twig: dict[str, object] = Field(
        ...,
        description="Describes twig structure parameters near the leaf level.",
        json_schema_extra={
            "type": "object",
            "properties": {
                "density": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Compactness of twig growth per unit space.",
                },
                "thickness": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Physical diameter of a single twig.",
                },
            },
            "required": ["density", "thickness"],
            "additionalProperties": False,
        },
    )


class TreeGenTool(ToolProtocol):
    @property
    def name(self) -> str:
        return "generate_tree_config"

    @property
    def description(self) -> str:
        return "Generate a full tree configuration using numeric values between 1 and 100."

    def tool_spec(self) -> ChatCompletionToolParam:
        return ChatCompletionToolParam(
            type="function",
            function={
                "name": self.name,
                "description": self.description,
                "parameters": TreeGenInput.model_json_schema(),
            },
        )

    def tool_intent_prompt(self) -> str:
        return ""

    def tool_system_prompt(self) -> str:
        return (
            "You are a procedural plant generation assistant. You will be asked to generate nested configuration "
            "JSON describing a tree's structure using the `generate_tree_config` tool. Each field is constrained by "
            "strict ranges and nested object structures. Return only valid JSON that adheres exactly to the schema."
        )

    def execute(self, input_data: TreeGenInput) -> str:
        return json.dumps(input_data.model_dump(), indent=2)

    def run_from_json(self, raw_json: str) -> str:
        return self.execute(TreeGenInput.model_validate_json(raw_json, strict=True))

    def validate_tool_call(self, raw_json: str) -> bool:
        """
        # Pydantic's model_json_schema() correctly emits `additionalProperties: false` in JSON Schema,
        # but runtime validation via `model_validate()` doesn't enforce shape for dict[str, object] fields.
        # This means we can't use Pydantic's model_validate_json() directly for shape validation.

        Now... the circular dependency issue arises because....
        # Using submodels would enable runtime validation, but introduces $ref/$defs which break OpenAI's expectations.

        So long term solution is to find another way to validate shape without breaking OpenAI's tool schema expectations.
        # To align both runtime validation and OpenAI tool schema, we validate shape separately using `jsonschema.validate()`.
        """
        try:
            TreeGenInput.model_validate_json(raw_json, strict=True)
            return True
        except ValidationError:
            return False
