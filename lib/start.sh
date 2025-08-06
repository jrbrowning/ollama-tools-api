#!/bin/bash
# Ollama startup script (one model per container)

set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# --- ENV VALIDATION ---
if [ -z "$MODEL_NAME" ]; then
    log "❌ ERROR: MODEL_NAME environment variable is required"
    exit 1
fi

if [ "$OFFLINE_MODE" != "true" ] && [ "$OFFLINE_MODE" != "false" ]; then
    log "❌ ERROR: OFFLINE_MODE must be 'true' or 'false' — got '$OFFLINE_MODE'"
    exit 1
fi

# --- START OLLAMA SERVER ---
log "🚀 Starting Ollama server"
export OLLAMA_HOST=0.0.0.0
export OLLAMA_PORT=11434
ollama serve &

# --- WAIT FOR SERVER TO COME ONLINE ---
log "⏳ Waiting for Ollama to report readiness on port 11434..."
RETRIES=0
until curl -s "http://localhost:11434" | grep -q "Ollama is running"; do
    sleep 1
    RETRIES=$((RETRIES + 1))
    if [ "$RETRIES" -gt 10 ]; then
        log "❌ Ollama did not become ready in 10 seconds."
        curl -v "http://localhost:11434" || true
        ss -ltn || netstat -ltn || true
        exit 1
    fi
done
log "✅ Ollama is reporting ready."

# --- VERIFY OR PULL MODEL ---
MODEL="$MODEL_NAME"

if [ "$OFFLINE_MODE" == "true" ]; then
    log "🔍 Checking if model '$MODEL' is cached locally..."
    if ! ollama list | grep -q "$MODEL"; then
        log "❌ Model '$MODEL' not found in local registry (offline mode enabled)"
        exit 1
    fi
    log "✅ Model '$MODEL' is cached and ready."
else
    log "📦 Pulling model '$MODEL' from registry..."
    if ! ollama pull "$MODEL"; then
        log "❌ Failed to pull model: $MODEL"
        ollama list
        exit 1
    fi
    log "✅ Model '$MODEL' successfully pulled."
fi

log "🏁 Startup complete. Ollama is serving model: $MODEL"
wait