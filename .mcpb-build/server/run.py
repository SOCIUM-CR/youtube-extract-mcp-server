#!/usr/bin/env python3
"""
Universal launcher for YouTube Extract MCP Server
Works on Windows, macOS, and Linux

Handles:
- uv auto-detection across different OS
- Fallback to venv if uv not available
- Cross-platform path handling
- First-run dependency installation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def find_uv():
    """
    Find uv executable in common locations across different OS.

    Returns:
        str: Path to uv executable, or None if not found
    """
    # Try uv in PATH first
    try:
        result = subprocess.run(['uv', '--version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            return 'uv'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Platform-specific common locations
    os_name = platform.system()

    if os_name == 'Windows':
        # Windows common paths
        potential_paths = [
            Path.home() / '.cargo' / 'bin' / 'uv.exe',
            Path.home() / 'AppData' / 'Local' / 'Programs' / 'uv' / 'uv.exe',
            Path('C:\\') / 'Program Files' / 'uv' / 'uv.exe',
        ]
    elif os_name == 'Darwin':  # macOS
        # macOS common paths
        potential_paths = [
            Path('/usr/local/bin/uv'),
            Path('/opt/homebrew/bin/uv'),
            Path.home() / '.cargo' / 'bin' / 'uv',
            Path.home() / '.local' / 'bin' / 'uv',
        ]
    else:  # Linux and others
        # Linux common paths
        potential_paths = [
            Path('/usr/local/bin/uv'),
            Path('/usr/bin/uv'),
            Path.home() / '.cargo' / 'bin' / 'uv',
            Path.home() / '.local' / 'bin' / 'uv',
        ]

    # Check each potential path
    for path in potential_paths:
        if path.exists() and path.is_file():
            try:
                # Verify it actually works
                result = subprocess.run([str(path), '--version'],
                                      capture_output=True,
                                      timeout=5)
                if result.returncode == 0:
                    return str(path)
            except (subprocess.TimeoutExpired, PermissionError):
                continue

    return None

def setup_venv(venv_dir):
    """
    Create virtual environment and install dependencies.

    Args:
        venv_dir: Path to venv directory
    """
    print("First-time setup: Creating virtual environment...", file=sys.stderr)

    # Create venv
    subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)

    # Determine python path based on OS
    if platform.system() == 'Windows':
        python_path = venv_dir / 'Scripts' / 'python.exe'
    else:
        python_path = venv_dir / 'bin' / 'python'

    print("Installing dependencies (mcp, yt-dlp, youtube-transcript-api)...", file=sys.stderr)

    # Upgrade pip (using python -m pip for Python 3.13+ compatibility)
    subprocess.run([str(python_path), '-m', 'pip', 'install', '--quiet', '--upgrade', 'pip'], check=True)

    # Install dependencies (using python -m pip for Python 3.13+ compatibility)
    subprocess.run([
        str(python_path),
        '-m',
        'pip',
        'install',
        '--quiet',
        'mcp>=1.0.0',
        'yt-dlp>=2024.4.9',
        'youtube-transcript-api>=1.2.3'
    ], check=True)

    print("Setup complete!", file=sys.stderr)
    return python_path

def main():
    """Main entry point"""
    # Use resolve() instead of absolute() - it canonicalizes paths more reliably
    # This ensures paths remain valid even after process replacement with os.execv()
    script_dir = Path(__file__).parent.resolve()
    server_script = script_dir / 'youtube_extract_mcp.py'

    # Try to find uv
    uv_path = find_uv()

    if uv_path:
        # Use uv (fastest option)
        print(f"Using uv from: {uv_path}", file=sys.stderr)
        try:
            # Pre-resolve uv path before exec to avoid path resolution issues
            # Using os.execv() is correct for MCP STDIO servers - maintains STDIO streams
            uv_exe = str(Path(uv_path).resolve())
            os.execv(uv_exe, [
                uv_exe,
                '--directory', str(script_dir),
                'run',
                'youtube_extract_mcp.py'
            ] + sys.argv[1:])
        except Exception as e:
            print(f"Failed to run with uv: {e}", file=sys.stderr)
            print("Falling back to venv...", file=sys.stderr)

    # Fallback to venv
    venv_dir = script_dir / '.venv'

    # Determine python path based on OS
    if platform.system() == 'Windows':
        python_path = venv_dir / 'Scripts' / 'python.exe'
    else:
        python_path = venv_dir / 'bin' / 'python'

    # Create venv if it doesn't exist
    if not venv_dir.exists():
        python_path = setup_venv(venv_dir)

    # Run the server with venv python
    # Pre-resolve all paths before os.execv() to prevent path resolution issues
    # Using os.execv() is REQUIRED for MCP STDIO servers to maintain proper STDIO communication
    # The key is to resolve paths BEFORE exec, not to avoid exec altogether
    python_exe = str(python_path.resolve())
    server_py = str(server_script.resolve())

    try:
        # os.execv() replaces current process - this is CORRECT for MCP servers because:
        # 1. STDIO streams (stdin/stdout/stderr) pass through naturally
        # 2. Server runs as the main process, not a subprocess
        # 3. No blocking - server can listen to stdin indefinitely
        # 4. Pre-resolved paths prevent Windows/Electron path resolution issues
        os.execv(python_exe, [python_exe, server_py] + sys.argv[1:])
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
