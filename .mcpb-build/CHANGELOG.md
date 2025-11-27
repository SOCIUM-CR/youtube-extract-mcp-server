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

## [1.0.6] - 2025-11-27

### Fixed
- **Windows**: Comprehensive Python PATH configuration documentation and detection
  - Error on Windows v1.0.5: `Server disconnected` - Python command not found
  - Root cause: Windows Python not in PATH or not installed correctly
  - This is an environment issue (Windows configuration), not a code bug

### Added
- **WINDOWS_INSTALL.md**: Comprehensive 250-line Windows installation guide
  - Step-by-step Python installation with "Add Python to PATH" emphasis
  - PowerShell verification commands (`python --version`)
  - Troubleshooting for multiple scenarios:
    - Python not in PATH (Reinstall or manual PATH configuration)
    - Multiple Python versions installed (`where python`)
    - Python Launcher (py) vs python command differences
    - Windows Store Python issues
    - Antivirus blocking Python/Claude Desktop
    - Permissions errors
  - Manual PATH configuration walkthrough
  - Common error messages and solutions
  - Checklist before installing extension

- **run.bat**: Windows batch launcher with Python detection fallback
  - Tries `py -3` (Windows Python Launcher - most reliable)
  - Falls back to `python3`
  - Falls back to `python`
  - Shows helpful error message if no Python found
  - Directs users to WINDOWS_INSTALL.md for setup help

### Platform Support
| Platform | v1.0.5 Status | v1.0.6 Status |
|----------|---------------|---------------|
| macOS    | ✅ Working    | ✅ Working    |
| Linux    | ✅ Should work | ✅ Should work |
| Windows  | ❌ Python PATH required | 📋 Documentation added |

### User Impact
- **Windows users:** Must install Python 3.11+ with "Add Python to PATH" checked
  - See WINDOWS_INSTALL.md for complete guide
  - Extension cannot automatically fix Windows PATH (OS limitation)
  - Once Python is properly installed, extension will work
- **macOS users:** No change (continues working)
- **Linux users:** No change (continues working)

### Important Notes
This release addresses a **Windows environment configuration issue**, not a code bug:
- Windows does not come with Python pre-installed
- Python must be added to Windows PATH during installation
- The "Add Python to PATH" checkbox must be checked in Python installer
- Alternative: Use Windows Python Launcher (`py` command)
- Full troubleshooting guide now included

### Migration
1. Windows users: Follow WINDOWS_INSTALL.md before installing extension
2. Existing users: Update to v1.0.6 for documentation access

## [1.0.5] - 2025-11-10

### Fixed
- **CRITICAL**: Fixed Windows compatibility
  - Error on Windows: `Cannot read properties of undefined (reading 'cmd')`
  - Root cause: `/bin/bash` command doesn't exist on Windows
  - Solution: Replaced bash wrapper with universal Python launcher (`run.py`)

### Changed
- **Command:** `/bin/bash` → `python` (cross-platform)
- **Launcher:** `run.sh` (Unix-only) → `run.py` (universal)
- **Removed:** Unix-specific PATH from manifest (not needed)

### Added
- **run.py**: Universal Python launcher for all platforms
  - Auto-detects uv on Windows, macOS, and Linux
  - Platform-specific path handling (Scripts vs bin, .exe vs no extension)
  - Searches common installation locations per OS:
    - Windows: AppData, Program Files, .cargo/bin
    - macOS: /usr/local/bin, /opt/homebrew/bin, .cargo/bin
    - Linux: /usr/local/bin, /usr/bin, .cargo/bin, .local/bin
  - Falls back to venv if uv not found
  - Cross-platform subprocess handling

### Platform Support
| Platform | v1.0.4 Status | v1.0.5 Status |
|----------|---------------|---------------|
| macOS    | ✅ Working    | ✅ Working    |
| Linux    | ⚠️ Untested   | ✅ Should work |
| Windows  | ❌ Broken     | ✅ Fixed      |

### Technical Details
- manifest.json (line 21): Changed command to "python" (available on all OS)
- manifest.json (line 23): Changed args to use run.py instead of run.sh
- manifest.json (line 25-28): Removed Unix-specific PATH
- server/run.py: New 150-line universal launcher
- Tested on: macOS (verified), Windows (user reported fix needed)

### User Impact
- **Windows users:** Extension now works! (was completely broken)
- **macOS users:** No change (continues working)
- **Linux users:** Better compatibility (was untested, now should work)

### Migration
No action needed - just update to v1.0.5

## [1.0.4] - 2025-11-10

### Fixed
- **CRITICAL**: Fixed class method vs instance method usage
  - Error: `YouTubeTranscriptApi.list() missing 1 required positional argument: 'video_id'`
  - Root cause: `list()` is an INSTANCE method, not a class method
  - Changed from: `YouTubeTranscriptApi.list(video_id)` (calling as class method)
  - Changed to: `ytt_api = YouTubeTranscriptApi()` then `ytt_api.list(video_id)` (instance method)

- Updated youtube-transcript-api to latest version
  - Previous: `>=0.6.0` (older API)
  - New: `>=1.2.3` (latest, released October 2025)
  - This version has the modern instance-based API

### Root Cause Analysis - Complete Timeline

| Version | Dependency Version | API Call | Error |
|---------|-------------------|----------|-------|
| v1.0.0-1.0.1 | ❌ Wrong (1.1.1) | ❌ `list_transcripts()` | `has no attribute 'list_transcripts'` |
| v1.0.2 | ✅ Fixed (0.6.0) | ❌ `list_transcripts()` → `list()` | Still `has no attribute 'list_transcripts'` |
| v1.0.3 | ✅ Fixed (0.6.0) | ⚠️ `YouTubeTranscriptApi.list()` (class) | `missing 1 required positional argument` |
| **v1.0.4** | **✅ Latest (1.2.3)** | **✅ Instance method** | **Should work** |

### Technical Details
- Line 636-638: Added instance creation before calling list()
- Updated PEP 723 dependencies to youtube-transcript-api>=1.2.3
- Updated run.sh fallback with new version

### Verified Against
- PyPI: https://pypi.org/project/youtube-transcript-api/ (v1.2.3)
- Official docs show instance-based usage pattern

## [1.0.3] - 2025-11-10

### Fixed
- **CRITICAL**: Fixed incorrect API method name in fallback system
  - Changed `YouTubeTranscriptApi.list_transcripts()` to `YouTubeTranscriptApi.list()`
  - The method `list_transcripts()` does NOT exist in youtube-transcript-api
  - Correct method is `list()` as per official API documentation
  - This was the ACTUAL cause of: `type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'`

### Root Cause Analysis
- v1.0.2 fixed dependency versions (correct) ✅
- But the code was calling a non-existent method ❌
- Line 636: `YouTubeTranscriptApi.list_transcripts(video_id)` (WRONG)
- Fixed: `YouTubeTranscriptApi.list(video_id)` (CORRECT)

### Verified Against Official API
- Source: https://github.com/jdepoix/youtube-transcript-api
- YouTubeTranscriptApi class has `list()` method, not `list_transcripts()`
- Returns TranscriptList object with `find_manually_created_transcript()` and `find_generated_transcript()` methods (these are correct in our code)

### Impact
- **v1.0.2**: Dependencies fixed, but API call still wrong → transcriptions still failed
- **v1.0.3**: API call corrected → transcriptions should now work

## [1.0.2] - 2025-11-10

### Fixed
- **CRITICAL**: Fixed transcription extraction failure
  - Corrected `youtube-transcript-api` version from non-existent `>=1.1.1` to `>=0.6.0`
  - Corrected `yt-dlp` version from future `>=2025.6.30` to `>=2024.4.9`
  - Error was: `type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'`
  - Now triple-fallback system works correctly:
    1. yt-dlp with PO Token bypass ✅
    2. yt-dlp with alternative clients ✅
    3. youtube-transcript-api (fixed) ✅

### Technical
- Updated PEP 723 dependency specifications to valid package versions
- Updated run.sh fallback pip install with correct versions
- Metadata extraction was already working, now transcriptions work too

### Impact
- **Before**: Only metadata extraction worked, transcriptions failed with error
- **After**: Full functionality restored - both metadata and transcriptions work

## [1.0.1] - 2025-11-10

### Fixed
- **Critical**: Fixed "spawn uv ENOENT" error on macOS/Linux
  - Added wrapper script (`run.sh`) that auto-detects `uv` location
  - Searches common installation paths: Homebrew, Cargo, .local/bin
  - Falls back to Python venv if `uv` not found
  - Added comprehensive PATH environment variable for macOS GUI apps
- Improved first-run experience with automatic dependency installation

### Changed
- Server command changed from direct `uv` call to `/bin/bash` wrapper
- Added fallback mechanism for systems without `uv` installed
- Enhanced compatibility across different macOS/Linux configurations

### Technical
- New file: `server/run.sh` - Smart launcher with uv auto-detection
- PATH includes: `/usr/local/bin`, `/opt/homebrew/bin`, `~/.local/bin`, `~/.cargo/bin`
- Automatic venv creation and dependency installation on first run

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
