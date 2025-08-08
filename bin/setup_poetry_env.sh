# File: scripts/setup_python_poetry.sh
#!/bin/bash
# Usage: source scripts/setup_python_poetry.sh
# Purpose: Create/use a local .venv next to pyproject.toml with pyenv + poetry

# === CONFIGURATION ===
MODE="local"  # keep local-only
PYTHON_VERSION="3.12.2"

# === SCRIPT BOOTSTRAP ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$(pwd)"

# === COLOR OUTPUT ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Python + Poetry Environment Setup [Mode: $MODE]${NC}"
echo "Script: $SCRIPT_DIR"
echo "Working dir: $CURRENT_DIR"
echo "Python version: ${PYTHON_VERSION}"

# === CHECK DEPENDENCIES ===
if ! command -v pyenv >/dev/null 2>&1; then
    echo -e "${RED}❌ pyenv not installed. Get it: https://github.com/pyenv/pyenv${NC}"
    return 1 2>/dev/null || exit 1
fi

if ! command -v poetry >/dev/null 2>&1; then
    echo -e "${YELLOW}🔄 Poetry not found. Installing...${NC}"
    if ! command -v curl >/dev/null 2>&1; then
        echo -e "${RED}❌ curl is required to install Poetry${NC}"
        return 1 2>/dev/null || exit 1
    fi
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}❌ python3 is required to bootstrap Poetry installer${NC}"
        return 1 2>/dev/null || exit 1
    fi
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    if ! command -v poetry >/dev/null 2>&1; then
        echo -e "${RED}❌ Poetry install failed. Ensure ~/.local/bin is on PATH${NC}"
        return 1 2>/dev/null || exit 1
    else
        echo -e "${GREEN}✅ Poetry installed${NC}"
    fi
fi

# Ensure pyenv shims are active in THIS shell before using them
if command -v pyenv >/dev/null 2>&1; then
    eval "$(pyenv init -)"
fi

# === PYTHON INSTALL ===
echo -e "${YELLOW}🔄 Ensuring Python ${PYTHON_VERSION} is available...${NC}"
pyenv install -s "$PYTHON_VERSION"

# === EXECUTION MODE SWITCH ===
if [ "$MODE" = "local" ]; then
    # === LOCAL MODE ===
    if [ -f "pyproject.toml" ]; then
        echo -e "${GREEN}✅ Found pyproject.toml${NC}"
        pyenv local "$PYTHON_VERSION"
        poetry config virtualenvs.in-project true

        # Bind Poetry to the exact pyenv interpreter (prevents wrong system python)
        PY_BIN="$(pyenv which python)"
        if [ -z "$PY_BIN" ]; then
            echo -e "${RED}❌ Could not resolve pyenv python for ${PYTHON_VERSION}${NC}"
            return 1 2>/dev/null || exit 1
        fi
        poetry env use "$PY_BIN"

        poetry install --no-interaction
        if [ $? -eq 0 ]; then
            VENV_PATH="$(poetry env info --path)"
            echo -e "${BLUE}📁 .venv path: $VENV_PATH${NC}"
            if [ -d "$VENV_PATH" ]; then
                # Activate into current shell session
                # shellcheck disable=SC1090
                source "$VENV_PATH/bin/activate"
                echo -e "${GREEN}✅ Activated local .venv environment${NC}"
                echo -e "${BLUE}🐍 Python: $(which python)${NC}"
            fi
        else
            echo -e "${RED}❌ Poetry install failed${NC}"
            return 1 2>/dev/null || exit 1
        fi
    else
        echo -e "${RED}❌ pyproject.toml not found in $(pwd)${NC}"
        return 1 2>/dev/null || exit 1
    fi

else
    # === GLOBAL MODE (intentionally disabled to keep it local/rock-solid) ===
    echo -e "${YELLOW}⚠️ MODE=global disabled. This script is for local .venv only.${NC}"
    return 2 2>/dev/null || exit 2
fi

echo -e "${GREEN}🎉 Setup complete! Mode: $MODE${NC}"