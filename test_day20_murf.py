
#!/usr/bin/env python3
"""
Test script for Day 20: Murf WebSocket Integration
"""

import asyncio
import os
import sys
from services.murf_websocket_service import MurfWebSocketService

async def test_murf_websocket():
    """Test Murf WebSocket functionality"""
    print("🎵 Testing Day 20: Murf WebSocket Integration")
    print("=" * 60)
    
    # Check API key
    api_key = os.environ.get('MURF_API_KEY')
    if not api_key:
        print("❌ MURF_API_KEY not found in environment variables")
        print("💡 Please set your Murf API key in the Secrets panel")
        print("💡 Go to: Secrets tab → Add new secret:")
        print("   Key: MURF_API_KEY")
        print("   Value: your_murf_api_key_here")
        return False
    
    print(f"✅ MURF_API_KEY configured: {api_key[:10]}...")
    
    # Initialize service
    murf_service = MurfWebSocketService()
    
    try:
        # Test connection
        print("\n🔗 Connecting to Murf WebSocket...")
        connected = await murf_service.connect()
        
        if not connected:
            print("❌ Failed to connect to Murf WebSocket")
            print("💡 Check your API key and network connection")
            return False
        
        print("✅ Connected to Murf WebSocket successfully")
        
        # Test TTS generation
        test_text = "Hello, this is a test of Day 20 Murf WebSocket integration for VoxAura."
        print(f"\n🎵 Generating audio for: {test_text}")
        
        audio_base64 = await murf_service.send_text_for_tts(test_text)
        
        if audio_base64:
            print(f"✅ Audio generated successfully!")
            print(f"📏 Base64 length: {len(audio_base64)} characters")
            print(f"🔊 Base64 preview: {audio_base64[:100]}...")
            print(f"🔊 Base64 ending: ...{audio_base64[-50:]}")
            
            # This is what should appear in console logs for LinkedIn screenshot
            print(f"\n{'🎵'*60}")
            print(f"🎵 DAY 20: MURF WEBSOCKET BASE64 AUDIO GENERATED")
            print(f"{'🎵'*60}")
            print(f"📝 Input Text: {test_text}")
            print(f"📏 Base64 Length: {len(audio_base64)} characters")
            print(f"🔊 Base64 Audio (first 100 chars): {audio_base64[:100]}...")
            print(f"🔊 Base64 Audio (last 50 chars): ...{audio_base64[-50:]}")
            print(f"⏰ Generated at: {asyncio.get_event_loop().time()}")
            print(f"{'🎵'*60}")
            
        else:
            print("❌ No audio generated")
            return False
        
        # Disconnect
        await murf_service.disconnect()
        print("\n✅ Disconnected from Murf WebSocket")
        
        print("\n🎉 Day 20 Murf WebSocket test completed successfully!")
        print("📸 Take a screenshot of the base64 output above for LinkedIn")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"🔍 Error details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Day 20: Murf WebSocket Test")
    print("📋 This test verifies Murf WebSocket integration")
    print()
    
    result = asyncio.run(test_murf_websocket())
    
    if result:
        print("\n✅ All tests passed!")
        print("🎯 Next steps:")
        print("   1. Run the main app: python main.py")
        print("   2. Enable Murf WebSocket in the UI")
        print("   3. Speak or type a message")
        print("   4. Check console for base64 audio output")
        print("   5. Take screenshot for LinkedIn")
    else:
        print("\n❌ Tests failed!")
        print("💡 Check your MURF_API_KEY configuration")
        print("💡 Make sure you have an active Murf API subscription")
        sys.exit(1)
