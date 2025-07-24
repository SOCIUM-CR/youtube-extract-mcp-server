#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "yt-dlp>=2024.1.0",
# ]
# ///
"""
Phase 7 Enhanced Testing Script for YouTube Extract MCP Server
Tests all newly implemented features including critical fixes and optimizations.
"""

import asyncio
import json
import tempfile
from pathlib import Path
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from youtube_extract_mcp import YouTubeExtractMCP

async def test_phase_7_enhancements():
    """Test all Phase 7 enhancements including critical fixes"""
    print("🧪 Testing Phase 7 YouTube Extract MCP Enhancements")
    print("=" * 60)
    
    # Initialize the MCP server
    mcp_server = YouTubeExtractMCP()
    
    # Test cases for Phase 7 features
    test_cases = [
        {
            "name": "Global Configuration System",
            "test_type": "config",
            "description": "Test persistent global configuration"
        },
        {
            "name": "Timestamps Fix - Dual Processing",
            "url": "https://www.youtube.com/watch?v=7gDw9IaeKK4",
            "test_type": "timestamps",
            "description": "Verify different plain vs timestamped files"
        },
        {
            "name": "Optimized JSON Metadata",
            "url": "https://www.youtube.com/watch?v=7gDw9IaeKK4",
            "test_type": "metadata",
            "description": "Test JSON optimization and language links"
        },
        {
            "name": "New File Naming Convention",
            "url": "https://www.youtube.com/watch?v=7gDw9IaeKK4",
            "test_type": "naming",
            "description": "Test title-first naming with date"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"📝 {test_case['description']}")
        print("-" * 50)
        
        try:
            if test_case["test_type"] == "config":
                # Test global configuration
                await test_global_configuration(mcp_server)
                results.append({"test": test_case["name"], "status": "success"})
                
            elif test_case["test_type"] == "timestamps":
                # Test timestamp fix
                success = await test_timestamps_fix(mcp_server, test_case["url"])
                results.append({"test": test_case["name"], "status": "success" if success else "failed"})
                
            elif test_case["test_type"] == "metadata":
                # Test JSON metadata optimization
                success = await test_metadata_optimization(mcp_server, test_case["url"])
                results.append({"test": test_case["name"], "status": "success" if success else "failed"})
                
            elif test_case["test_type"] == "naming":
                # Test new file naming
                success = await test_file_naming(mcp_server, test_case["url"])
                results.append({"test": test_case["name"], "status": "success" if success else "failed"})
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            results.append({"test": test_case["name"], "status": "error", "error": str(e)})
    
    # Print summary
    await print_test_summary(results)
    
    # Return overall success
    success_count = sum(1 for r in results if r["status"] == "success")
    return success_count == len(results)

async def test_global_configuration(mcp_server):
    """Test global configuration system"""
    print("🔧 Testing global configuration system...")
    
    # Test show current config
    config_result = await mcp_server._show_current_config({})
    if config_result and len(config_result) > 0:
        config_text = config_result[0].text
        print("✅ Configuration display working")
        print(f"📄 Config preview: {config_text[:200]}...")
    else:
        raise Exception("Could not retrieve configuration")
    
    # Test configuration persistence
    temp_dir = Path(tempfile.mkdtemp()) / "phase7_test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    config_result = await mcp_server._configure_output_directory({"directory_path": str(temp_dir)})
    if config_result and "successfully" in config_result[0].text:
        print(f"✅ Configuration persisted to: {temp_dir}")
        print("✅ Global configuration system working")
    else:
        raise Exception("Configuration persistence failed")

async def test_timestamps_fix(mcp_server, url):
    """Test the critical timestamps fix"""
    print("⏰ Testing timestamps vs plain text fix...")
    
    # Configure temp directory
    temp_dir = Path(tempfile.mkdtemp()) / "timestamps_test"
    await mcp_server._configure_output_directory({"directory_path": str(temp_dir)})
    
    # Extract video with local save
    args = {
        "url": url,
        "language": "auto",
        "include_timestamps": True,
        "format": "json",
        "save_locally": True
    }
    
    result = await mcp_server._extract_video(args)
    
    if result and len(result) > 0:
        result_data = json.loads(result[0].text)
        transcription = result_data.get("transcription", {})
        
        plain_text = transcription.get("plain_text", "")
        timestamped_text = transcription.get("timestamped_text", "")
        
        if plain_text and timestamped_text and plain_text != timestamped_text:
            print("✅ Plain and timestamped texts are different (fix working)")
            print(f"📊 Plain text length: {len(plain_text)}")
            print(f"📊 Timestamped text length: {len(timestamped_text)}")
            print(f"📝 Timestamp markers detected: {'[' in timestamped_text}")
            return True
        else:
            print("❌ Plain and timestamped texts are identical (fix failed)")
            return False
    else:
        print("❌ No extraction result")
        return False

async def test_metadata_optimization(mcp_server, url):
    """Test JSON metadata optimization"""
    print("📋 Testing JSON metadata optimization...")
    
    # Configure temp directory
    temp_dir = Path(tempfile.mkdtemp()) / "metadata_test"
    await mcp_server._configure_output_directory({"directory_path": str(temp_dir)})
    
    # Extract video with local save
    args = {
        "url": url,
        "language": "auto",
        "format": "json",
        "save_locally": True
    }
    
    result = await mcp_server._extract_video(args)
    
    if result and len(result) > 0:
        result_data = json.loads(result[0].text)
        
        # Check for available languages info
        transcription = result_data.get("transcription", {})
        available_languages = transcription.get("available_languages", {})
        
        if available_languages and "total_languages" in available_languages:
            print(f"✅ Language availability info present: {available_languages['total_languages']} languages")
            print(f"📊 Language codes: {available_languages.get('language_codes', [])}")
            return True
        else:
            print("❌ Missing language availability optimization")
            return False
    else:
        print("❌ No extraction result")
        return False

async def test_file_naming(mcp_server, url):
    """Test new file naming convention"""
    print("📁 Testing new file naming convention...")
    
    # Configure temp directory  
    temp_dir = Path(tempfile.mkdtemp()) / "naming_test"
    await mcp_server._configure_output_directory({"directory_path": str(temp_dir)})
    
    # Extract video with local save
    args = {
        "url": url,
        "language": "auto", 
        "format": "json",
        "save_locally": True
    }
    
    result = await mcp_server._extract_video(args)
    
    if result and len(result) > 0:
        result_data = json.loads(result[0].text)
        local_save = result_data.get("local_save", {})
        
        if local_save.get("status") == "success":
            directory_path = local_save.get("directory", "")
            directory_name = Path(directory_path).name
            
            # Check naming convention: title_YYYYMMDD_videoID
            parts = directory_name.split("_")
            if len(parts) >= 3:
                # Get the date part (should be second to last)
                date_part = parts[-2]
                video_id = parts[-1]
                
                # Check if date part looks like YYYYMMDD
                if len(date_part) == 8 and date_part.isdigit():
                    print(f"✅ New naming convention working: {directory_name}")
                    print(f"📅 Date part: {date_part}")
                    print(f"🆔 Video ID: {video_id}")
                    return True
                else:
                    print(f"❌ Date format incorrect: {date_part}")
                    return False
            else:
                print(f"❌ Naming convention not followed: {directory_name}")
                return False
        else:
            print("❌ Local save failed")
            return False
    else:
        print("❌ No extraction result")
        return False

async def print_test_summary(results):
    """Print test results summary"""
    print("\n📊 Phase 7 Test Results Summary")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    total_tests = len(results)
    
    for result in results:
        status_emoji = "✅" if result["status"] == "success" else "❌"
        print(f"{status_emoji} {result['test']}: {result['status']}")
        if "error" in result:
            print(f"   └─ Error: {result['error']}")
    
    print(f"\n🎯 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All Phase 7 enhancements working correctly!")
        print("✨ Critical fixes implemented successfully!")
        print("\n🚀 Phase 7 Features Summary:")
        print("   • ⏰ Timestamps fix - separate plain/timestamped files")
        print("   • 📋 Optimized JSON metadata with language links")
        print("   • 🔧 Global configuration persistence")
        print("   • 📁 Improved file naming (title first + date)")
        print("   • 🆕 Enhanced MCP tools with new functionality")
    else:
        print("⚠️ Some tests failed - review implementation")

if __name__ == "__main__":
    success = asyncio.run(test_phase_7_enhancements())
    sys.exit(0 if success else 1)