"""
Build script to create standalone .exe for AIra Pro Photobooth System
Run this script: python build_exe.py
"""

import os
import sys
import shutil
from pathlib import Path

def build_exe():
    """Build the photobooth executable using PyInstaller."""
    
    print("=" * 60)
    print("  AIra Pro Photobooth System - Build Script")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        os.system("pip install pyinstaller")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    # Remove .spec file if exists
    spec_file = "AIraPhotobooth.spec"
    if Path(spec_file).exists():
        Path(spec_file).unlink()
        print(f"  Removed {spec_file}")
    
    print("\n🔨 Building executable...")
    print("   This may take 2-5 minutes...")
    print()
    
    # Verify icon file exists
    icon_path = Path("assets/app_icon.ico")
    if not icon_path.exists():
        print(f"❌ ERROR: Icon file not found: {icon_path}")
        print("   Please run: python convert_logo.py")
        return 1
    print(f"✓ Using icon: {icon_path} ({icon_path.stat().st_size / 1024:.1f} KB)")
    print()
    
    # PyInstaller command
    build_command = (
        'pyinstaller '
        '--name AIraPhotobooth '
        '--windowed '
        '--onefile '
        '--icon=assets/app_icon.ico '
        '--add-data "config.json;." '
        '--add-data "frames;frames" '
        '--add-data "assets;assets" '
        '--hidden-import cv2 '
        '--hidden-import numpy '
        '--hidden-import PIL '
        '--hidden-import qrcode '
        '--collect-all PyQt6 '
        'main.py'
    )
    
    print(f"Running: {build_command}")
    print()
    
    # Execute build
    result = os.system(build_command)
    
    if result == 0:
        print("\n" + "=" * 60)
        print("  ✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print()
        print("📦 Executable created: dist/AIraPhotobooth.exe")
        print()
        
        # Get file size
        exe_path = Path("dist/AIraPhotobooth.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📊 File size: {size_mb:.1f} MB")
        print()
        
        # Copy cloudflared.exe if it exists in project root
        cloudflared_src = Path("cloudflared.exe")
        cloudflared_dst = Path("dist/cloudflared.exe")
        if cloudflared_src.exists():
            shutil.copy2(cloudflared_src, cloudflared_dst)
            print("✓ Cloudflare Tunnel included: dist/cloudflared.exe")
        else:
            print("⚠️  Cloudflare Tunnel not found in project root")
            print("   Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
            print("   Place cloudflared.exe in project root and rebuild")
        print()
        print("📋 Next steps:")
        print("  1. Test the .exe: dist/AIraPhotobooth.exe")
        print("  2. Create shortcuts for easy access")
        print("  3. Distribute to school computers")
        print()
        print("⚠️  Note: First run may trigger Windows SmartScreen")
        print("   Click 'More info' → 'Run anyway' to allow")
        print()
        
    else:
        print("\n" + "=" * 60)
        print("  ❌ BUILD FAILED!")
        print("=" * 60)
        print()
        print("Check the error messages above for details.")
        print("Common issues:")
        print("  - Missing dependencies: pip install -r requirements.txt")
        print("  - Antivirus blocking: Temporarily disable AV")
        print()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(build_exe())
