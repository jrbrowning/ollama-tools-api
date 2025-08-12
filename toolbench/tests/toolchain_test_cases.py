# tests/toolchain_test_cases.py

from models.toolchain_test_case import ToolchainModelStage, ToolchainPromptSpec, ToolchainTestCase

TEST_CASES = [
        # Mode 1: Chat Completion (Non-Streaming)
    ToolchainTestCase(
        id="chat_completion",
        stage_a=ToolchainModelStage(
            system_prompt="You are a helpful travel assistant.",
            user_prompt="Tell me a little about how the streets are named in Washington, DC.",
            model_container="traditional",
            stream=False,
            prompt_tool_spec=ToolchainPromptSpec(
                strategy="chat_completion",
                max_tokens=1024,
                temperature=1.0,
            ),
            synthesis=False,
        ),
        evaluation=False,
    ),
]
