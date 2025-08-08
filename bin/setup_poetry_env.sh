#!/bin/bash

# Python + Poetry Environment Setup Script
# Usage: source setup_python_poetry.sh

# === CONFIGURATION ===
MODE="local"  # Change to "global" for system-wide Python
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
if ! command -v pyenv &> /dev/null; then
    echo -e "${RED}❌ pyenv not installed. Get it: https://github.com/pyenv/pyenv${NC}"
    return 1 2>/dev/null || exit 1
fi

if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}🔄 Poetry not found. Installing...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    if ! command -v poetry &> /dev/null; then
        echo -e "${RED}❌ Poetry install failed. Add ~/.local/bin to PATH${NC}"
        return 1 2>/dev/null || exit 1
    else
        echo -e "${GREEN}✅ Poetry installed${NC}"
    fi
fi

# === PYTHON INSTALL ===
echo -e "${YELLOW}🔄 Installing Python ${PYTHON_VERSION} (if needed)...${NC}"
pyenv install -s "$PYTHON_VERSION"

# === EXECUTION MODE SWITCH ===
if [ "$MODE" = "local" ]; then
    # === LOCAL MODE ===
    if [ -f "pyproject.toml" ]; then
        echo -e "${GREEN}✅ Found pyproject.toml${NC}"
        pyenv local "$PYTHON_VERSION"
        poetry config virtualenvs.in-project true
        poetry env use python
        poetry install

        if [ $? -eq 0 ]; then
            VENV_PATH=$(poetry env info --path)
            echo -e "${BLUE}📁 .venv path: $VENV_PATH${NC}"
            if [ -d "$VENV_PATH" ]; then
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
    # === GLOBAL MODE ===
    echo -e "${YELLOW}⚠️ MODE=global: No local project config used${NC}"
    pyenv global "$PYTHON_VERSION"
    echo -e "${GREEN}✅ Set Python ${PYTHON_VERSION} as global version${NC}"
    python --version
fi

echo -e "${GREEN}🎉 Setup complete! Mode: $MODE${NC}"