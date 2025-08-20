# tests/toolchain_test_cases.py

from models.toolchain_test_case import ToolchainModelStage, ToolchainPromptSpec, ToolchainTestCase

TEST_CASES = [
    ToolchainTestCase(
        id="chat_completion_1",
        stage_a=ToolchainModelStage(
            system_prompt=(
                "You are a weather assistant that answers location-based weather queries. "
                "When a user asks about the weather in a location, convert the city to coordinates, "
                "call the `get_weather` tool with latitude and longitude, and return the result. "
                "After the tool call, summarize the weather condition using simple, factual language. "
                "Avoid making predictions or interpretations not supported by the data. "
                "Only respond with information directly derived from tool output or coordinates."
            ),
            user_prompt="What's going on in Washington, DC today?",
            model_container="traditional",
            stream=False,
            prompt_tool_spec=ToolchainPromptSpec(
                strategy="tool_call",
                max_tokens=128,
                temperature=0.0,
            ),
            prompt_synthesis_spec=ToolchainPromptSpec(
                strategy="synthesis",
                max_tokens=1024,
                temperature=1.0,
            ),
            synthesis=True,
        ),
        evaluation=False,
    ),
    # ToolchainTestCase(
    #     id="chat_completion_2",
    #     stage_a=ToolchainModelStage(
    #         system_prompt="You are a helpful travel assistant.",
    #         user_prompt="Tell me a little about how the streets are named in Washington, DC.",
    #         model_container="traditional_alt",
    #         stream=False,
    #         prompt_tool_spec=ToolchainPromptSpec(
    #             strategy="chat_completion",
    #             max_tokens=128,
    #             temperature=1.0,
    #         ),
    #         synthesis=False,
    #     ),
    #     evaluation=False,
    # ),
    # ToolchainTestCase(
    #     id="chat_completion_3",
    #     stage_a=ToolchainModelStage(
    #         system_prompt="You are a helpful travel assistant.",
    #         user_prompt="Tell me a little about how the streets are named in Washington, DC.",
    #         model_container="reasoning",
    #         stream=False,
    #         prompt_tool_spec=ToolchainPromptSpec(
    #             strategy="chat_completion",
    #             max_tokens=128,
    #             temperature=1.0,
    #         ),
    #         synthesis=False,
    #     ),
    #     evaluation=False,
    # ),
    # ToolchainTestCase(
    #     id="chat_completion_4",
    #     stage_a=ToolchainModelStage(
    #         system_prompt="You are a helpful travel assistant.",
    #         user_prompt="Tell me a little about how the streets are named in Washington, DC.",
    #         model_container="reasoning_alt",
    #         stream=False,
    #         prompt_tool_spec=ToolchainPromptSpec(
    #             strategy="chat_completion",
    #             max_tokens=128,
    #             temperature=1.0,
    #         ),
    #         synthesis=False,
    #     ),
    #     evaluation=False,
    # ),
    # ToolchainTestCase(
    #     id="chat_completion_5",
    #     stage_a=ToolchainModelStage(
    #         system_prompt="You are a helpful travel assistant.",
    #         user_prompt="Tell me a little about how the streets are named in Washington, DC.",
    #         model_container="local_gpu",
    #         stream=False,
    #         prompt_tool_spec=ToolchainPromptSpec(
    #             strategy="chat_completion",
    #             max_tokens=128,
    #             temperature=1.0,
    #         ),
    #         synthesis=False,
    #     ),
    #     evaluation=False,
    # ),
    # ToolchainTestCase(
    #     id="chat_completion_1",
    #     stage_a=ToolchainModelStage(
    #         system_prompt=(
    #             "You are a weather assistant that answers location-based weather queries. "
    #             "When a user asks about the weather in a location, convert the city to coordinates, "
    #             "call the `get_weather` tool with latitude and longitude, and return the result. "
    #             "After the tool call, summarize the weather condition using simple, factual language. "
    #             "Avoid making predictions or interpretations not supported by the data. "
    #             "Only respond with information directly derived from tool output or coordinates."
    #         ),
    #         user_prompt="What's going on in Washington, DC today?",
    #         model_container="traditional",
    #         stream=False,
    #         prompt_tool_spec=ToolchainPromptSpec(
    #             strategy="tool_call",
    #             max_tokens=128,
    #             temperature=1.0,
    #         ),
    #         synthesis=False,
    #     ),
    #     evaluation=False,
    # ),
    # # # Mode 4 Tool + Synthesis (Non-Streaming)
    # ToolchainTestCase(
    #     id="weather_tool_synthesis",
    #     stage_a=ToolchainModelStage(
    #         system_prompt=(
    #             "You are a weather assistant that answers location-based weather queries. "
    #             "When a user asks about the weather in a location, convert the city to coordinates, "
    #             "call the `get_weather` tool with latitude and longitude, and return the result. "
    #             "After the tool call, summarize the weather condition using simple, factual language. "
    #             "Avoid making predictions or interpretations not supported by the data. "
    #             "Only respond with information directly derived from tool output or coordinates."
    #         ),
    #         user_prompt="What's the weather like in Washington, DC today?",
    #         model_container="traditional",
    #         stream=False,
    #         prompt_tool_spec=ToolchainPromptSpec(
    #             strategy="tool_call",
    #             max_tokens=1024,
    #             temperature=0.0,
    #         ),
    #         prompt_synthesis_spec=ToolchainPromptSpec(
    #             strategy="synthesis",
    #             max_tokens=1024,
    #             temperature=0.0,
    #         ),
    #         synthesis=True,
    #     ),
    #     evaluation=False,
    # ),
]
