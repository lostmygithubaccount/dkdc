#!/bin/bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."
    
    if ! command -v curl &> /dev/null; then
        echo "Error: curl is required to install uv but is not installed"
        exit 1
    fi
    
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if ! command -v fnm &> /dev/null; then
    echo "fnm not found, installing..."
    
    if ! command -v curl &> /dev/null; then
        echo "Error: curl is required to install fnm but is not installed"
        exit 1
    fi
    
    curl -fsSL https://fnm.vercel.app/install | bash
fi

./bin/dotfiles.py --yes
