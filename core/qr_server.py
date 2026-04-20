"""AIra Pro Photobooth System - QR Code Server
Simple HTTP server for photo downloads via QR code.
"""

import logging
import socket
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import quote, unquote
import qrcode
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def get_download_page_html(photo_url: str, download_url: str, filename: str) -> str:
    """Generate the HTML download page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIra Pro Photobooth - Download Photo</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #e8e8e8;
        }}
        .container {{
            background: linear-gradient(145deg, #111111 0%, #0d0d0d 100%);
            border-radius: 16px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(212,175,55,0.1);
            text-align: center;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            color: #D4AF37;
            margin-bottom: 8px;
            letter-spacing: 2px;
        }}
        .subtitle {{
            font-size: 12px;
            color: #666;
            margin-bottom: 30px;
            letter-spacing: 3px;
            text-transform: uppercase;
        }}
        .photo-preview {{
            width: 100%;
            max-width: 350px;
            margin: 0 auto 30px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.4);
            border: 2px solid rgba(212,175,55,0.3);
        }}
        .photo-preview img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .download-btn {{
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
            color: #0a0a0a;
            border: none;
            padding: 16px 40px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(212,175,55,0.3);
        }}
        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(212,175,55,0.4);
        }}
        .download-btn:active {{
            transform: translateY(0);
        }}
        .filename {{
            font-size: 13px;
            color: #888;
            margin-bottom: 30px;
            word-break: break-all;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(212,175,55,0.2);
        }}
        .footer-brand {{
            font-size: 14px;
            color: #D4AF37;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .footer-dev {{
            font-size: 11px;
            color: #666;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 15px;
        }}
        @media (max-width: 480px) {{
            .container {{
                padding: 25px;
            }}
            .logo {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">&#128247;</div>
        <div class="logo">AIra Pro</div>
        <div class="subtitle">Photobooth</div>
        
        <div class="photo-preview">
            <img src="{photo_url}" alt="Your Photo">
        </div>
        
        <a href="{download_url}" download class="download-btn">
            &#11015; Download Photo
        </a>
        
        <div class="filename">{filename}</div>
        
        <div class="footer">
            <div class="footer-brand">AIra Photobooth System</div>
            <div class="footer-dev">Developed by John Melvin R. Macabeo</div>
        </div>
    </div>
</body>
</html>"""


class PhotoHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler for serving photos and download pages."""
    
    photo_directory = Path("events/output")
    base_url = None  # Will be set by QRCodeServer
    
    def log_message(self, format, *args):
        """Log requests for debugging."""
        logger.info(f"QR Server: {format % args}")
    
    def do_GET(self):
        """Handle GET requests."""
        # Parse the path (remove query string)
        path = unquote(self.path.split('?')[0])
        
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
        
        # If no path or path is empty, show error
        if not path:
            self._send_error(404, "Not Found")
            return
        
        # Check if this is a direct file request
        file_path = self.photo_directory / path
        
        # If file exists, serve it
        if file_path.exists() and file_path.is_file():
            # Check if client wants the download page
            user_agent = self.headers.get('User-Agent', '').lower()
            referer = self.headers.get('Referer', '')
            is_browser = any(x in user_agent for x in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])
            
            # Serve download page ONLY if:
            # 1. It's a browser request
            # 2. It's an image file
            # 3. The request is NOT coming from our own download page (no Referer or different referer)
            is_from_our_page = PhotoHTTPRequestHandler.base_url and referer.startswith(PhotoHTTPRequestHandler.base_url)
            
            if is_browser and path.lower().endswith(('.jpg', '.jpeg', '.png')) and not is_from_our_page:
                print(f"[QR SERVER] Serving DOWNLOAD PAGE for: {path} (browser request, new visit)")
                self._serve_download_page(path)
            else:
                # Direct file download (or image request from our download page)
                if is_from_our_page:
                    print(f"[QR SERVER] Serving IMAGE FILE for: {path} (from download page)")
                else:
                    print(f"[QR SERVER] Serving FILE for: {path}")
                self._serve_file(file_path)
        else:
            self._send_error(404, "File Not Found")
    
    def _serve_download_page(self, filename):
        """Serve the styled download page."""
        try:
            # Photo URL for image src (no query string)
            photo_url = f"/{quote(filename)}"
            # Download URL for the button (with query string to force download)
            download_url = f"/{quote(filename)}?download=1"
            
            html = get_download_page_html(photo_url, download_url, filename)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(html.encode('utf-8')))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
            print(f"[QR SERVER] Served download page for: {filename}")
            
        except Exception as e:
            logger.error(f"Error serving download page: {e}")
            self._send_error(500, "Internal Server Error")
    
    def _serve_file(self, file_path):
        """Serve a file directly."""
        try:
            content_type = 'image/jpeg' if file_path.suffix.lower() in ['.jpg', '.jpeg'] else 'image/png'
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            
            # Force download if ?download=1 is in URL
            if 'download=1' in self.path:
                self.send_header('Content-Disposition', f'attachment; filename="{file_path.name}"')
            
            self.end_headers()
            self.wfile.write(content)
            
            print(f"[QR SERVER] Served file: {file_path.name}")
            
        except Exception as e:
            logger.error(f"Error serving file: {e}")
            self._send_error(500, "Internal Server Error")
    
    def _send_error(self, code, message):
        """Send an error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"{code} {message}".encode())
    
    def end_headers(self):
        """Add CORS headers to allow cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        super().end_headers()


class QRCodeServer:
    """Manages QR code generation and HTTP server for photo downloads."""
    
    DEFAULT_PORT = 8080  # Fixed port for easier firewall configuration
    
    def __init__(self, port=None):
        """Initialize QR code server.
        
        Args:
            port: HTTP server port (None = use default 8080)
        """
        self.port = port or self.DEFAULT_PORT
        self.server = None
        self.server_thread = None
        self.base_url = None
        self._start_server()
    
    def _start_server(self):
        """Start the HTTP server in a background thread."""
        # Try ports: default first, then fallback to random
        ports_to_try = [self.port, 0] if self.port != 0 else [0]
        
        for port in ports_to_try:
            try:
                # Ensure photo directory exists
                photo_dir = Path("events/output")
                photo_dir.mkdir(parents=True, exist_ok=True)
                
                # Set the handler's directory
                PhotoHTTPRequestHandler.photo_directory = photo_dir
                PhotoHTTPRequestHandler.base_url = f"http://{self._get_local_ip()}:{port}"
                
                # Create server
                self.server = HTTPServer(("0.0.0.0", port), PhotoHTTPRequestHandler)
                
                # Get assigned port
                self.port = self.server.server_address[1]
                
                # Get local IP
                ip = self._get_local_ip()
                self.base_url = f"http://{ip}:{self.port}"
                
                # Start in background thread
                self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self.server_thread.start()
                
                logger.info(f"QR Server started at {self.base_url}")
                print(f"[QR SERVER] ✓ Started successfully at {self.base_url}")
                print(f"[QR SERVER] ✓ Server is listening on all network interfaces (0.0.0.0:{self.port})")
                print(f"[QR SERVER] ✓ Make sure Windows Firewall allows incoming connections on port {self.port}")
                
                # Print firewall warning if using non-standard port
                if self.port != self.DEFAULT_PORT:
                    print(f"[QR SERVER] WARNING: Using port {self.port} instead of {self.DEFAULT_PORT}")
                    print(f"[QR SERVER] For best results, ensure port {self.DEFAULT_PORT} is available")
                
                return
                
            except OSError as e:
                if "Address already in use" in str(e):
                    print(f"[QR SERVER] Port {port} is in use, trying next...")
                    continue
                raise
        
        logger.error("Failed to start QR server: All ports in use")
        print("[QR SERVER] Failed to start: All ports in use")
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
    
    def generate_qr_code(self, photo_path: str, size: int = 300) -> Image.Image:
        """Generate QR code image for a photo.

        Args:
            photo_path: Path to the photo file
            size: QR code size in pixels (300+ recommended for screen display)

        Returns:
            PIL Image of the QR code
        """
        if not self.base_url:
            logger.error("QR Server not running")
            print("[QR SERVER] Cannot generate QR code - server not running")
            return None

        try:
            photo_path = Path(photo_path)
            filename = photo_path.name

            # Ensure the file is in the output directory for serving
            output_dir = Path("events/output")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / filename

            # Copy file to output directory if it's not already there
            if photo_path != output_file:
                if photo_path.exists():
                    try:
                        import shutil
                        shutil.copy2(photo_path, output_file)
                        print(f"[QR SERVER] Copied photo to output directory: {output_file}")
                    except Exception as e:
                        print(f"[QR SERVER] ERROR copying file: {e}")
                        # Continue anyway - maybe the file is already there
                if not output_file.exists():
                    print(f"[QR SERVER] WARNING: Photo not found at {photo_path} or {output_file}")
                    return None

            # Keep the URL short — every extra character bumps the QR version
            download_url = f"{self.base_url}/{quote(filename)}"
            print(f"[QR SERVER] ✓ Generated download URL: {download_url}")
            print(f"[QR SERVER] ✓ URL length: {len(download_url)} characters")

            qr = qrcode.QRCode(
                version=None,             # Auto-fit
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% — maximum reliability for screens
                box_size=10,              # Standard module size
                border=4,                 # Standard quiet zone (4 modules, per spec)
            )
            qr.add_data(download_url)
            qr.make(fit=True)

            print(f"[QR SERVER] ✓ QR version: {qr.version}, modules: {qr.modules_count}x{qr.modules_count}")
            print(f"[QR SERVER] ✓ Error correction: ERROR_CORRECT_H (30% redundancy)")

            # NEAREST avoids blurring module edges — critical for reliable scanning
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to RGB if necessary (QR images can be mode '1' binary)
            if qr_img.mode != 'RGB':
                qr_img = qr_img.convert('RGB')
            
            # Add white border padding for better scanner detection
            # Create a new image with white background and paste QR code in center
            original_size = qr_img.size
            border_size = 40
            new_size = (original_size[0] + border_size * 2, original_size[1] + border_size * 2)
            qr_with_border = Image.new('RGB', new_size, 'white')
            qr_with_border.paste(qr_img, (border_size, border_size))
            qr_img = qr_with_border
            
            # Resize to target size using NEAREST to preserve sharp edges
            qr_img = qr_img.resize((size, size), Image.Resampling.NEAREST)

            print(f"[QR SERVER] ✓ QR code generated: {size}x{size}px with white border")
            return qr_img

        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            print(f"[QR SERVER] Error generating QR code: {e}")
            return None
    
    def stop(self):
        """Stop the HTTP server."""
        try:
            if self.server:
                print("[QR SERVER] Shutting down server...")
                self.server.shutdown()
                self.server = None
                logger.info("QR Server stopped")
                print("[QR SERVER] Server stopped")
        except Exception as e:
            logger.error(f"Error stopping QR server: {e}")
            print(f"[QR SERVER] Error during shutdown: {e}")
