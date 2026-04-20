"""AIra Pro Photobooth System - Cloudflare Tunnel Manager
Manages Cloudflare Tunnel for public internet access to QR download server.
"""

import os
import sys
import time
import logging
import subprocess
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CloudflareTunnel:
    """Manages Cloudflare Tunnel for exposing local server to internet."""
    
    def __init__(self, local_port: int = 8080):
        """Initialize Cloudflare Tunnel manager.
        
        Args:
            local_port: Local server port to expose (default: 8080)
        """
        self.local_port = local_port
        self.tunnel_process: Optional[subprocess.Popen] = None
        self.public_url: Optional[str] = None
        self.is_running = False
        self.tunnel_thread: Optional[threading.Thread] = None
        
    def is_cloudflared_installed(self) -> bool:
        """Check if cloudflared is installed."""
        try:
            result = subprocess.run(
                ['cloudflared', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def install_cloudflared(self) -> bool:
        """Install cloudflared automatically.
        
        Returns:
            True if installation successful
        """
        print("[CLOUDFLARE] Installing cloudflared...")
        
        try:
            # Download and install cloudflared for Windows
            import urllib.request
            
            # Create temp directory
            temp_dir = Path("temp_cloudflared")
            temp_dir.mkdir(exist_ok=True)
            
            # Download URL for Windows
            download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            exe_path = temp_dir / "cloudflared.exe"
            
            print(f"[CLOUDFLARE] Downloading from: {download_url}")
            urllib.request.urlretrieve(download_url, exe_path)
            
            # Move to application directory
            dest_path = Path("cloudflared.exe")
            exe_path.rename(dest_path)
            
            # Clean up
            temp_dir.rmdir()
            
            print(f"[CLOUDFLARE] ✓ Installed to: {dest_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install cloudflared: {e}")
            print(f"[CLOUDFLARE] ❌ Installation failed: {e}")
            return False
    
    def start_tunnel(self) -> bool:
        """Start Cloudflare Tunnel.
        
        Returns:
            True if tunnel started successfully
        """
        if self.is_running:
            print("[CLOUDFLARE] Tunnel is already running")
            return True
        
        # Check if cloudflared is installed
        if not self.is_cloudflared_installed():
            # Try to install it
            if not Path("cloudflared.exe").exists():
                print("[CLOUDFLARE] cloudflared not found. Installing...")
                if not self.install_cloudflared():
                    return False
        
        print(f"[CLOUDFLARE] Starting tunnel for localhost:{self.local_port}...")
        
        try:
            # Start cloudflared process
            self.tunnel_process = subprocess.Popen(
                ['cloudflared', 'tunnel', '--url', f'http://localhost:{self.local_port}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Start thread to monitor output
            self.tunnel_thread = threading.Thread(
                target=self._monitor_tunnel,
                daemon=True
            )
            self.tunnel_thread.start()
            
            # Wait for tunnel to start (max 30 seconds)
            print("[CLOUDFLARE] Waiting for tunnel to initialize...")
            for i in range(30):
                if self.public_url:
                    break
                time.sleep(1)
            
            if self.public_url:
                self.is_running = True
                print(f"[CLOUDFLARE] ✓ Tunnel started successfully!")
                print(f"[CLOUDFLARE] ✓ Public URL: {self.public_url}")
                return True
            else:
                print("[CLOUDFLARE] ❌ Tunnel failed to start within 30 seconds")
                self.stop_tunnel()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start tunnel: {e}")
            print(f"[CLOUDFLARE] ❌ Error starting tunnel: {e}")
            return False
    
    def _monitor_tunnel(self):
        """Monitor tunnel output and extract public URL."""
        try:
            if not self.tunnel_process or not self.tunnel_process.stdout:
                return
            
            for line in self.tunnel_process.stdout:
                line = line.strip()
                
                # Log output
                if line:
                    logger.debug(f"cloudflared: {line}")
                
                # Look for the public URL
                if 'trycloudflare.com' in line:
                    # Extract URL from output
                    # Format: "https://xxxx-xxxx.trycloudflare.com"
                    parts = line.split()
                    for part in parts:
                        if 'trycloudflare.com' in part and part.startswith('http'):
                            self.public_url = part
                            print(f"[CLOUDFLARE] 🌐 Public URL detected: {self.public_url}")
                            break
                
                # Stop if process ended
                if self.tunnel_process.poll() is not None:
                    break
                    
        except Exception as e:
            logger.error(f"Tunnel monitor error: {e}")
            print(f"[CLOUDFLARE] Monitor error: {e}")
    
    def stop_tunnel(self):
        """Stop Cloudflare Tunnel."""
        if not self.is_running:
            return
        
        print("[CLOUDFLARE] Stopping tunnel...")
        
        try:
            if self.tunnel_process:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
                self.tunnel_process = None
            
            self.is_running = False
            self.public_url = None
            
            print("[CLOUDFLARE] ✓ Tunnel stopped")
            
        except Exception as e:
            logger.error(f"Error stopping tunnel: {e}")
            print(f"[CLOUDFLARE] Error during shutdown: {e}")
            # Force kill if terminate fails
            if self.tunnel_process:
                self.tunnel_process.kill()
    
    def get_public_url(self) -> Optional[str]:
        """Get the current public URL.
        
        Returns:
            Public URL if tunnel is running, None otherwise
        """
        return self.public_url
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.is_running:
            self.stop_tunnel()
