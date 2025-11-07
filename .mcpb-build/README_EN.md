# YouTube Extract MCP Server

A self-contained Python MCP server for robust YouTube transcription extraction, managed with `uv`.

## Features

- **Automatic language detection**
- **Local file persistence**
- **Global configuration**
- **Dual transcript formats** (plain text and timestamped)
- **Playlist processing**

## Prerequisites

- **uv**: A fast Python package manager. If you don't have it, install it based on your operating system:

  **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  **Windows (using PowerShell):**
  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SOCIUM-CR/youtube-extract-mcp-server.git
    cd youtube-extract-mcp-server
    ```

2.  **Install dependencies (optional):**
    `uv` will install dependencies automatically when running the script. If you want to install them manually, you can use:
    ```bash
    uv pip install -r requirements.txt
    ```

## Claude Desktop Configuration

1.  Find your Claude Desktop configuration file:

    **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
    **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
    **Linux:** `~/.config/Claude/claude_desktop_config.json`

2.  Add this server configuration. **It is crucial** that you replace the example paths with the **absolute paths** on your system.

    ```json
    {
      "mcpServers": {
        "youtube-extract-mlx": {
          "command": "/absolute/path/to/your/uv",
          "args": [
            "--directory",
            "/absolute/path/to/project/",
            "run",
            "youtube_extract_mcp.py"
          ],
          "cwd": "/absolute/path/to/project/"
        }
      }
    }
    ```

    *   `command`: The absolute path to your `uv` executable. You can find this by running `which uv` in your terminal.
    *   `args`: The first argument (`--directory`) must be the absolute path to this project's folder. The rest of the arguments should not be modified.
    *   `cwd`: The current working directory, which must be the same absolute path to this project's folder.

3.  Restart Claude Desktop for the changes to take effect.

## Usage

### Available Tools

- `youtube_extract_video`: Extract video metadata and transcription.
- `configure_output_directory`: Set the local directory where transcripts will be saved.
- `show_current_config`: Display the current global configuration.
- `youtube_extract_playlist`: Extract transcripts from an entire YouTube playlist.

### Example

```bash
# 1. Configure a directory to save transcripts
configure_output_directory ~/MyTranscripts

# 2. Extract a video and save it locally
youtube_extract_video url="https://www.youtube.com/watch?v=dQw4w9WgXcQ" save_locally=true

# 3. Extract an entire playlist
youtube_extract_playlist playlist_url="https://www.youtube.com/playlist?list=PL-osiE80TeTucQ0nA_cItCgpcin0U-unE"
```

## License

This project is licensed under the MIT License.
