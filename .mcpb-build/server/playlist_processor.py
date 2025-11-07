#!/usr/bin/env python3
"""
Playlist Processor Module for YouTube Extract MCP
Handles playlist-specific logic without modifying core server

Architecture: Modular design that preserves existing core functionality
Strategy: Context-safe processing with playlist-centric organization
"""

import asyncio
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class PlaylistProcessor:
    """Handles YouTube playlist processing with intelligent organization"""
    
    def __init__(self, output_directory: Optional[Path]):
        self.output_directory = output_directory or Path.home() / "YouTube-Transcripts"
        self.processed_videos = []
        self.failed_videos = []
    
    async def process_playlist(self, playlist_url: str, max_videos: int = 50) -> List[Dict]:
        """
        Main method to process complete YouTube playlist
        Returns list of TextContent for MCP response
        """
        try:
            # 1. Extract playlist metadata and video list
            playlist_info = await self._extract_playlist_info(playlist_url)
            videos = playlist_info.get('videos', [])
            
            if len(videos) > max_videos:
                videos = videos[:max_videos]
                
            print(f"📋 Processing playlist: {playlist_info['title']}")
            print(f"🎵 Videos found: {len(videos)} (limit: {max_videos})")
            
            # 2. Create playlist directory structure
            playlist_dir = self._create_playlist_structure(playlist_info['title'])
            
            # 3. Process videos sequentially with progress
            results = []
            for i, video in enumerate(videos, 1):
                try:
                    print(f"🎬 Processing video {i}/{len(videos)}: {video.get('title', 'Unknown')[:50]}")
                    video_result = await self._process_single_video(video, i, playlist_dir)
                    results.append(video_result)
                    self.processed_videos.append(video_result)
                except Exception as e:
                    print(f"❌ Error processing video {i}: {str(e)}")
                    error_result = {
                        "sequence": i,
                        "video_id": video.get('id', 'unknown'),
                        "title": video.get('title', 'Unknown'),
                        "status": "failed",
                        "error": str(e)
                    }
                    results.append(error_result)
                    self.failed_videos.append(error_result)
            
            # 4. Generate playlist index and metadata
            self._create_playlist_index(results, playlist_info, playlist_dir)
            self._save_playlist_metadata(playlist_info, results, playlist_dir)
            
            # 5. Generate MCP response
            return self._generate_mcp_response(playlist_info, results, playlist_dir)
            
        except Exception as e:
            error_msg = f"❌ Error processing playlist: {str(e)}"
            print(error_msg)
            return [{"type": "text", "text": error_msg}]
    
    async def _extract_playlist_info(self, playlist_url: str) -> Dict[str, Any]:
        """Extract playlist metadata and video list using yt-dlp"""
        
        # Extract playlist metadata
        metadata_cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--dump-json',
            '--flat-playlist',
            '--playlist-end', '1',  # Just get playlist info, not individual videos
            playlist_url
        ]
        
        try:
            metadata_result = await asyncio.create_subprocess_exec(
                *metadata_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            metadata_stdout, metadata_stderr = await metadata_result.communicate()
            
            if metadata_result.returncode != 0:
                raise RuntimeError(f"yt-dlp playlist metadata failed: {metadata_stderr.decode()}")
            
            # Parse first line for playlist info
            first_line = metadata_stdout.decode().strip().split('\n')[0]
            playlist_data = json.loads(first_line)
            
        except Exception as e:
            # Fallback: create minimal playlist info
            playlist_data = {
                'title': 'Unknown Playlist',
                'id': 'unknown',
                'uploader': 'Unknown'
            }
        
        # Extract video list
        videos_cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--flat-playlist',
            '--dump-json',
            playlist_url
        ]
        
        try:
            videos_result = await asyncio.create_subprocess_exec(
                *videos_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            videos_stdout, videos_stderr = await videos_result.communicate()
            
            if videos_result.returncode != 0:
                raise RuntimeError(f"yt-dlp video list extraction failed: {videos_stderr.decode()}")
            
            # Parse video entries
            videos = []
            for line in videos_stdout.decode().strip().split('\n'):
                if line:
                    try:
                        video_data = json.loads(line)
                        videos.append(video_data)
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"⚠️ Error extracting video list: {e}")
            videos = []
        
        return {
            'title': playlist_data.get('title', 'Unknown Playlist'),
            'url': playlist_url,
            'id': playlist_data.get('id', 'unknown'),
            'uploader': playlist_data.get('uploader', 'Unknown'),
            'videos': videos
        }
    
    def _create_playlist_structure(self, playlist_title: str) -> Path:
        """Create directory structure for playlist"""
        # Clean title and add date
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', playlist_title)[:80]
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Create main playlist directory
        playlist_dir = self.output_directory / "playlists" / f"{clean_title}_{date_str}"
        playlist_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (playlist_dir / "transcripts").mkdir(exist_ok=True)
        (playlist_dir / "metadata").mkdir(exist_ok=True)
        
        print(f"📁 Created playlist structure: {playlist_dir}")
        return playlist_dir
    
    async def _process_single_video(self, video: Dict, sequence: int, playlist_dir: Path) -> Dict:
        """Process individual video within playlist context"""
        
        video_url = f"https://youtube.com/watch?v={video['id']}"
        video_title = video.get('title', 'Unknown Video')
        
        # Clean filename for sequence
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', video_title)[:50]
        sequence_prefix = f"{sequence:02d}"
        base_filename = f"{sequence_prefix}_{clean_title}"
        
        try:
            # Extract video metadata
            metadata = await self._extract_video_metadata(video_url)
            
            # Extract transcription
            transcription_data = await self._extract_video_transcription(video_url)
            
            # Save files in playlist structure
            transcript_plain_path = playlist_dir / "transcripts" / f"{base_filename}_plain.txt"
            transcript_timestamps_path = playlist_dir / "transcripts" / f"{base_filename}_timestamps.txt"
            metadata_path = playlist_dir / "metadata" / f"{base_filename}.json"
            
            # Write transcription files
            if transcription_data.get('plain_text'):
                transcript_plain_path.write_text(transcription_data['plain_text'], encoding='utf-8')
            
            if transcription_data.get('timestamped_text'):
                transcript_timestamps_path.write_text(transcription_data['timestamped_text'], encoding='utf-8')
            
            # Write metadata
            optimized_metadata = self._create_optimized_metadata(metadata, transcription_data)
            metadata_path.write_text(
                json.dumps(optimized_metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            # Generate context-safe brief
            first_words = transcription_data.get('plain_text', '')[:150]
            brief = self._generate_video_brief(metadata, first_words)
            
            return {
                "sequence": sequence,
                "video_id": video['id'],
                "title": video_title,
                "url": video_url,
                "duration": metadata.get('duration_string', 'Unknown'),
                "language": metadata.get('language', 'unknown'),
                "status": "success",
                "brief": brief,
                "files": {
                    "transcript_plain": str(transcript_plain_path),
                    "transcript_timestamps": str(transcript_timestamps_path),
                    "metadata": str(metadata_path)
                }
            }
            
        except Exception as e:
            print(f"❌ Error processing video {sequence}: {e}")
            return {
                "sequence": sequence,
                "video_id": video['id'],
                "title": video_title,
                "url": video_url,
                "status": "failed",
                "error": str(e)
            }
    
    async def _extract_video_metadata(self, video_url: str) -> Dict:
        """Extract video metadata using yt-dlp"""
        
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--dump-json',
            '--skip-download',
            video_url
        ]
        
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise RuntimeError(f"yt-dlp metadata extraction failed: {stderr.decode()}")
            
            return json.loads(stdout.decode())
            
        except Exception as e:
            print(f"⚠️ Error extracting metadata: {e}")
            return {}
    
    async def _extract_video_transcription(self, video_url: str) -> Dict:
        """Extract video transcription using yt-dlp"""
        
        # Create temporary directory for VTT files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--write-subs',
                '--write-auto-subs',
                '--skip-download',
                '--sub-format', 'vtt',
                '--sub-langs', 'es,es-ES,es-MX,es-AR,en',  # Priorizar español, fallback inglés
                '-o', str(temp_path / '%(title)s.%(ext)s'),
                video_url
            ]
            
            try:
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await result.communicate()
                
                if result.returncode != 0:
                    raise RuntimeError(f"yt-dlp transcription extraction failed: {stderr.decode()}")
                
                # Find VTT files
                vtt_files = list(temp_path.glob("*.vtt"))
                
                if not vtt_files:
                    raise RuntimeError("No transcription files found")
                
                # Process VTT file
                vtt_file = vtt_files[0]  # Use first available VTT file
                return self._process_vtt_file_dual(vtt_file)
                
            except Exception as e:
                print(f"⚠️ Error extracting transcription: {e}")
                return {"plain_text": "", "timestamped_text": ""}
    
    def _process_vtt_file_dual(self, vtt_file: Path) -> Dict:
        """Process VTT file to generate both plain and timestamped versions"""
        
        try:
            content = vtt_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            plain_text_lines = []
            timestamped_lines = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip WEBVTT header and empty lines
                if line.startswith('WEBVTT') or line == '':
                    i += 1
                    continue
                
                # Check if line contains timestamp
                if '-->' in line:
                    timestamp = line
                    i += 1
                    
                    # Get text content (may span multiple lines)
                    text_content = []
                    while i < len(lines) and lines[i].strip() != '':
                        text_line = lines[i].strip()
                        # Remove HTML tags
                        clean_text = re.sub(r'<[^>]+>', '', text_line)
                        if clean_text:
                            text_content.append(clean_text)
                        i += 1
                    
                    if text_content:
                        full_text = ' '.join(text_content)
                        plain_text_lines.append(full_text)
                        timestamped_lines.append(f"[{timestamp}] {full_text}")
                else:
                    i += 1
            
            return {
                "plain_text": '\n'.join(plain_text_lines),
                "timestamped_text": '\n'.join(timestamped_lines)
            }
            
        except Exception as e:
            print(f"⚠️ Error processing VTT file: {e}")
            return {"plain_text": "", "timestamped_text": ""}
    
    def _create_optimized_metadata(self, metadata: Dict, transcription_data: Dict) -> Dict:
        """Create optimized metadata without full transcription duplicates"""
        
        # Extract essential metadata
        optimized = {
            "video_info": {
                "id": metadata.get('id', ''),
                "title": metadata.get('title', ''),
                "description": metadata.get('description', '')[:500] + "..." if len(metadata.get('description', '')) > 500 else metadata.get('description', ''),
                "uploader": metadata.get('uploader', ''),
                "duration": metadata.get('duration', 0),
                "duration_string": metadata.get('duration_string', ''),
                "view_count": metadata.get('view_count', 0),
                "upload_date": metadata.get('upload_date', ''),
                "language": metadata.get('language', 'unknown')
            },
            "transcription_info": {
                "plain_text_length": len(transcription_data.get('plain_text', '')),
                "timestamped_text_length": len(transcription_data.get('timestamped_text', '')),
                "has_transcription": bool(transcription_data.get('plain_text', '').strip()),
                "first_100_words": ' '.join(transcription_data.get('plain_text', '').split()[:100])
            },
            "extraction_info": {
                "extracted_at": datetime.now().isoformat(),
                "method": "yt-dlp direct",
                "format": "vtt"
            }
        }
        
        return optimized
    
    def _generate_video_brief(self, metadata: Dict, first_words: str) -> str:
        """Generate context-safe brief from metadata + first words only"""
        
        title = metadata.get('title', '')[:60]
        description = metadata.get('description', '')[:100]
        first_text = first_words[:150]
        
        # Pattern detection for intro keywords
        intro_keywords = [
            "hoy vamos", "en este video", "vamos a ver", "aprenderemos", 
            "explicaré", "tutorial", "today we", "in this video", "we're going to"
        ]
        
        # Check if first words contain intro pattern
        has_intro = any(keyword in first_text.lower() for keyword in intro_keywords)
        
        if has_intro and first_text:
            brief = f"{first_text}..."
        elif description:
            brief = f"{description}. {first_text[:50]}..." if first_text else f"{description}"
        else:
            brief = f"{title}. {first_text[:80]}..." if first_text else title
        
        return brief[:200]  # Maximum 200 characters
    
    def _create_playlist_index(self, videos: List[Dict], playlist_info: Dict, playlist_dir: Path):
        """Generate PLAYLIST_INDEX.md with navigation table"""
        
        # Calculate statistics
        total_videos = len(videos)
        successful_videos = len([v for v in videos if v.get('status') == 'success'])
        failed_videos = len([v for v in videos if v.get('status') == 'failed'])
        
        # Generate markdown content
        index_content = f"""# 📺 {playlist_info['title']}

**Playlist**: [{playlist_info['url']}]({playlist_info['url']})  
**Procesado**: {datetime.now().strftime('%d %B %Y, %H:%M')}  
**Videos**: {successful_videos}/{total_videos} completados  
**Fallidos**: {failed_videos}

---

## 📊 Resumen Rápido

| # | Video | Duración | Estado | Brief |
|---|-------|----------|--------|-------|
"""
        
        # Add table rows
        for video in videos:
            seq = f"{video['sequence']:02d}"
            title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
            duration = video.get('duration', 'N/A')
            status = "✅" if video['status'] == 'success' else "❌"
            brief = video.get('brief', 'No brief available')[:60] + "..."
            
            index_content += f"| {seq} | {title} | {duration} | {status} | {brief} |\n"
        
        # Add file links section
        index_content += """

---

## 📁 Archivos Generados

### 📝 Transcripciones
"""
        
        for video in videos:
            if video['status'] == 'success':
                seq = f"{video['sequence']:02d}"
                clean_title = re.sub(r'[<>:"/\\|?*]', '_', video['title'])[:50]
                
                index_content += f"- [`{seq}_{clean_title}_plain.txt`](./transcripts/{seq}_{clean_title}_plain.txt)\n"
                index_content += f"- [`{seq}_{clean_title}_timestamps.txt`](./transcripts/{seq}_{clean_title}_timestamps.txt)\n"
        
        # Add direct links section
        index_content += """

---

## 🔍 Enlaces Directos

"""
        
        for video in videos:
            if video['status'] == 'success':
                seq = f"{video['sequence']:02d}"
                clean_title = re.sub(r'[<>:"/\\|?*]', '_', video['title'])[:50]
                
                index_content += f"- **Video {seq}**: [{video['url']}]({video['url']}) → [`Transcripción`](./transcripts/{seq}_{clean_title}_plain.txt)\n"
        
        # Save index file
        index_file = playlist_dir / "PLAYLIST_INDEX.md"
        index_file.write_text(index_content, encoding="utf-8")
        print(f"📋 Created playlist index: {index_file}")
    
    def _save_playlist_metadata(self, playlist_info: Dict, videos: List[Dict], playlist_dir: Path):
        """Save comprehensive playlist metadata as JSON"""
        
        metadata = {
            "playlist_info": {
                "title": playlist_info['title'],
                "url": playlist_info['url'],
                "total_videos": len(videos),
                "processed_videos": len([v for v in videos if v['status'] == 'success']),
                "failed_videos": len([v for v in videos if v['status'] == 'failed']),
                "processed_date": datetime.now().isoformat()
            },
            "videos": videos,
            "statistics": {
                "success_rate": len([v for v in videos if v['status'] == 'success']) / len(videos) * 100 if videos else 0,
                "total_files_created": len([v for v in videos if v['status'] == 'success']) * 3  # plain + timestamps + metadata
            }
        }
        
        metadata_file = playlist_dir / "playlist_metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"📊 Created playlist metadata: {metadata_file}")
    
    def _generate_mcp_response(self, playlist_info: Dict, videos: List[Dict], playlist_dir: Path) -> List[Dict]:
        """Generate MCP response for chat display"""
        
        successful_videos = [v for v in videos if v['status'] == 'success']
        failed_videos = [v for v in videos if v['status'] == 'failed']
        
        # Main response
        response_text = f"""📺 Playlist "{playlist_info['title']}" procesada exitosamente!

📊 RESUMEN:
├── {len(successful_videos)} videos procesados exitosamente
├── {len(failed_videos)} videos fallaron
└── Ubicación: {playlist_dir}

📋 ÍNDICE PRINCIPAL:
📁 PLAYLIST_INDEX.md → Navegación completa con tabla y enlaces directos

📝 TOP 5 VIDEOS:"""
        
        # Add top 5 videos
        for i, video in enumerate(successful_videos[:5], 1):
            brief = video.get('brief', 'No brief available')[:80]
            response_text += f"\n{i:02d}. {video['title'][:50]} → {brief}..."
        
        response_text += f"""

🔗 ACCESO RÁPIDO:
• Índice completo: PLAYLIST_INDEX.md
• Metadata técnica: playlist_metadata.json
• Transcripciones: /transcripts/ ({len(successful_videos) * 2} archivos)
• Metadata individual: /metadata/ ({len(successful_videos)} archivos JSON)
"""
        
        if failed_videos:
            response_text += f"\n⚠️ Videos fallidos: {len(failed_videos)} (ver detalles en playlist_metadata.json)"
        
        return [{"type": "text", "text": response_text}]