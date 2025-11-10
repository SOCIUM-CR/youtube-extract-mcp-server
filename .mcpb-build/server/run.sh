#!/bin/bash
# Auto-setup wrapper for YouTube Extract MCP Server
# Tries to use uv if available, falls back to venv

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Try to find uv in common locations
UV_CMD=""
for uv_path in \
    "uv" \
    "/usr/local/bin/uv" \
    "/opt/homebrew/bin/uv" \
    "$HOME/.cargo/bin/uv" \
    "$HOME/.local/bin/uv"; do
    if command -v "$uv_path" &> /dev/null; then
        UV_CMD="$uv_path"
        break
    fi
done

# If uv is available, use it (fastest)
if [ -n "$UV_CMD" ]; then
    exec "$UV_CMD" run youtube_extract_mcp.py "$@"
fi

# Fallback: use venv
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "First-time setup: Creating virtual environment..." >&2
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet "mcp>=1.0.0" "yt-dlp>=2024.4.9" "youtube-transcript-api>=0.6.0"
    echo "Setup complete!" >&2
fi

exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/youtube_extract_mcp.py" "$@"
