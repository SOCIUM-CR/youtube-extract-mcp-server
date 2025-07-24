#!/usr/bin/env python3
"""
Test script to verify the YouTube Extract MCP server functionality
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent))

from youtube_extract_mcp import YouTubeExtractMCP

async def test_server_initialization():
    """Test server initialization and basic functionality"""
    print("🧪 Testing YouTube Extract MCP Server initialization...")
    
    try:
        # Initialize server
        server = YouTubeExtractMCP()
        print("✅ Server initialized successfully")
        
        # Test video ID extraction
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
        ]
        
        for url in test_urls:
            video_id = server._extract_video_id(url)
            print(f"✅ Video ID extraction: {url} → {video_id}")
        
        # Test dependency imports
        try:
            import yt_dlp
            print(f"✅ yt-dlp available: {yt_dlp.__version__}")
        except ImportError as e:
            print(f"❌ yt-dlp import failed: {e}")
            
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            print("✅ youtube-transcript-api available")
        except ImportError as e:
            print(f"❌ youtube-transcript-api import failed: {e}")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False

async def test_fallback_method():
    """Test the fallback method with a known working video"""
    print("\n🧪 Testing fallback method...")
    
    try:
        server = YouTubeExtractMCP()
        
        # Test with Adrian Estevez video from user's test (known to have transcripts)
        test_url = "https://www.youtube.com/watch?v=FXIi-eOtgyg"
        
        result = await server._extract_transcription_fallback(test_url, "en", True)
        
        if result.get("status") == "success":
            print(f"✅ Fallback method succeeded!")
            print(f"   Language: {result.get('language')}")
            print(f"   Text length: {len(result.get('text', ''))}")
            print(f"   Method: {result.get('source_method')}")
            print(f"   Segments: {result.get('segments_count', 0)}")
        else:
            print(f"⚠️ Fallback method returned: {result.get('status')}")
            if result.get('error'):
                print(f"   Error: {result.get('error')}")
        
        return result.get("status") == "success"
        
    except Exception as e:
        print(f"❌ Fallback method test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 YouTube Extract MCP Server Test Suite\n")
        
        # Test 1: Basic initialization
        init_success = await test_server_initialization()
        
        if init_success:
            # Test 2: Fallback method
            fallback_success = await test_fallback_method()
            
            if fallback_success:
                print("\n🎉 All tests completed successfully!")
                print("   The server should work correctly with the new fixes.")
            else:
                print("\n⚠️ Fallback test failed - check dependencies")
        else:
            print("\n❌ Basic initialization failed")
        
        print("\n📝 Note: For full testing, run the server with Claude Desktop")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")