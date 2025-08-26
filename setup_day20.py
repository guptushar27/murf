
#!/usr/bin/env python3
"""
Day 20 Setup Script - Murf WebSocket Integration
"""

import os
import sys
import subprocess

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking Day 20 Environment...")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python 3.8+ required")
        return False
    
    # Check required environment variables
    required_vars = ['MURF_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
        else:
            key_preview = os.environ.get(var)[:10] + "..."
            print(f"✅ {var}: {key_preview}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please set them in the Secrets panel:")
        for var in missing_vars:
            print(f"   {var}: your_api_key_here")
        return False
    
    # Check if required directories exist
    required_dirs = ['instance', 'services', 'templates', 'static']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory exists: {dir_name}")
        else:
            print(f"❌ Missing directory: {dir_name}")
            return False
    
    print("\n🎉 Environment check passed!")
    return True

def main():
    """Main setup function"""
    print("🚀 Day 20: Murf WebSocket Setup")
    print("🎵 VoxAura AI Voice Agent Platform")
    print()
    
    if not check_environment():
        print("\n❌ Environment check failed!")
        print("💡 Please fix the issues above and run again")
        sys.exit(1)
    
    print("\n✅ Day 20 setup completed successfully!")
    print("\n🎯 Ready to run:")
    print("   1. Run test: python test_day20_murf.py")
    print("   2. Start app: python main.py")
    print("   3. Open browser to http://localhost:5000")
    print("   4. Enable Murf WebSocket TTS")
    print("   5. Test voice interaction")
    print("   6. Screenshot base64 output for LinkedIn")

if __name__ == "__main__":
    main()
