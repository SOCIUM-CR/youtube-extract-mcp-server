#!/usr/bin/env python3
"""
Testing for Playlist Processing Features
Validates playlist-specific functionality
"""

import asyncio
import tempfile
from pathlib import Path
import sys
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from playlist_processor import PlaylistProcessor
    PROCESSOR_AVAILABLE = True
except ImportError:
    print("⚠️ PlaylistProcessor not available for testing")
    PROCESSOR_AVAILABLE = False

async def test_playlist_extraction():
    """Test playlist video extraction"""
    print("🧪 Testing Playlist Video Extraction")
    
    if not PROCESSOR_AVAILABLE:
        print("❌ PlaylistProcessor not available")
        return False
    
    # Test with a small public playlist (using Rick Astley's uploads as a safe test)
    test_playlist_url = "https://www.youtube.com/playlist?list=UUuAXFkgsw1L7xaCfnd5JJOw"  # Rick Astley official
    
    try:
        # Create temporary processor
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = PlaylistProcessor(Path(temp_dir))
            
            # Try to extract playlist info (not full processing)
            playlist_info = await processor._extract_playlist_info(test_playlist_url)
            
            if playlist_info and playlist_info.get('videos') and len(playlist_info['videos']) > 0:
                print(f"✅ Extracted playlist: {playlist_info['title']}")
                print(f"   Videos found: {len(playlist_info['videos'])}")
                print(f"   First video: {playlist_info['videos'][0].get('title', 'Unknown')[:50]}")
                return True
            else:
                print("❌ No videos extracted or playlist info incomplete")
                return False
                
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

async def test_brief_generation():
    """Test context-safe brief generation"""
    print("\n🧪 Testing Brief Generation")
    
    if not PROCESSOR_AVAILABLE:
        print("❌ PlaylistProcessor not available")
        return False
    
    processor = PlaylistProcessor(None)
    
    # Test data
    test_metadata = {
        "title": "Introducción a Python para Principiantes",
        "description": "En este tutorial aprenderás los conceptos básicos de Python programming"
    }
    
    test_first_words = "Hola, bienvenidos a este curso de Python. En este video vamos a ver los conceptos fundamentales que necesitas para empezar a programar."
    
    brief = processor._generate_video_brief(test_metadata, test_first_words)
    
    if brief and len(brief) <= 200:
        print(f"✅ Brief generated: {brief}")
        print(f"   Length: {len(brief)} chars (limit: 200)")
        return True
    else:
        print(f"❌ Brief generation failed or too long: {len(brief) if brief else 0} chars")
        return False

async def test_directory_structure():
    """Test playlist directory structure creation"""
    print("\n🧪 Testing Directory Structure Creation")
    
    if not PROCESSOR_AVAILABLE:
        print("❌ PlaylistProcessor not available")
        return False
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = PlaylistProcessor(Path(temp_dir))
            
            # Test directory creation
            playlist_dir = processor._create_playlist_structure("Test Playlist Name")
            
            # Check if directories were created
            if (playlist_dir.exists() and 
                (playlist_dir / "transcripts").exists() and 
                (playlist_dir / "metadata").exists()):
                
                print(f"✅ Directory structure created: {playlist_dir.name}")
                print(f"   Transcripts dir: {(playlist_dir / 'transcripts').exists()}")
                print(f"   Metadata dir: {(playlist_dir / 'metadata').exists()}")
                return True
            else:
                print("❌ Directory structure creation failed")
                return False
                
    except Exception as e:
        print(f"❌ Directory structure test failed: {e}")
        return False

async def test_vtt_processing():
    """Test VTT file processing for dual output"""
    print("\n🧪 Testing VTT Processing")
    
    if not PROCESSOR_AVAILABLE:
        print("❌ PlaylistProcessor not available")
        return False
    
    try:
        processor = PlaylistProcessor(None)
        
        # Create a test VTT file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False) as temp_vtt:
            test_vtt_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
Hello and welcome to this video tutorial.

00:00:05.000 --> 00:00:10.000
Today we're going to learn about Python programming.

00:00:10.000 --> 00:00:15.000
Let's start with the basics of variables and data types.
"""
            temp_vtt.write(test_vtt_content)
            temp_vtt.flush()
            
            # Process the VTT file
            result = processor._process_vtt_file_dual(Path(temp_vtt.name))
            
            plain_text = result.get("plain_text", "")
            timestamped_text = result.get("timestamped_text", "")
            
            if plain_text and timestamped_text and plain_text != timestamped_text:
                print("✅ VTT processing successful")
                print(f"   Plain text length: {len(plain_text)} chars")
                print(f"   Timestamped text length: {len(timestamped_text)} chars")
                print(f"   Texts are different: {plain_text != timestamped_text}")
                return True
            else:
                print("❌ VTT processing failed or texts are identical")
                return False
                
    except Exception as e:
        print(f"❌ VTT processing test failed: {e}")
        return False
    finally:
        # Clean up temp file
        try:
            Path(temp_vtt.name).unlink()
        except:
            pass

async def test_index_generation():
    """Test PLAYLIST_INDEX.md generation"""
    print("\n🧪 Testing Index Generation")
    
    if not PROCESSOR_AVAILABLE:
        print("❌ PlaylistProcessor not available")
        return False
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = PlaylistProcessor(Path(temp_dir))
            playlist_dir = Path(temp_dir) / "test_playlist"
            playlist_dir.mkdir()
            (playlist_dir / "transcripts").mkdir()
            (playlist_dir / "metadata").mkdir()
            
            # Test data
            test_videos = [
                {
                    "sequence": 1,
                    "title": "Introduction to Python",
                    "duration": "15:23",
                    "status": "success",
                    "brief": "Welcome to this Python course. We'll learn basics...",
                    "url": "https://youtube.com/watch?v=test1"
                },
                {
                    "sequence": 2,
                    "title": "Variables and Data Types",
                    "duration": "12:45",
                    "status": "success",
                    "brief": "Today we'll explore variables, strings, integers...",
                    "url": "https://youtube.com/watch?v=test2"
                }
            ]
            
            test_playlist_info = {
                "title": "Complete Python Course",
                "url": "https://youtube.com/playlist?list=test"
            }
            
            # Generate index
            processor._create_playlist_index(test_videos, test_playlist_info, playlist_dir)
            
            # Check if index was created
            index_file = playlist_dir / "PLAYLIST_INDEX.md"
            if index_file.exists():
                content = index_file.read_text()
                if "Complete Python Course" in content and "Introduction to Python" in content:
                    print("✅ PLAYLIST_INDEX.md generated successfully")
                    print(f"   File size: {len(content)} chars")
                    print(f"   Contains title: {'Complete Python Course' in content}")
                    return True
                else:
                    print("❌ Index content incomplete")
                    return False
            else:
                print("❌ PLAYLIST_INDEX.md not created")
                return False
                
    except Exception as e:
        print(f"❌ Index generation test failed: {e}")
        return False

async def main():
    """Run all playlist tests"""
    print("🧪 YouTube Extract MCP - Playlist Features Test Suite")
    print("=" * 60)
    
    tests = [
        ("Playlist Video Extraction", test_playlist_extraction),
        ("Brief Generation", test_brief_generation),
        ("Directory Structure Creation", test_directory_structure),
        ("VTT File Processing", test_vtt_processing),
        ("Index Generation", test_index_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
            print(f"{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
        except Exception as e:
            print(f"💥 ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 PLAYLIST TEST RESULTS")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL PLAYLIST FEATURES WORKING CORRECTLY!")
        return True
    else:
        print("⚠️ Some tests failed. Check implementation.")
        return False

if __name__ == "__main__":
    if not PROCESSOR_AVAILABLE:
        print("❌ Cannot run playlist tests: PlaylistProcessor module not available")
        sys.exit(1)
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)