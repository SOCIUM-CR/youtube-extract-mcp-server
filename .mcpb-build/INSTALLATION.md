# YouTube Extract MCP - Installation Guide

## For Claude Desktop Users

### Quick Installation (Coming Soon)

Once published to the Anthropic Extension Directory:
1. Open Claude Desktop
2. Go to Settings → Extensions
3. Search for "YouTube Transcript Extractor"
4. Click "Install"
5. Configure output directory when prompted

### Manual Installation (Current)

1. **Download the `.mcpb` file**
   - From GitHub Releases: https://github.com/SOCIUM-CR/youtube-extract-mcp-server/releases
   - Or build from source (see below)

2. **Install the extension**
   - Double-click the `.mcpb` file, OR
   - In Claude Desktop: Settings → Extensions → Advanced → "Install Extension..."
   - Select the downloaded `.mcpb` file

3. **Configure**
   - When prompted, set your preferred output directory
   - Default: `~/YouTube-Transcripts`

4. **Verify Installation**
   - Restart Claude Desktop
   - The extension should appear in your Extensions list
   - Try: "Extract the transcription from [YouTube URL]"

## Prerequisites

### Required
- **Python 3.11 or higher**
  - macOS: `brew install python@3.11`
  - Windows: Download from https://www.python.org/downloads/
  - Linux: `sudo apt install python3.11` (Ubuntu/Debian)

- **uv** (Python package manager)
  - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows: `irm https://astral.sh/uv/install.ps1 | iex`

### Automatic (Handled by Extension)
- `yt-dlp` - YouTube video downloader
- `youtube-transcript-api` - Transcript API fallback
- `mcp` - Model Context Protocol library

## Build from Source

If you want to build the `.mcpb` file yourself:

```bash
# 1. Clone repository
git clone https://github.com/SOCIUM-CR/youtube-extract-mcp-server.git
cd youtube-extract-mcp-server

# 2. Install MCPB CLI
npm install -g @anthropic-ai/mcpb

# 3. Build package
cd .mcpb-build
mcpb pack

# 4. Install the generated .mcpb file
# Double-click or use Claude Desktop → Settings → Extensions
```

## Usage Examples

### Extract Single Video
```
Extract the transcription from https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Extract with Specific Language
```
Extract the Spanish transcription from [YouTube URL]
```

### Save Locally
```
Extract and save the transcription from [YouTube URL] to my configured directory
```

### Extract Playlist
```
Extract all videos from this playlist: [Playlist URL]
```

### Configure Output Directory
```
Set my YouTube transcription directory to ~/Documents/Transcripts
```

## Troubleshooting

### Extension not appearing
1. Restart Claude Desktop completely
2. Check Settings → Extensions → Extension list
3. Verify Python 3.11+ installed: `python3 --version`
4. Verify uv installed: `uv --version`

### "Python not found" error
- Install Python 3.11+
- Ensure it's in your PATH
- Try: `which python3` (macOS/Linux) or `where python` (Windows)

### "uv not found" error
- Install uv: https://github.com/astral-sh/uv
- Restart your terminal/Claude Desktop after installation

### Extraction fails
- Check your internet connection
- Try with a different video URL
- The server uses triple-fallback system (yt-dlp → alternative → youtube-transcript-api)
- Check Claude Desktop logs for detailed error messages

### Permission errors
- Ensure the output directory is writable
- Try changing to a directory you own: `~/YouTube-Transcripts`

## Support

- **Issues:** https://github.com/SOCIUM-CR/youtube-extract-mcp-server/issues
- **Discussions:** https://github.com/SOCIUM-CR/youtube-extract-mcp-server/discussions
- **Documentation:** https://github.com/SOCIUM-CR/youtube-extract-mcp-server

## Features

✅ **Automatic language detection**
✅ **Triple-fallback system** (99%+ success rate)
✅ **Dual formats** (plain text + timestamps)
✅ **Playlist support** (up to 50 videos default)
✅ **Local file persistence**
✅ **Zero configuration** (works out of the box)

## Privacy

- All processing happens **locally** on your machine
- No data sent to external servers (except YouTube API)
- Transcriptions stored **only** in your configured directory
- No telemetry or tracking

## License

MIT License - See LICENSE file in repository
