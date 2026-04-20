"""
Clear Windows Icon Cache to fix stale icons
Run this if your app still shows the Python logo after rebuilding
"""
import subprocess
import os

def clear_icon_cache():
    """Clear Windows icon cache"""
    print("Clearing Windows Icon Cache...")
    print()
    
    # Kill Explorer
    print("1. Closing Windows Explorer...")
    subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], 
                   capture_output=True, timeout=10)
    
    # Delete icon cache files
    cache_dir = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer")
    cache_files = [
        "iconcache_*.db",
        "thumbcache_*.db",
        "iconcache.db"
    ]
    
    print("2. Deleting icon cache files...")
    deleted = 0
    for pattern in cache_files:
        import glob
        for cache_file in glob.glob(os.path.join(cache_dir, pattern)):
            try:
                os.remove(cache_file)
                print(f"   ✓ Deleted: {os.path.basename(cache_file)}")
                deleted += 1
            except Exception as e:
                print(f"   ⚠ Could not delete {os.path.basename(cache_file)}: {e}")
    
    if deleted == 0:
        print("   No cache files found to delete")
    
    # Restart Explorer
    print("3. Restarting Windows Explorer...")
    subprocess.Popen("explorer.exe")
    
    print()
    print("Icon cache cleared!")
    print()
    print("Next steps:")
    print("   1. Wait 10 seconds for Explorer to restart")
    print("   2. Check your desktop shortcut - should now show your logo")
    print("   3. If still showing Python icon, right-click -> Properties -> Change Icon")

if __name__ == "__main__":
    clear_icon_cache()

