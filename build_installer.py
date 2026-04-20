"""
AIra Pro Photobooth System - Installer Builder
Creates a professional Windows installer using Inno Setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_inno_setup():
    """Check if Inno Setup is installed."""
    # Common installation paths
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def build_installer():
    """Build the Windows installer."""
    print("=" * 60)
    print("  AIra Pro Photobooth System - Installer Builder")
    print("=" * 60)
    print()
    
    # Check if dist exists
    if not Path("dist/AIraPhotobooth.exe").exists():
        print("❌ Error: dist/AIraPhotobooth.exe not found!")
        print("   Please run build_exe.py first to create the executable.")
        sys.exit(1)
    
    # Check if cloudflared.exe exists in dist
    if not Path("dist/cloudflared.exe").exists():
        print("⚠️  Warning: dist/cloudflared.exe not found!")
        print("   The installer will be created without Cloudflare Tunnel.")
        print()
    
    # Find Inno Setup
    iscc_path = check_inno_setup()
    
    if not iscc_path:
        print("❌ Inno Setup not found!")
        print()
        print("Please download and install Inno Setup:")
        print("  https://jrsoftware.org/isdl.php")
        print()
        print("After installation, run this script again.")
        sys.exit(1)
    
    print(f"✓ Inno Setup found: {iscc_path}")
    print()
    
    # Create output directory
    output_dir = Path("installer_output")
    output_dir.mkdir(exist_ok=True)
    
    # Build installer
    print("🔨 Building installer...")
    print()
    
    try:
        result = subprocess.run(
            [iscc_path, "installer_setup.iss"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Installer built successfully!")
            print()
            
            # Find the installer file
            installer_files = list(output_dir.glob("AIraPhotobooth_Setup_*.exe"))
            if installer_files:
                installer_path = installer_files[0]
                file_size_mb = installer_path.stat().st_size / (1024 * 1024)
                
                print("=" * 60)
                print("  ✅ INSTALLER READY!")
                print("=" * 60)
                print(f"📦 Installer: {installer_path}")
                print(f"📊 Size: {file_size_mb:.1f} MB")
                print()
                print("📋 Distribution Instructions:")
                print("  1. Copy the installer to a USB drive or cloud storage")
                print("  2. Run on target computer")
                print("  3. Follow the installation wizard")
                print("  4. Desktop shortcut will be created automatically")
                print()
                print("🎯 Features Included:")
                print("  ✓ Desktop shortcut")
                print("  ✓ Start Menu entry")
                print("  ✓ Automatic uninstaller")
                print("  ✓ All required files bundled")
                print("  ✓ Cloudflare Tunnel included")
                print()
            else:
                print("⚠️  Build completed but installer file not found in output directory")
                
        else:
            print("❌ Build failed!")
            print()
            print("Error output:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_installer()
