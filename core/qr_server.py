"""AIra Pro Photobooth System - QR Code Server
Simple HTTP server for photo downloads via QR code.
"""

import logging
import socket
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import quote
import qrcode
from PIL import Image

logger = logging.getLogger(__name__)


class PhotoHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving photos."""
    
    def __init__(self, *args, photo_dir=None, **kwargs):
        self.photo_dir = photo_dir or Path("events/output")
        super().__init__(*args, directory=str(self.photo_dir), **kwargs)
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class QRCodeServer:
    """Manages QR code generation and HTTP server for photo downloads."""
    
    def __init__(self, port=0):
        """Initialize QR code server.
        
        Args:
            port: HTTP server port (0 = auto-assign)
        """
        self.port = port
        self.server = None
        self.server_thread = None
        self.base_url = None
        self._start_server()
    
    def _start_server(self):
        """Start the HTTP server in a background thread."""
        try:
            # Create server
            handler = lambda *args, **kwargs: PhotoHTTPRequestHandler(
                *args, photo_dir=Path("events/output"), **kwargs
            )
            self.server = HTTPServer(("0.0.0.0", self.port), handler)
            
            # Get assigned port
            self.port = self.server.server_address[1]
            
            # Get local IP
            ip = self._get_local_ip()
            self.base_url = f"http://{ip}:{self.port}"
            
            # Start in background thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logger.info(f"QR Server started at {self.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to start QR server: {e}")
            self.base_url = None
    
    def _get_local_ip(self):
        """Get local IP address for QR code URLs."""
        try:
            # Connect to external host to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
    
    def generate_qr_code(self, photo_path: str, size: int = 200) -> Image.Image:
        """Generate QR code image for a photo.
        
        Args:
            photo_path: Path to the photo file
            size: QR code size in pixels
            
        Returns:
            PIL Image of the QR code
        """
        if not self.base_url:
            logger.error("QR Server not running")
            return None
        
        try:
            # Get filename from path
            filename = Path(photo_path).name
            
            # Create download URL
            download_url = f"{self.base_url}/{quote(filename)}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=2,
            )
            qr.add_data(download_url)
            qr.make(fit=True)
            
            # Create image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
            
            return qr_img
            
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return None
    
    def stop(self):
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            logger.info("QR Server stopped")
