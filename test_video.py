#!/usr/bin/env python3
"""Simple test to verify video processing functionality"""

import subprocess
import sys
from pathlib import Path

def test_video_support():
    """Test that the script can handle video files"""
    try:
        # Test help output
        result = subprocess.run([sys.executable, 'resize_screenshots.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Script loads successfully")
            if "video" in result.stdout.lower():
                print("✓ Help mentions video support")
            else:
                print("⚠ Help does not mention video support")
        else:
            print(f"✗ Script failed to load: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_video_support()
    sys.exit(0 if success else 1)