#!/bin/bash

# Python + Poetry Environment Setup Script
# Usage: source setup_python_poetry.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the directory where the script was called from
CURRENT_DIR="$(pwd)"

echo "Script location: $SCRIPT_DIR"
echo "Current directory: $CURRENT_DIR"

# Define the Python version
PYTHON_VERSION="3.12.2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Python + Poetry Environment Setup${NC}"
echo "Target Python version: ${PYTHON_VERSION}"
echo "Current directory: $(pwd)"

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo -e "${RED}❌ pyenv is not installed. Install it first: https://github.com/pyenv/pyenv${NC}"
    return 1 2>/dev/null || exit 1
fi

# Check if poetry is installed, install if missing
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}🔄 Poetry not found. Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Check if installation worked
    if ! command -v poetry &> /dev/null; then
        echo -e "${RED}❌ Poetry installation failed. You may need to restart your shell or add to PATH manually${NC}"
        echo -e "${BLUE}💡 Add this to your ~/.zshrc or ~/.bashrc:${NC}"
        echo -e "${GREEN}   export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        return 1 2>/dev/null || exit 1
    else
        echo -e "${GREEN}✅ Poetry installed successfully${NC}"
    fi
fi

# Install and set Python version with pyenv
echo -e "${YELLOW}🔄 Setting up Python ${PYTHON_VERSION} with pyenv...${NC}"
pyenv install -s "$PYTHON_VERSION"

# Check if we're in a directory with pyproject.toml
if [ -f "pyproject.toml" ]; then
    echo -e "${GREEN}✅ Found pyproject.toml in current directory${NC}"
    
    # Set local Python version for this directory
    pyenv local "$PYTHON_VERSION"
    echo -e "${GREEN}📌 Set Python ${PYTHON_VERSION} as local version for this directory${NC}"
    
    # Verify Python version
    echo -e "${BLUE}🐍 Python version:${NC}"
    python --version
    
    # Configure Poetry to use the pyenv Python
    poetry env use python
    
    # Install dependencies with Poetry
    echo -e "${YELLOW}📦 Installing dependencies with Poetry...${NC}"
    poetry install
    
    # Check if installation was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Poetry dependencies installed successfully!${NC}"
        
        # Get the virtual environment path
        VENV_PATH=$(poetry env info --path)
        
        if [ -n "$VENV_PATH" ] && [ -d "$VENV_PATH" ]; then
            echo -e "${YELLOW}🔄 Activating Poetry virtual environment...${NC}"
            
            # Activate the virtual environment directly
            source "$VENV_PATH/bin/activate"
            
            echo -e "${GREEN}✅ Virtual environment activated!${NC}"
            echo -e "${BLUE}📍 Virtual environment: $VENV_PATH${NC}"
            echo -e "${BLUE}🐍 Active Python: $(which python)${NC}"
            echo ""
            echo -e "${GREEN}🎯 You can now run: python <your script name>.py${NC}"
        else
            echo -e "${YELLOW}⚠️ Could not find virtual environment path${NC}"
            echo -e "${BLUE}📋 To activate manually, run:${NC}"
            echo -e "${GREEN}   poetry shell${NC}"
        fi
        
    else
        echo -e "${RED}❌ Poetry installation failed!${NC}"
        return 1 2>/dev/null || exit 1
    fi
    
else
    echo -e "${YELLOW}⚠️  No pyproject.toml found in current directory${NC}"
    echo -e "${BLUE}Available options:${NC}"
    echo "1. Set global Python version only"
    echo "2. Look for pyproject.toml in subdirectories"
    
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            pyenv global "$PYTHON_VERSION"
            echo -e "${GREEN}✅ Set Python ${PYTHON_VERSION} as global version${NC}"
            python --version
            ;;
        2)
            echo -e "${BLUE}🔍 Searching for pyproject.toml files...${NC}"
            find . -name "pyproject.toml" -type f | head -5
            echo -e "${YELLOW}💡 Navigate to one of these directories and run this script again${NC}"
            ;;
        *)
            echo -e "${RED}❌ Invalid choice${NC}"
            return 1 2>/dev/null || exit 1
            ;;
    esac
fi

echo -e "${GREEN}🎉 Setup complete!${NC}"