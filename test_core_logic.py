#!/usr/bin/env python3
"""
Quick Test for Core Logic
Tests functionality without external dependencies
"""

import asyncio
import tempfile
from pathlib import Path
import sys
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if modules can be imported"""
    print("🧪 Testing Module Imports")
    
    try:
        from playlist_processor import PlaylistProcessor
        print("✅ PlaylistProcessor imported successfully")
        
        # Test basic instantiation
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = PlaylistProcessor(Path(temp_dir))
            print(f"✅ PlaylistProcessor instantiated with output: {processor.output_directory}")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        return False

def test_brief_generation():
    """Test brief generation logic"""
    print("\n🧪 Testing Brief Generation Logic")
    
    try:
        from playlist_processor import PlaylistProcessor
        processor = PlaylistProcessor(None)
        
        # Test cases
        test_cases = [
            {
                "metadata": {
                    "title": "Introducción a Python",
                    "description": "Tutorial básico de programación"
                },
                "first_words": "Hola, en este video vamos a aprender Python",
                "expected_length": 200
            },
            {
                "metadata": {
                    "title": "Tutorial muy largo que debería ser truncado porque excede el límite",
                    "description": "Descripción muy larga que también debería ser truncada para evitar problemas de contexto"
                },
                "first_words": "Este es un texto muy largo para probar que el sistema de briefs funciona correctamente truncando el contenido",
                "expected_length": 200
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            brief = processor._generate_video_brief(
                test_case["metadata"], 
                test_case["first_words"]
            )
            
            if brief and len(brief) <= test_case["expected_length"]:
                print(f"✅ Test case {i}: Brief generated ({len(brief)} chars)")
            else:
                print(f"❌ Test case {i}: Brief failed ({len(brief) if brief else 0} chars)")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Brief generation test failed: {e}")
        return False

def test_directory_structure():
    """Test directory structure creation"""
    print("\n🧪 Testing Directory Structure")
    
    try:
        from playlist_processor import PlaylistProcessor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = PlaylistProcessor(Path(temp_dir))
            
            # Test different playlist names
            test_names = [
                "Normal Playlist Name",
                "Playlist with Special Characters: <>|*?",
                "Very Long Playlist Name That Should Be Truncated Because It Exceeds Normal Limits"
            ]
            
            for name in test_names:
                playlist_dir = processor._create_playlist_structure(name)
                
                # Check structure
                if (playlist_dir.exists() and 
                    (playlist_dir / "transcripts").exists() and 
                    (playlist_dir / "metadata").exists()):
                    print(f"✅ Directory created: {playlist_dir.name[:50]}...")
                else:
                    print(f"❌ Directory structure failed for: {name}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Directory structure test failed: {e}")
        return False

def test_vtt_processing():
    """Test VTT processing logic"""
    print("\n🧪 Testing VTT Processing")
    
    try:
        from playlist_processor import PlaylistProcessor
        processor = PlaylistProcessor(None)
        
        # Create test VTT content
        test_vtt_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
Hola y bienvenidos al tutorial.

00:00:05.000 --> 00:00:10.000
Hoy vamos a aprender sobre Python.

00:00:10.000 --> 00:00:15.000
Empezaremos con variables y tipos de datos.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False) as temp_vtt:
            temp_vtt.write(test_vtt_content)
            temp_vtt.flush()
            
            # Process VTT
            result = processor._process_vtt_file_dual(Path(temp_vtt.name))
            
            plain_text = result.get("plain_text", "")
            timestamped_text = result.get("timestamped_text", "")
            
            # Validate results
            if plain_text and timestamped_text:
                print(f"✅ Plain text extracted ({len(plain_text)} chars)")
                print(f"✅ Timestamped text extracted ({len(timestamped_text)} chars)")
                print(f"✅ Texts are different: {plain_text != timestamped_text}")
                
                # Check content
                if "Hola y bienvenidos" in plain_text and "[00:00:00.000" in timestamped_text:
                    print("✅ Content validation passed")
                    return True
                else:
                    print("❌ Content validation failed")
                    return False
            else:
                print("❌ VTT processing returned empty results")
                return False
        
    except Exception as e:
        print(f"❌ VTT processing test failed: {e}")
        return False
    finally:
        try:
            Path(temp_vtt.name).unlink()
        except:
            pass

def test_index_generation():
    """Test index generation"""
    print("\n🧪 Testing Index Generation")
    
    try:
        from playlist_processor import PlaylistProcessor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = PlaylistProcessor(Path(temp_dir))
            playlist_dir = Path(temp_dir) / "test_playlist"
            playlist_dir.mkdir()
            (playlist_dir / "transcripts").mkdir()
            (playlist_dir / "metadata").mkdir()
            
            # Complete test data
            test_videos = [
                {
                    "sequence": 1,
                    "title": "Introducción a Python",
                    "duration": "15:23",
                    "status": "success",
                    "brief": "Bienvenidos al curso. Aprenderemos conceptos básicos...",
                    "url": "https://youtube.com/watch?v=test1"
                },
                {
                    "sequence": 2,
                    "title": "Variables y Tipos",
                    "duration": "12:45",
                    "status": "success",
                    "brief": "Hoy exploraremos variables, strings, enteros...",
                    "url": "https://youtube.com/watch?v=test2"
                }
            ]
            
            test_playlist_info = {
                "title": "Curso Completo de Python",
                "url": "https://youtube.com/playlist?list=test"
            }
            
            # Generate index
            processor._create_playlist_index(test_videos, test_playlist_info, playlist_dir)
            
            # Validate index
            index_file = playlist_dir / "PLAYLIST_INDEX.md"
            if index_file.exists():
                content = index_file.read_text(encoding='utf-8')
                
                # Check required elements
                checks = [
                    ("Title", "Curso Completo de Python" in content),
                    ("Video 1", "Introducción a Python" in content),
                    ("Video 2", "Variables y Tipos" in content),
                    ("Table format", "| # | Video |" in content),
                    ("Links", "./transcripts/" in content)
                ]
                
                all_passed = True
                for check_name, passed in checks:
                    if passed:
                        print(f"✅ {check_name} found in index")
                    else:
                        print(f"❌ {check_name} missing in index")
                        all_passed = False
                
                if all_passed:
                    print(f"✅ Index file generated successfully ({len(content)} chars)")
                    return True
                else:
                    print("❌ Index content validation failed")
                    return False
            else:
                print("❌ Index file not created")
                return False
        
    except Exception as e:
        print(f"❌ Index generation test failed: {e}")
        return False

def test_mcp_integration():
    """Test MCP integration logic"""
    print("\n🧪 Testing MCP Integration")
    
    try:
        # Test importing main MCP server
        from youtube_extract_mcp import YouTubeExtractMCP
        print("✅ YouTubeExtractMCP imported successfully")
        
        # Test that new tool is registered
        server_instance = YouTubeExtractMCP()
        tools = server_instance.server.list_tools()
        
        tool_names = [tool.name for tool in tools.tools]
        
        if "youtube_extract_playlist" in tool_names:
            print("✅ youtube_extract_playlist tool registered")
        else:
            print("❌ youtube_extract_playlist tool not found")
            print(f"   Available tools: {tool_names}")
            return False
        
        print(f"✅ Total tools available: {len(tool_names)}")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        return False

def main():
    """Run core logic tests"""
    print("🧪 YouTube Extract MCP - Core Logic Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Brief Generation Logic", test_brief_generation),
        ("Directory Structure", test_directory_structure),
        ("VTT Processing Logic", test_vtt_processing),
        ("Index Generation", test_index_generation),
        ("MCP Integration", test_mcp_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
        except Exception as e:
            print(f"💥 ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 CORE LOGIC TEST RESULTS")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CORE LOGIC TESTS PASSED!")
        print("✨ Phase 8 implementation is working correctly!")
        return True
    else:
        print("⚠️ Some tests failed. Check implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)