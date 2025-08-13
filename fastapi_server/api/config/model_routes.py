# File: api/config/model_routes.py

import os

ENABLE_LOCAL_GPU_MODEL = os.getenv("ENABLE_LOCAL_GPU_MODEL", "true").lower() == "true"

# Local models
LOCAL_GPU = os.getenv("LOCAL_GPU", "")
TRADITIONAL_MODEL = os.getenv("TRADITIONAL_MODEL", "")
TRADITIONAL_MODEL_ALT = os.getenv("TRADITIONAL_MODEL_ALT", "")
REASONING_MODEL = os.getenv("REASONING_MODEL", "")
REASONING_MODEL_ALT = os.getenv("REASONING_MODEL_ALT", "")

# Remote models
REMOTE_OPENAI_MODEL = os.getenv("REMOTE_OPENAI_MODEL", "")
CLAUDE_SONNET_MODEL = os.getenv("CLAUDE_SONNET_MODEL", "")
CLAUDE_OPUS_MODEL = os.getenv("CLAUDE_OPUS_MODEL", "")

# Base URLs
model_service_map = {
    # Local Ollama
    "traditional": "http://traditional_model:11434",
    "traditional_alt": "http://traditional_model_alt:11434",
    "reasoning": "http://reasoning_model:11434",
    "reasoning_alt": "http://reasoning_model_alt:11434",
    # Remote OpenAI-compatible
    "remote_openai": "https://api.groq.com",  # Or "https://api.openai.com"
    # Remote Claude (MCP)
    "claude_sonnet": "https://api.anthropic.com",
    "claude_opus": "https://api.anthropic.com",
}

# Model versions
model_map = {
    "traditional": TRADITIONAL_MODEL,
    "traditional_alt": TRADITIONAL_MODEL_ALT,
    "reasoning": REASONING_MODEL,
    "reasoning_alt": REASONING_MODEL_ALT,
    "remote_openai": REMOTE_OPENAI_MODEL,
    "claude_sonnet": CLAUDE_SONNET_MODEL,
    "claude_opus": CLAUDE_OPUS_MODEL,
}

# Protocol routing
protocol_map = {
    "traditional": "openai",
    "traditional_alt": "openai",
    "reasoning": "openai",
    "reasoning_alt": "openai",
    "local_gpu": "openai",
    "remote_openai": "openai",
    "claude_sonnet": "mcp",
    "claude_opus": "mcp",
}

# Optional: enable local GPU model dynamically
if ENABLE_LOCAL_GPU_MODEL:
    model_service_map["local_gpu"] = "http://host.docker.internal:11434"
    model_map["local_gpu"] = LOCAL_GPU

# Debugging
print(ENABLE_LOCAL_GPU_MODEL, "ENABLE_LOCAL_GPU_MODEL")
print("model_service_map:", model_service_map)
print("model_map:", model_map)
print("protocol_map:", protocol_map)
