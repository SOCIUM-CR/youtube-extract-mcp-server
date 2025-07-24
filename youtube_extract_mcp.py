#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mcp>=1.0.0",
#     "yt-dlp>=2025.6.30",
#     "youtube-transcript-api>=1.1.1",
# ]
# ///
"""
YouTube Extract MCP Server - MLX Whisper Pattern
Auto-contained Python script with uv dependency management

Implements robust YouTube transcription extraction using:
- uv for automatic virtual environment management
- PEP 723 inline dependency metadata
- yt-dlp direct integration for reliable transcription extraction
- Single-file auto-contained MCP server

Based on the proven MLX Whisper Pattern for zero-configuration deployment.
"""

import asyncio
import json
import subprocess
import sys
import tempfile
import re
import glob
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# MCP imports
try:
    from mcp.server.models import InitializationOptions
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    import mcp.server.stdio
    MCP_AVAILABLE = True
except ImportError:
    # Fallback for testing without MCP
    print("Warning: MCP not available, running in test mode")
    types = None
    Server = None
    MCP_AVAILABLE = False
    
    # Mock types for testing
    class MockTextContent:
        def __init__(self, type, text):
            self.type = type
            self.text = text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[YouTubeExtractMCP] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeExtractMCP:
    """MLX Pattern MCP Server for YouTube transcript extraction"""
    
    def __init__(self):
        # Always initialize temp_dir
        self.temp_dir = Path(tempfile.gettempdir()) / "youtube-extract-mcp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Load global configuration
        self.config = self._load_global_config()
        self.output_directory = self.config.get("output_directory")
        
        if Server is None:
            logger.warning("MCP not available, running in test mode")
            return
            
        self.server = Server("youtube-extract-mlx")
        
        # Register tools
        self._register_tools()
        logger.info("🚀 YouTube Extract MCP Server initialized with MLX Pattern")
        
        # Log configuration status
        if self.output_directory:
            logger.info(f"📁 Global output directory configured: {self.output_directory}")

    def _get_config_file_path(self) -> Path:
        """Get the path to the global configuration file"""
        # Try environment variable first
        config_path = os.getenv("YOUTUBE_EXTRACT_CONFIG_PATH")
        if config_path:
            return Path(config_path)
        
        # Default to home directory
        home_dir = Path.home()
        return home_dir / ".youtube-extract-mcp-config.json"

    def _load_global_config(self) -> Dict[str, Any]:
        """Load global configuration from file or environment variables"""
        config = {}
        
        # Load from environment variables first
        env_output_dir = os.getenv("YOUTUBE_EXTRACT_OUTPUT_DIR")
        if env_output_dir:
            config["output_directory"] = Path(env_output_dir).expanduser().resolve()
        
        # Load from config file
        config_file = self._get_config_file_path()
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # File config overrides environment variables
                if "output_directory" in file_config:
                    config["output_directory"] = Path(file_config["output_directory"]).expanduser().resolve()
                
                # Merge other config options
                for key, value in file_config.items():
                    if key not in config:
                        config[key] = value
                        
                logger.info(f"📄 Loaded configuration from: {config_file}")
            except Exception as e:
                logger.warning(f"Error loading config file {config_file}: {e}")
        
        return config

    def _save_global_config(self, config: Dict[str, Any]) -> bool:
        """Save global configuration to file"""
        try:
            config_file = self._get_config_file_path()
            
            # Convert Path objects to strings for JSON serialization
            serializable_config = {}
            for key, value in config.items():
                if isinstance(value, Path):
                    serializable_config[key] = str(value)
                else:
                    serializable_config[key] = value
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Configuration saved to: {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            return False
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="youtube_extract_video",
                    description="Extract comprehensive YouTube video data: metadata + transcription with auto language detection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "YouTube video URL (supports various formats)"
                            },
                            "language": {
                                "type": "string", 
                                "description": "Preferred language for transcription (auto-detected if not specified)",
                                "default": "auto"
                            },
                            "include_timestamps": {
                                "type": "boolean",
                                "description": "Include timestamps in transcription output",
                                "default": True
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format: 'json' or 'text'",
                                "enum": ["json", "text"],
                                "default": "json"
                            },
                            "save_locally": {
                                "type": "boolean",
                                "description": "Save transcription to configured local directory",
                                "default": False
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="configure_output_directory",
                    description="Set the local directory where transcriptions will be saved (persists globally)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Absolute path to directory for saving transcriptions"
                            }
                        },
                        "required": ["directory_path"]
                    }
                ),
                types.Tool(
                    name="show_current_config",
                    description="Display current global configuration and settings",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="youtube_extract_playlist",
                    description="Extract transcriptions from an entire YouTube playlist with intelligent organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "playlist_url": {
                                "type": "string",
                                "description": "YouTube playlist URL to extract transcriptions from"
                            },
                            "max_videos": {
                                "type": "integer",
                                "description": "Maximum number of videos to process from playlist",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["playlist_url"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool execution"""
            logger.info(f"🔧 Executing tool: {name}")
            
            if name == "youtube_extract_video":
                return await self._extract_video(arguments)
            elif name == "configure_output_directory":
                return await self._configure_output_directory(arguments)
            elif name == "show_current_config":
                return await self._show_current_config(arguments)
            elif name == "youtube_extract_playlist":
                return await self._extract_playlist(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _extract_video(self, args: dict):
        """Extract video metadata and transcription using yt-dlp"""
        url = args.get("url", "")
        language = args.get("language", "auto")
        include_timestamps = args.get("include_timestamps", True)
        output_format = args.get("format", "json")
        save_locally = args.get("save_locally", False)
        
        if not url:
            raise ValueError("URL is required")
        
        logger.info(f"📺 Extracting video: {url}")
        
        try:
            # Extract video ID for validation
            video_id = self._extract_video_id(url)
            if not video_id:
                raise ValueError("Invalid YouTube URL format")
            
            # Extract metadata
            metadata = await self._extract_metadata(url)
            
            # Use detected original language if auto mode, otherwise use specified language
            detected_original = metadata.get("original_language", "es")
            
            if language == "auto":
                target_language = detected_original
                logger.info(f"🤖 Auto-detected original language: {detected_original}")
            else:
                target_language = language
                logger.info(f"👤 User-specified language: {target_language}")
            
            transcription = await self._extract_transcription(url, target_language, include_timestamps)
            
            # Combine results
            result = {
                "video_id": video_id,
                "url": url,
                "metadata": metadata,
                "transcription": transcription,
                "extraction_info": {
                    "language_requested": language,
                    "language_detected": metadata.get("original_language", "unknown"),
                    "language_extracted": transcription.get("language", "unknown"),
                    "language_used": target_language,
                    "has_timestamps": include_timestamps,
                    "method": transcription.get("source_method", "yt-dlp"),
                    "is_auto_generated": transcription.get("is_auto_generated"),
                    "segments_count": transcription.get("segments_count"),
                    "status": "success"
                }
            }
            
            # Save locally if requested and directory is configured
            if save_locally and self.output_directory:
                save_result = await self._save_transcription_locally(result)
                result["local_save"] = save_result
            
            if output_format == "text":
                # Return formatted text output
                output = self._format_as_text(result)
                if MCP_AVAILABLE:
                    return [types.TextContent(type="text", text=output)]
                else:
                    return [MockTextContent(type="text", text=output)]
            else:
                # Return JSON output
                json_output = json.dumps(result, indent=2, ensure_ascii=False)
                if MCP_AVAILABLE:
                    return [types.TextContent(type="text", text=json_output)]
                else:
                    return [MockTextContent(type="text", text=json_output)]
                
        except Exception as e:
            error_msg = f"❌ Error extracting video {url}: {str(e)}"
            logger.error(error_msg)
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=error_msg)]
            else:
                return [MockTextContent(type="text", text=error_msg)]

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _detect_original_language(self, metadata: Dict[str, Any]) -> str:
        """Detect original language from auto-generated captions (most reliable source)"""
        
        logger.info("🔍 Detecting original language from auto-generated captions...")
        
        # 1. Direct language field from yt-dlp (if available and reliable)
        if "language" in metadata and metadata["language"]:
            raw_lang = metadata["language"]
            # Normalize language codes (en-US -> en, es-ES -> es, etc.)
            normalized_lang = self._normalize_language_code(raw_lang)
            logger.info(f"  📝 Direct language field: {raw_lang} → normalized: {normalized_lang}")
            return normalized_lang
        
        # 2. Find auto-generated captions (THE MOST RELIABLE SOURCE)
        if "automatic_captions" in metadata:
            auto_captions = metadata["automatic_captions"]
            if auto_captions and isinstance(auto_captions, dict):
                available_langs = list(auto_captions.keys())
                logger.info(f"  🤖 Available auto-generated captions: {available_langs}")
                
                # Auto-generated captions are always in the original language of the video
                # Use the first available auto-generated caption language
                if available_langs:
                    original_lang = available_langs[0]
                    normalized_lang = self._normalize_language_code(original_lang)
                    logger.info(f"  ✅ Original language from auto-generated captions: {original_lang} → normalized: {normalized_lang}")
                    return normalized_lang
        
        # 3. Fallback to manual subtitles (less reliable, could be translations)
        if "subtitles" in metadata:
            subtitles = metadata["subtitles"]
            if subtitles and isinstance(subtitles, dict):
                available_langs = list(subtitles.keys())
                logger.info(f"  📖 Available manual subtitles: {available_langs}")
                
                # Use first available manual subtitle as fallback
                if available_langs:
                    fallback_lang = available_langs[0]
                    normalized_lang = self._normalize_language_code(fallback_lang)
                    logger.info(f"  ⚠️  Using manual subtitle as fallback: {fallback_lang} → normalized: {normalized_lang}")
                    return normalized_lang
        
        # 4. Final fallback - default to English as most universal
        logger.info("  ⚠️  No captions found, defaulting to English")
        return "en"
    
    def _normalize_language_code(self, lang_code: str) -> str:
        """Normalize language codes to base language (en-US -> en, es-ES -> es)"""
        if not lang_code:
            return "en"
        
        # Extract base language code (first part before hyphen or underscore)
        base_lang = lang_code.split('-')[0].split('_')[0].lower()
        return base_lang

    async def _extract_metadata(self, url: str) -> Dict[str, Any]:
        """Extract video metadata using yt-dlp"""
        try:
            cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--dump-json',
                '--no-download',
                url
            ]
            
            logger.info("📊 Extracting metadata with yt-dlp")
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise RuntimeError(f"yt-dlp metadata extraction failed: {stderr.decode()}")
            
            metadata = json.loads(stdout.decode())
            
            # Extract key fields including original language
            original_language = self._detect_original_language(metadata)
            
            return {
                "title": metadata.get("title", "Unknown Title"),
                "description": metadata.get("description", ""),
                "duration": metadata.get("duration"),
                "view_count": metadata.get("view_count"),
                "like_count": metadata.get("like_count"),
                "channel": metadata.get("channel", ""),
                "upload_date": metadata.get("upload_date"),
                "categories": metadata.get("categories", []),
                "tags": metadata.get("tags", []),
                "thumbnail": metadata.get("thumbnail"),
                "webpage_url": metadata.get("webpage_url", url),
                "original_language": original_language,
                "detected_from": "yt-dlp metadata analysis"
            }
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {
                "title": "Metadata extraction failed",
                "error": str(e)
            }

    async def _extract_transcription(self, url: str, language: str, include_timestamps: bool) -> Dict[str, Any]:
        """Extract transcription using yt-dlp with language fallback"""
        temp_output_dir = self.temp_dir / f"extract_{self._extract_video_id(url)}"
        temp_output_dir.mkdir(exist_ok=True)
        
        try:
            # Language priority: prioritize the detected/requested language first
            if language in ["es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh", "ru"]:
                # For recognized languages, prioritize requested, then common fallbacks
                if language == "es":
                    language_options = ["es", "en"]
                elif language == "en":
                    language_options = ["en", "es"]
                else:
                    # For other languages, try requested first, then English and Spanish
                    language_options = [language, "en", "es"]
            else:
                # For unrecognized/auto cases, use Spanish and English as fallbacks
                language_options = ["es", "en"]
            
            language_options = list(dict.fromkeys(language_options))  # Remove duplicates
            
            logger.info(f"🌐 Language priority order: {language_options} (requested: {language})")
            
            cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--write-auto-sub',
                '--write-sub',
                '--skip-download',
                '--sub-lang', ','.join(language_options),
                '--extractor-args', 'youtube:formats=missing_pot',  # Bypass PO Token
                '--extractor-args', 'youtube:player_client=web,web_safari',  # Múltiples clientes
                '--output', str(temp_output_dir / '%(title)s.%(ext)s'),
                url
            ]
            
            logger.info(f"📝 Extracting transcription (languages: {language_options})")
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            # Check if yt-dlp succeeded or try alternatives
            yt_dlp_success = result.returncode == 0
            
            if not yt_dlp_success:
                stderr_text = stderr.decode()
                
                # Check for PO Token errors specifically and try alternative config
                if 'po_token' in stderr_text.lower() or 'missing_pot' in stderr_text.lower():
                    logger.warning(f"⚠️ PO Token error detected: {stderr_text[:200]}...")
                    logger.info("🔄 Trying alternative yt-dlp configuration...")
                    
                    # Try alternative configuration with different clients
                    cmd_alt = [
                        sys.executable, '-m', 'yt_dlp',
                        '--write-auto-sub',
                        '--write-sub',
                        '--skip-download',
                        '--sub-lang', ','.join(language_options),
                        '--extractor-args', 'youtube:formats=missing_pot',
                        '--extractor-args', 'youtube:player_client=android,web_embedded',
                        '--output', str(temp_output_dir / '%(title)s.%(ext)s'),
                        url
                    ]
                    
                    try:
                        result_alt = await asyncio.create_subprocess_exec(
                            *cmd_alt,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        
                        stdout_alt, stderr_alt = await result_alt.communicate()
                        
                        if result_alt.returncode == 0:
                            logger.info("✅ Alternative yt-dlp configuration succeeded!")
                            yt_dlp_success = True
                        else:
                            logger.warning(f"⚠️ Alternative yt-dlp config also failed: {stderr_alt.decode()[:200]}...")
                    except Exception as alt_e:
                        logger.warning(f"⚠️ Alternative yt-dlp config error: {alt_e}")
                
                # If both primary and alternative yt-dlp failed, use fallback
                if not yt_dlp_success:
                    logger.warning(f"⚠️ All yt-dlp methods failed: {stderr_text[:200]}...")
                    logger.info("🔄 Attempting fallback with youtube-transcript-api...")
                    return await self._extract_transcription_fallback(url, language, include_timestamps)
            
            # Find and process VTT files
            vtt_files = list(temp_output_dir.glob("*.vtt"))
            
            if not vtt_files:
                logger.warning("⚠️ No VTT files found from yt-dlp")
                logger.info("🔄 Attempting fallback with youtube-transcript-api...")
                return await self._extract_transcription_fallback(url, language, include_timestamps)
            
            # Select best VTT file based on language priority and original language detection
            vtt_file = self._select_best_vtt_file(vtt_files, language_options)
            
            # Validate selection and apply intelligent fallback if needed
            selected_file_lang = self._detect_language_from_filename(vtt_file.name, language_options)
            expected_lang = language_options[0] if language_options else "unknown"
            
            # Check if selection matches expectations
            if selected_file_lang != expected_lang and len(vtt_files) > 1:
                logger.warning(f"⚠️  Selected file language ({selected_file_lang}) differs from expected ({expected_lang})")
                
                # Try to find a better match if available
                alternative_file = self._find_alternative_vtt_file(vtt_files, expected_lang, vtt_file)
                if alternative_file:
                    logger.info(f"🔄 Switching to alternative file: {alternative_file.name}")
                    vtt_file = alternative_file
                    selected_file_lang = self._detect_language_from_filename(vtt_file.name, language_options)
            
            plain_text, timestamped_text = self._process_vtt_file_dual(vtt_file)
            
            # Final validation: check if content seems to match expected language
            content_validation = self._validate_content_language(plain_text[:500], expected_lang)
            if not content_validation["matches"] and content_validation["confidence"] > 0.7:
                logger.warning(f"⚠️  Content language validation failed: expected {expected_lang}, "
                             f"detected {content_validation['detected']} (confidence: {content_validation['confidence']:.2f})")
            
            # Determine actual language from filename
            detected_language = selected_file_lang
            
            # Create comprehensive language availability info for JSON optimization
            available_languages = self._extract_available_languages(vtt_files)
            
            return {
                "text": timestamped_text if include_timestamps else plain_text,
                "plain_text": plain_text,
                "timestamped_text": timestamped_text,
                "language": detected_language,
                "status": "success",
                "source_method": "yt-dlp",
                "source_file": vtt_file.name,
                "available_files": [f.name for f in vtt_files],
                "available_languages": available_languages
            }
            
        except Exception as e:
            logger.warning(f"yt-dlp transcription extraction failed: {e}")
            logger.info("🔄 Attempting fallback with youtube-transcript-api...")
            
            # Try fallback method before giving up
            fallback_result = await self._extract_transcription_fallback(url, language, include_timestamps)
            
            # If fallback also fails, return original error with fallback info
            if fallback_result.get("status") == "fallback_failed":
                return {
                    "text": "",
                    "language": "error",
                    "status": "both_methods_failed",
                    "primary_error": str(e),
                    "fallback_error": fallback_result.get("error", "Unknown fallback error")
                }
            
            # Fallback succeeded, return its result
            return fallback_result
        finally:
            # Cleanup temp files
            try:
                import shutil
                shutil.rmtree(temp_output_dir, ignore_errors=True)
            except:
                pass

    async def _extract_transcription_fallback(self, url: str, language: str, include_timestamps: bool) -> Dict[str, Any]:
        """Extract transcription using youtube-transcript-api as fallback method"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            video_id = self._extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
            
            logger.info(f"🔄 Trying fallback method: youtube-transcript-api for video {video_id}")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Language priority similar to main method
            if language in ["es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh", "ru"]:
                if language == "es":
                    language_codes = ['es', 'es-ES', 'en', 'en-US']
                elif language == "en":
                    language_codes = ['en', 'en-US', 'es', 'es-ES']
                else:
                    language_codes = [language, f'{language}-{language.upper()}', 'en', 'es']
            else:
                language_codes = ['es', 'es-ES', 'en', 'en-US']
            
            selected_transcript = None
            used_language = "unknown"
            is_auto_generated = False
            
            # Priority: Manual transcripts first
            for lang_code in language_codes:
                try:
                    transcript = transcript_list.find_manually_created_transcript([lang_code])
                    selected_transcript = transcript.fetch()
                    used_language = transcript.language_code
                    is_auto_generated = False
                    logger.info(f"✅ Found manual transcript: {used_language}")
                    break
                except:
                    continue
            
            # Fallback: Auto-generated transcripts
            if not selected_transcript:
                for lang_code in language_codes:
                    try:
                        transcript = transcript_list.find_generated_transcript([lang_code])
                        selected_transcript = transcript.fetch()
                        used_language = transcript.language_code
                        is_auto_generated = True
                        logger.info(f"✅ Found auto-generated transcript: {used_language}")
                        break
                    except:
                        continue
            
            if not selected_transcript:
                return {
                    "text": "",
                    "language": "none",
                    "status": "no_transcription_available",
                    "message": "No transcripts found with youtube-transcript-api"
                }
            
            # Process transcript segments
            segments = []
            for segment in selected_transcript:
                # youtube-transcript-api returns dictionaries, access directly
                try:
                    start_time = segment.get('start', 0) if hasattr(segment, 'get') else segment['start']
                    text = segment.get('text', '').strip() if hasattr(segment, 'get') else segment['text'].strip()
                except (KeyError, TypeError):
                    # Fallback for different object types
                    start_time = getattr(segment, 'start', 0)
                    text = getattr(segment, 'text', '').strip()
                
                # Convert start time to MM:SS format
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                formatted_timestamp = f"{minutes:02d}:{seconds:02d}"
                
                if text:
                    segments.append({
                        'timestamp': formatted_timestamp,
                        'text': text,
                        'seconds': start_time
                    })
            
            # Generate both formats
            plain_text = ' '.join([seg['text'] for seg in segments])
            timestamped_text = '\n'.join([f"[{seg['timestamp']}] {seg['text']}" for seg in segments])
            
            # Normalize language code
            normalized_lang = self._normalize_language_code(used_language)
            
            return {
                "text": timestamped_text if include_timestamps else plain_text,
                "plain_text": plain_text,
                "timestamped_text": timestamped_text,
                "language": normalized_lang,
                "status": "success",
                "source_method": "youtube-transcript-api",
                "is_auto_generated": is_auto_generated,
                "original_language_code": used_language,
                "segments_count": len(segments)
            }
            
        except Exception as e:
            logger.warning(f"Fallback method failed: {e}")
            return {
                "text": "",
                "language": "error",
                "status": "fallback_failed",
                "error": str(e)
            }

    def _process_vtt_file_dual(self, vtt_file: Path) -> tuple[str, str]:
        """Process VTT file to extract both plain and timestamped versions"""
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            segments = []  # Lista de segmentos con timestamp y texto
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip VTT headers and empty lines
                if (line.startswith('WEBVTT') or 
                    line.startswith('NOTE') or 
                    line.startswith('Kind:') or 
                    line.startswith('Language:') or
                    not line):
                    i += 1
                    continue
                
                # Check if line is a timestamp (formato: 00:00:00.000 --> 00:00:03.000)
                if '-->' in line:
                    timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                    if timestamp_match:
                        start_time = timestamp_match.group(1)
                        
                        # Convertir timestamp a formato MM:SS
                        time_parts = start_time.split(':')
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1]) + (hours * 60)
                        seconds = int(float(time_parts[2]))
                        formatted_timestamp = f"{minutes:02d}:{seconds:02d}"
                        
                        # Leer las líneas de texto siguientes
                        i += 1
                        text_lines = []
                        text_set = set()  # Para evitar duplicados dentro del mismo segmento
                        
                        while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                            text_line = lines[i].strip()
                            if text_line:
                                clean_line = self._clean_transcript_line(text_line)
                                # Solo agregar si no es duplicado en este segmento
                                if clean_line and clean_line not in text_set:
                                    text_lines.append(clean_line)
                                    text_set.add(clean_line)
                            i += 1
                        
                        # Unir texto del segmento
                        if text_lines:
                            segment_text = ' '.join(text_lines)
                            segments.append({
                                'timestamp': formatted_timestamp,
                                'text': segment_text.strip(),
                                'seconds': minutes * 60 + seconds
                            })
                        continue
                    
                i += 1
            
            # Post-procesar segmentos para fusionar duplicados consecutivos
            merged_segments = []
            
            for segment in segments:
                text = segment['text']
                
                if not merged_segments:
                    # Primer segmento
                    merged_segments.append(segment)
                else:
                    last_segment = merged_segments[-1]
                    last_text = last_segment['text']
                    
                    # Calcular diferencia de tiempo entre segmentos
                    time_diff = abs(segment['seconds'] - last_segment['seconds'])
                    
                    # Detectar duplicados exactos
                    if text == last_text:
                        # Es exactamente el mismo texto, omitir
                        continue
                    
                    # Detectar si uno contiene al otro (extensión de texto)
                    elif text in last_text or last_text in text:
                        # Mantener el texto más largo
                        if len(text) > len(last_text):
                            last_segment['text'] = text
                        # Si no es más largo, no hacer nada (mantener el anterior)
                        continue
                    
                    # Detectar si el texto actual empieza con el anterior (continuación directa)
                    elif text.startswith(last_text) and time_diff <= 3:
                        # Es una continuación, tomar el texto más completo
                        last_segment['text'] = text
                        continue
                    
                    # Detectar si el anterior empieza con el actual (orden inverso)
                    elif last_text.startswith(text) and time_diff <= 3:
                        # El anterior ya es más completo, mantenerlo
                        continue
                    
                    # Detectar continuaciones por palabras comunes al final/inicio
                    last_words = last_text.split()[-3:] if last_text else []
                    current_words = text.split()[:3] if text else []
                    
                    # Si hay overlap de palabras y tiempo cercano, puede ser continuación
                    if (len(last_words) >= 2 and len(current_words) >= 2 and 
                        any(word in current_words for word in last_words) and 
                        time_diff <= 5):
                        
                        # Fusionar inteligentemente evitando repetición
                        if not last_text.endswith(text) and text not in last_text:
                            # Encontrar punto de fusión común
                            combined = last_text
                            for word in text.split():
                                if word not in combined.split()[-5:]:  # Evitar repetir últimas 5 palabras
                                    combined += " " + word
                            last_segment['text'] = combined.strip()
                        continue
                    
                    # Si llegamos aquí, es un segmento diferente
                    merged_segments.append(segment)
            
            # Generar outputs finales
            plain_parts = [seg['text'] for seg in merged_segments]
            timestamped_parts = [f"[{seg['timestamp']}] {seg['text']}" for seg in merged_segments]
            
            plain_text = ' '.join(plain_parts).strip()
            timestamped_text = '\n'.join(timestamped_parts).strip()
            
            return plain_text, timestamped_text
            
        except Exception as e:
            logger.error(f"Error processing VTT file: {e}")
            error_msg = f"Error processing transcription: {e}"
            return error_msg, error_msg

    def _process_vtt_file(self, vtt_file: Path, include_timestamps: bool) -> str:
        """Process VTT file to extract text (legacy method for compatibility)"""
        plain_text, timestamped_text = self._process_vtt_file_dual(vtt_file)
        return timestamped_text if include_timestamps else plain_text

    def _clean_transcript_line(self, line: str) -> str:
        """Clean transcript line removing HTML tags and artifacts"""
        # Remove HTML tags
        line = re.sub(r'<[^>]+>', '', line)
        
        # Remove common VTT artifacts
        line = re.sub(r'&lt;.*?&gt;', '', line)
        line = re.sub(r'&amp;', '&', line)
        line = re.sub(r'&quot;', '"', line)
        
        # Remove extra whitespace
        line = ' '.join(line.split())
        
        return line.strip()

    def _select_best_vtt_file(self, vtt_files: List[Path], language_options: List[str]) -> Path:
        """Select the best VTT file prioritizing auto-generated files in the detected language"""
        if not vtt_files:
            raise ValueError("No VTT files available")
        
        if len(vtt_files) == 1:
            logger.info(f"🎯 Only one VTT file available: {vtt_files[0].name}")
            return vtt_files[0]
        
        # Log available files for debugging
        logger.info(f"🔍 Available VTT files ({len(vtt_files)}):")
        for vtt_file in vtt_files:
            is_auto = self._is_auto_generated_vtt(vtt_file.name)
            detected_lang = self._detect_language_from_filename(vtt_file.name, language_options)
            logger.info(f"  • {vtt_file.name} (lang: {detected_lang}, auto: {is_auto})")
        
        # Priority: Auto-generated files in the detected language (most reliable)
        target_lang = language_options[0] if language_options else None
        logger.info(f"🎯 Looking for auto-generated file in language: {target_lang}")
        
        for vtt_file in vtt_files:
            is_auto = self._is_auto_generated_vtt(vtt_file.name)
            detected_lang = self._detect_language_from_filename(vtt_file.name, language_options)
            
            if is_auto and detected_lang == target_lang:
                logger.info(f"✅ Found auto-generated file in target language: {vtt_file.name}")
                return vtt_file
        
        # Fallback 1: Any auto-generated file in target language (even if not perfectly detected)
        for vtt_file in vtt_files:
            is_auto = self._is_auto_generated_vtt(vtt_file.name)
            if is_auto and target_lang and f'.{target_lang}.' in vtt_file.name.lower():
                logger.info(f"✅ Found auto-generated file with target language pattern: {vtt_file.name}")
                return vtt_file
        
        # Fallback 2: Any file in target language (manual subtitles) - STRICT MATCH
        for vtt_file in vtt_files:
            detected_lang = self._detect_language_from_filename(vtt_file.name, language_options)
            if detected_lang == target_lang:
                logger.info(f"⚠️  Using manual subtitle in target language: {vtt_file.name}")
                return vtt_file
            # Also check for exact language code in filename
            if target_lang and f'.{target_lang}.' in vtt_file.name.lower():
                logger.info(f"⚠️  Using manual subtitle with target language pattern: {vtt_file.name}")
                return vtt_file
        
        # Fallback 3: First auto-generated file (any language)
        for vtt_file in vtt_files:
            is_auto = self._is_auto_generated_vtt(vtt_file.name)
            if is_auto:
                detected_lang = self._detect_language_from_filename(vtt_file.name, language_options)
                logger.info(f"⚠️  Using first auto-generated file: {vtt_file.name} (lang: {detected_lang})")
                return vtt_file
        
        # Final fallback: First available file
        selected = vtt_files[0]
        detected_lang = self._detect_language_from_filename(selected.name, language_options)
        logger.warning(f"⚠️  Using first available file as last resort: {selected.name} (lang: {detected_lang})")
        return selected
    
    def _is_auto_generated_vtt(self, filename: str) -> bool:
        """Check if a VTT file is auto-generated by YouTube"""
        filename_lower = filename.lower()
        
        # Common patterns for auto-generated files
        auto_patterns = [
            'auto',           # Most common pattern
            'generated',      # Alternative pattern  
            'automatic',      # Full word
            '.a.',           # Sometimes abbreviated as .a.
        ]
        
        return any(pattern in filename_lower for pattern in auto_patterns)

    def _find_alternative_vtt_file(self, vtt_files: List[Path], target_lang: str, current_file: Path) -> Optional[Path]:
        """Find an alternative VTT file that better matches the target language"""
        for vtt_file in vtt_files:
            if vtt_file == current_file:
                continue
            
            detected_lang = self._detect_language_from_filename(vtt_file.name, [target_lang])
            if detected_lang == target_lang:
                logger.info(f"🔍 Found alternative file with correct language: {vtt_file.name}")
                return vtt_file
        
        return None

    def _validate_content_language(self, sample_text: str, expected_lang: str) -> Dict[str, Any]:
        """Validate if the content text matches the expected language"""
        if not sample_text or len(sample_text) < 50:
            return {"matches": True, "confidence": 0.0, "detected": "unknown", "reason": "insufficient_text"}
        
        text_lower = sample_text.lower()
        
        # Spanish indicators
        spanish_indicators = [
            "es", "está", "son", "con", "por", "para", "una", "los", "las", "que", "cómo", "qué",
            "muy", "más", "todo", "como", "hacer", "este", "esta", "pueden", "tiene", "ser"
        ]
        spanish_score = sum(1 for word in spanish_indicators if word in text_lower)
        
        # English indicators
        english_indicators = [
            "the", "and", "this", "that", "with", "for", "you", "your", "are", "is", "can",
            "will", "have", "has", "they", "them", "what", "how", "very", "more", "all"
        ]
        english_score = sum(1 for word in english_indicators if word in text_lower)
        
        # Special characters check
        if any(char in text_lower for char in ['ñ', 'á', 'é', 'í', 'ó', 'ú', '¿', '¡']):
            spanish_score += 3
        
        total_score = spanish_score + english_score
        if total_score == 0:
            return {"matches": True, "confidence": 0.0, "detected": "unknown", "reason": "no_indicators"}
        
        spanish_confidence = spanish_score / total_score
        english_confidence = english_score / total_score
        
        if spanish_confidence > english_confidence:
            detected = "es"
            confidence = spanish_confidence
        else:
            detected = "en"
            confidence = english_confidence
        
        matches = detected == expected_lang
        
        return {
            "matches": matches,
            "confidence": confidence,
            "detected": detected,
            "spanish_score": spanish_score,
            "english_score": english_score
        }

    def _detect_language_from_filename(self, filename: str, preferred_languages: List[str]) -> str:
        """Detect language from VTT filename with normalized language codes"""
        filename_lower = filename.lower()
        
        # Check for exact language codes in preferred order
        for lang in preferred_languages:
            if f'.{lang}.' in filename_lower:
                return lang
        
        # Extended language patterns including common variations
        language_patterns = {
            'es': ['.es.', '.es-', '.spanish.', '.español.', '.spa.'],
            'en': ['.en.', '.en-', '.english.', '.eng.'],
            'fr': ['.fr.', '.fr-', '.french.', '.français.', '.fra.'],
            'de': ['.de.', '.de-', '.german.', '.deutsch.', '.ger.'],
            'it': ['.it.', '.it-', '.italian.', '.italiano.', '.ita.'],
            'pt': ['.pt.', '.pt-', '.portuguese.', '.português.', '.por.'],
            'ja': ['.ja.', '.ja-', '.japanese.', '.日本語.', '.jpn.'],
            'ko': ['.ko.', '.ko-', '.korean.', '.한국어.', '.kor.'],
            'zh': ['.zh.', '.zh-', '.chinese.', '.中文.', '.chi.'],
            'ru': ['.ru.', '.ru-', '.russian.', '.русский.', '.rus.']
        }
        
        # Check patterns and normalize to base language
        for lang, patterns in language_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                return lang
        
        # Final attempt: extract any language-like pattern and normalize
        import re
        lang_match = re.search(r'\.([a-z]{2})[-\.]', filename_lower)
        if lang_match:
            detected = lang_match.group(1)
            # Normalize if it's a known language
            if detected in language_patterns:
                return detected
        
        return "unknown"

    def _extract_available_languages(self, vtt_files: List[Path]) -> Dict[str, Any]:
        """Extract information about all available languages from VTT files"""
        available_languages = {}
        
        for vtt_file in vtt_files:
            filename = vtt_file.name.lower()
            
            # Extract language from filename
            detected_lang = "unknown"
            
            # Try common patterns
            language_patterns = {
                'es': ['.es.', '.spanish.', '.español.'],
                'en': ['.en.', '.english.'],
                'fr': ['.fr.', '.french.', '.français.'],
                'de': ['.de.', '.german.', '.deutsch.'],
                'it': ['.it.', '.italian.', '.italiano.'],
                'pt': ['.pt.', '.portuguese.', '.português.'],
                'ja': ['.ja.', '.japanese.', '.日本語.'],
                'ko': ['.ko.', '.korean.', '.한국어.'],
                'zh': ['.zh.', '.chinese.', '.中文.'],
                'ru': ['.ru.', '.russian.', '.русский.'],
                'ar': ['.ar.', '.arabic.', '.العربية.']
            }
            
            for lang, patterns in language_patterns.items():
                if any(pattern in filename for pattern in patterns):
                    detected_lang = lang
                    break
            
            # Determine if auto-generated or manual
            is_auto = 'auto' in filename or 'generated' in filename
            
            # Store language info
            if detected_lang not in available_languages:
                available_languages[detected_lang] = {
                    "language_code": detected_lang,
                    "filename": vtt_file.name,
                    "auto_generated": is_auto,
                    "available": True
                }
        
        return {
            "total_languages": len(available_languages),
            "languages": available_languages,
            "language_codes": list(available_languages.keys())
        }

    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """Format extraction result as readable text"""
        metadata = result.get("metadata", {})
        transcription = result.get("transcription", {})
        
        output = []
        output.append(f"📺 **{metadata.get('title', 'Unknown Title')}**")
        output.append(f"🔗 URL: {result.get('url', '')}")
        output.append(f"📺 Canal: {metadata.get('channel', 'Unknown')}")
        
        if metadata.get('duration'):
            duration = metadata['duration']
            minutes = duration // 60
            seconds = duration % 60
            output.append(f"⏱️ Duración: {minutes}:{seconds:02d}")
        
        output.append(f"👀 Vistas: {metadata.get('view_count', 'Unknown')}")
        output.append(f"🗣️ Idioma: {transcription.get('language', 'Unknown')}")
        output.append("")
        
        # Add transcription
        transcription_text = transcription.get('text', '')
        if transcription_text:
            output.append("📝 **Transcripción:**")
            output.append("")
            output.append(transcription_text)
        else:
            output.append("❌ No se pudo extraer la transcripción")
        
        return '\n'.join(output)

    async def _configure_output_directory(self, args: dict):
        """Configure the output directory for local transcription storage"""
        directory_path = args.get("directory_path", "")
        
        if not directory_path:
            error_msg = "❌ Directory path is required"
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=error_msg)]
            else:
                return [MockTextContent(type="text", text=error_msg)]
        
        try:
            output_dir = Path(directory_path).expanduser().resolve()
            
            # Create directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = output_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            # Update both instance and global config
            self.output_directory = output_dir
            self.config["output_directory"] = output_dir
            
            # Save to global configuration
            config_saved = self._save_global_config(self.config)
            
            success_msg = (f"✅ Output directory configured successfully:\n📁 {output_dir}\n\n"
                          f"Transcriptions will be saved with this structure:\n"
                          f"{output_dir}/{{channel_name}}/{{title}}_{{YYYYMMDD}}_{{video_id}}/\n"
                          f"├── transcript_plain.txt\n"
                          f"├── transcript_timestamps.txt\n"
                          f"└── metadata.json\n\n"
                          f"📝 New naming: Title comes first, includes download date\n"
                          f"{'💾 Configuration saved globally - will persist across sessions' if config_saved else '⚠️ Could not save global configuration'}")
            
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=success_msg)]
            else:
                return [MockTextContent(type="text", text=success_msg)]
            
        except PermissionError:
            error_msg = f"❌ Permission denied: Cannot write to {directory_path}"
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=error_msg)]
            else:
                return [MockTextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"❌ Error configuring directory: {str(e)}"
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=error_msg)]
            else:
                return [MockTextContent(type="text", text=error_msg)]

    async def _show_current_config(self, args: dict):
        """Display current global configuration and settings"""
        try:
            config_file = self._get_config_file_path()
            
            config_info = [
                "🔧 **YouTube Extract MCP - Current Configuration**",
                "",
                f"📁 **Output Directory**: {self.output_directory if self.output_directory else 'Not configured'}",
                f"📄 **Config File**: {config_file}",
                f"📂 **Config File Exists**: {'✅ Yes' if config_file.exists() else '❌ No'}",
                "",
                "🌍 **Environment Variables**:",
                f"  • YOUTUBE_EXTRACT_OUTPUT_DIR: {os.getenv('YOUTUBE_EXTRACT_OUTPUT_DIR', 'Not set')}",
                f"  • YOUTUBE_EXTRACT_CONFIG_PATH: {os.getenv('YOUTUBE_EXTRACT_CONFIG_PATH', 'Not set')}",
                "",
                "⚙️ **Current Settings**:",
                f"  • Global config loaded: {'✅ Yes' if self.config else '❌ No'}",
                f"  • Auto-save enabled: ✅ Yes" if self.output_directory else f"  • Auto-save enabled: ❌ No (configure directory first)",
                "",
                "📝 **File Naming Pattern**:",
                "  • Structure: {channel_name}/{title}_{YYYYMMDD}_{video_id}/",
                "  • Files: transcript_plain.txt, transcript_timestamps.txt, metadata.json",
                "",
                "🔄 **Next Steps**:",
                "  • Use `configure_output_directory` to set/change output directory",
                "  • Use `youtube_extract_video` with `save_locally=true` to save files",
                "  • Configuration persists globally across sessions"
            ]
            
            config_text = "\n".join(config_info)
            
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=config_text)]
            else:
                return [MockTextContent(type="text", text=config_text)]
                
        except Exception as e:
            error_msg = f"❌ Error displaying configuration: {str(e)}"
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=error_msg)]
            else:
                return [MockTextContent(type="text", text=error_msg)]

    async def _extract_playlist(self, args: dict):
        """Extract playlist using external PlaylistProcessor module"""
        playlist_url = args.get("playlist_url", "")
        max_videos = args.get("max_videos", 50)
        
        if not playlist_url:
            raise ValueError("Playlist URL is required")
        
        logger.info(f"📋 Processing playlist: {playlist_url} (max {max_videos} videos)")
        
        try:
            # Import PlaylistProcessor module
            from playlist_processor import PlaylistProcessor
            
            # Create processor with current output directory
            processor = PlaylistProcessor(self.output_directory)
            
            # Process playlist
            result = await processor.process_playlist(playlist_url, max_videos)
            
            # Return MCP-compatible response
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=item["text"]) for item in result]
            else:
                return [MockTextContent(type="text", text=item["text"]) for item in result]
                
        except ImportError as e:
            error_msg = f"❌ PlaylistProcessor module not available: {str(e)}"
            logger.error(error_msg)
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=error_msg)]
            else:
                return [MockTextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"❌ Error processing playlist: {str(e)}"
            logger.error(error_msg)
            if MCP_AVAILABLE:
                return [types.TextContent(type="text", text=error_msg)]
            else:
                return [MockTextContent(type="text", text=error_msg)]

    async def _save_transcription_locally(self, result: dict) -> dict:
        """Save transcription and metadata to local directory structure"""
        try:
            metadata = result["metadata"]
            transcription = result["transcription"]
            video_id = result["video_id"]
            
            # Clean title for filename (title first, more descriptive)
            title = metadata.get("title", "Unknown_Title")
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:80]  # Increased length
            
            # Get current date for filename
            from datetime import datetime
            download_date = datetime.now().strftime("%Y%m%d")
            
            # Create channel directory
            channel_name = metadata.get("channel", "Unknown_Channel")
            clean_channel = re.sub(r'[<>:"/\\|?*]', '_', channel_name)
            
            # Improved directory naming: Title_first_YYYYMMDD_VideoID
            video_dir_name = f"{clean_title}_{download_date}_{video_id}"
            video_dir = self.output_directory / clean_channel / video_dir_name
            video_dir.mkdir(parents=True, exist_ok=True)
            
            # Save both versions using the correctly processed text
            plain_file = video_dir / "transcript_plain.txt"
            plain_text = transcription.get("plain_text", "")
            if not plain_text:  # Fallback for older extractions
                plain_text = self._extract_plain_text(transcription.get("text", ""))
            plain_file.write_text(plain_text, encoding="utf-8")
            
            # Save timestamped transcription 
            timestamps_file = video_dir / "transcript_timestamps.txt"
            timestamped_text = transcription.get("timestamped_text", "")
            if not timestamped_text:  # Fallback for older extractions
                timestamped_text = transcription.get("text", "")
            timestamps_file.write_text(timestamped_text, encoding="utf-8")
            
            # Create optimized metadata for JSON (without full transcription text)
            optimized_metadata = self._create_optimized_metadata(result)
            
            # Save optimized metadata as JSON
            metadata_file = video_dir / "metadata.json"
            metadata_file.write_text(
                json.dumps(optimized_metadata, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            
            return {
                "status": "success",
                "directory": str(video_dir),
                "files_created": [
                    str(plain_file.name),
                    str(timestamps_file.name),
                    str(metadata_file.name)
                ]
            }
            
        except Exception as e:
            logger.error(f"Error saving locally: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _create_optimized_metadata(self, result: dict) -> dict:
        """Create optimized metadata JSON without full transcription text"""
        transcription = result.get("transcription", {})
        
        # Create summary information instead of full text
        plain_text = transcription.get("plain_text", "")
        timestamped_text = transcription.get("timestamped_text", "")
        
        # Calculate text statistics
        word_count = len(plain_text.split()) if plain_text else 0
        char_count = len(plain_text) if plain_text else 0
        estimated_reading_time = max(1, word_count // 200)  # ~200 words per minute
        
        optimized_result = {
            "video_id": result.get("video_id"),
            "url": result.get("url"),
            "metadata": result.get("metadata", {}),
            "transcription_summary": {
                "language": transcription.get("language", "unknown"),
                "status": transcription.get("status", "unknown"),
                "source_file": transcription.get("source_file", ""),
                "word_count": word_count,
                "character_count": char_count,
                "estimated_reading_time_minutes": estimated_reading_time,
                "has_timestamps": bool(timestamped_text and timestamped_text != plain_text),
                "available_languages": transcription.get("available_languages", {}),
                "files_created": {
                    "plain_text": "transcript_plain.txt",
                    "timestamped_text": "transcript_timestamps.txt",
                    "metadata": "metadata.json"
                }
            },
            "extraction_info": result.get("extraction_info", {}),
            "generated_at": self._get_current_timestamp()
        }
        
        # Add local save info if present
        if "local_save" in result:
            optimized_result["local_save"] = result["local_save"]
        
        return optimized_result
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _extract_plain_text(self, text_with_timestamps: str) -> str:
        """Extract plain text removing timestamp markers"""
        # Remove timestamp patterns like [00:01:23.456]
        plain_text = re.sub(r'\[?\d{2}:\d{2}:\d{2}\.\d{3}\]?\s*', '', text_with_timestamps)
        
        # Clean up extra whitespace
        plain_text = ' '.join(plain_text.split())
        
        return plain_text

async def main():
    """Main entry point"""
    logger.info("🚀 Starting YouTube Extract MCP Server (MLX Pattern)")
    
    # Create and run server
    mcp_server = YouTubeExtractMCP()
    
    # Run with stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="youtube-extract-mlx",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Server shutdown requested")
    except Exception as e:
        logger.error(f"💥 Server error: {e}")
        sys.exit(1)