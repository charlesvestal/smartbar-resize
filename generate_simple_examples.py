#!/usr/bin/env python3
"""Generate example images with simple file names for README"""

import subprocess
import sys
from pathlib import Path

def generate_examples():
    """Generate simple example images for README"""
    
    # Create simple output directory
    output_dir = Path("examples_simple")
    output_dir.mkdir(exist_ok=True)
    
    # Process iPad landscape example
    cmd_ipad = [
        sys.executable, "resize_screenshots.py", 
        "examples/input/source_ipad_landscape.png",
        "-o", str(output_dir),
        "--device", "ipad", 
        "--families", "ipad",
        "--smartbar", "both"
    ]
    
    # Process iPhone portrait example  
    cmd_iphone = [
        sys.executable, "resize_screenshots.py",
        "examples/input/source_iphone_portrait.png", 
        "-o", str(output_dir),
        "--device", "iphone",
        "--families", "iphone", 
        "--smartbar", "portrait"
    ]
    
    try:
        print("Generating iPad example...")
        subprocess.run(cmd_ipad, check=True, capture_output=True)
        
        print("Generating iPhone example...")
        subprocess.run(cmd_iphone, check=True, capture_output=True)
        
        print("✅ Examples generated in examples_simple/")
        
        # List generated files
        for file in output_dir.rglob("*.png"):
            print(f"  - {file}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating examples: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = generate_examples()
    sys.exit(0 if success else 1)