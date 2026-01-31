#!/bin/bash
set -e

REPO="polyphilz/vv"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Installing vv (VibeVox)..."

# Detect platform
OS="$(uname -s)"
ARCH="$(uname -m)"
APPLE_SILICON=false
if [[ "$OS" == "Darwin" && ("$ARCH" == "arm64" || "$ARCH" == "aarch64") ]]; then
    APPLE_SILICON=true
fi

# Check for Python 3.10+
check_python() {
    if command -v python3 &> /dev/null; then
        version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [[ "$major" -ge 3 && "$minor" -ge 10 ]]; then
            return 0
        fi
    fi
    echo -e "${RED}Error: Python 3.10+ is required${NC}"
    echo "Install Python from https://www.python.org/downloads/"
    exit 1
}

check_python

# Determine install method and package spec
if [[ "$APPLE_SILICON" == true ]]; then
    PKG_SPEC="vv[apple] @ git+https://github.com/${REPO}"
else
    PKG_SPEC="git+https://github.com/${REPO}"
fi

# Install using uv, pipx, or pip (in order of preference)
if command -v uv &> /dev/null; then
    echo -e "${GREEN}Installing with uv...${NC}"
    uv tool install --force "$PKG_SPEC"
elif command -v pipx &> /dev/null; then
    echo -e "${GREEN}Installing with pipx...${NC}"
    pipx install --force "$PKG_SPEC"
else
    echo -e "${GREEN}Installing with pip...${NC}"
    pip install --user "$PKG_SPEC"

    # Warn about PATH for pip --user installs
    echo ""
    echo -e "${YELLOW}Note: Installed with pip --user${NC}"
    echo "You may need to add ~/.local/bin to your PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo -e "${GREEN}vv installed successfully!${NC}"
echo ""
echo "Run 'vv --help' to get started."
echo ""
if ! command -v vv &> /dev/null; then
    echo -e "${YELLOW}You may need to restart your shell or run:${NC}"
    echo "  source ~/.zshrc  # or ~/.bashrc"
fi
