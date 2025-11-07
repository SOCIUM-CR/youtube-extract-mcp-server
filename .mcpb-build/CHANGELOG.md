# Changelog

All notable changes to the YouTube Extract MCP Server extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Resources API for transcript history
- Prompts API for common use cases
- HTTP transport option for multi-client support
- Remote deployment option

## [1.0.0] - 2025-11-07

### Added
- **Claude Desktop Extension** (.mcpb) packaging
- One-click installation support
- User configuration for output directory
- Complete tool manifest with 4 tools:
  - `youtube_extract_video` - Extract single video transcription
  - `youtube_extract_playlist` - Extract playlist transcriptions
  - `configure_output_directory` - Set output directory
  - `show_current_config` - Display configuration

### Features
- **Triple-fallback system** for transcription extraction
  - Primary: yt-dlp with PO Token bypass
  - Secondary: yt-dlp with alternative clients (android, web_embedded)
  - Tertiary: youtube-transcript-api (guaranteed fallback)
- **Automatic language detection**
- **Dual output formats**
  - Plain text (clean, readable)
  - Timestamped text (with timing information)
- **Playlist support** (up to 50 videos default)
- **Local file persistence** with organized structure
- **99%+ success rate** verified

### Technical
- Python 3.11+ required
- Auto-managed dependencies with `uv`
- PEP 723 inline dependency metadata
- Zero external configuration needed
- Platform support: macOS, Windows, Linux

### Security
- All processing local (no data sent to third parties)
- Filesystem write permissions limited to output directory
- Network access only for YouTube API calls

## [0.x.x] - Pre-release Versions

Historical changelog from original stdio-only implementation:

### [0.2.0] - 2025-07-19
- Fixed: PO Token error handling
- Added: youtube-transcript-api as fallback
- Updated: yt-dlp to version 2025.6.30
- Improved: Error detection and recovery

### [0.1.0] - 2024-12-01
- Initial stdio-based MCP server
- Core transcription extraction with yt-dlp
- Basic language detection
- Playlist processing support

---

## Migration Guide

### From stdio to .mcpb Extension

If you were previously using the stdio version:

1. **Backup your configuration** (if any):
   ```bash
   cp ~/.youtube-extract-mcp-config.json ~/backup/
   ```

2. **Remove old Claude Desktop config**:
   - Open `claude_desktop_config.json`
   - Remove the manual `youtube-extract-mlx` server entry

3. **Install the extension**:
   - Follow instructions in INSTALLATION.md

4. **Reconfigure output directory** (if changed from default):
   - Use the configuration UI in Claude Desktop
   - Or use the `configure_output_directory` tool

### Configuration Changes

| Old (stdio) | New (.mcpb) |
|-------------|-------------|
| Manual JSON editing | UI-based configuration |
| Absolute paths required | Template variables supported |
| Manual uv path | Automatic detection |
| Manual restart needed | Auto-restart on config change |

### Breaking Changes

None - The extension maintains full backward compatibility with the stdio interface.

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/SOCIUM-CR/youtube-extract-mcp-server/issues
- Discussions: https://github.com/SOCIUM-CR/youtube-extract-mcp-server/discussions

## Contributors

- SOCIUM-CR Team
- Community contributors (see GitHub)

Thank you to everyone who helped make this project better! 🎉
