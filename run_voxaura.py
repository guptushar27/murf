
#!/usr/bin/env python3
"""
VoxAura AI Voice Agent - Clean Startup Script
Days 17, 18, 19, 20 Implementation
"""

import sys
import os
import subprocess
import time

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'pydantic',
        'flask',
        'flask_socketio',
        'websockets',
        'assemblyai',
        'google.generativeai'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').replace('.', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return missing

def install_missing(packages):
    """Install missing packages"""
    if packages:
        print(f"\n🔧 Installing missing packages: {', '.join(packages)}")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + packages)

def main():
    print("🚀 VoxAura AI Voice Agent Startup")
    print("=" * 50)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        install_missing(missing)
    
    print("\n🎯 Starting VoxAura Server...")
    print("🌐 Access at: http://0.0.0.0:5000")
    print("🎯 Day 18 Turn Detection: http://0.0.0.0:5000/day18-turn-detection")
    print("=" * 50)
    
    # Start the app
    try:
        from app import app, socketio
        socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
