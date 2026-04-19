"""
SnapFrame Pro - Camera Module
Handles webcam and tethered camera integration.
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Callable, List, Tuple
from PyQt6.QtCore import QThread, pyqtSignal
from PIL import Image

logger = logging.getLogger(__name__)


class CameraThread(QThread):
    """Background thread for camera capture."""
    
    frame_ready = pyqtSignal(bytes)  # JPEG encoded frame
    capture_ready = pyqtSignal(str)  # Path to captured photo
    error_occurred = pyqtSignal(str)
    
    def __init__(self, camera_id: int = 0, fps: int = 30):
        super().__init__()
        self.camera_id = camera_id
        self.fps = fps
        self.running = False
        self.capture_requested = False
        self.output_path = None
        self.frame_skip = 1  # No frame skipping for smoothness
        self.frame_count = 0
        self.preview_width = 640
        self.preview_height = 480
        self.actual_width = 0
        self.actual_height = 0
    
    def run(self):
        """Main camera loop."""
        cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)  # Use DirectShow backend
        
        if not cap.isOpened():
            self.error_occurred.emit(f"Failed to open camera {self.camera_id}")
            return
        
        # Get camera's native resolution first
        native_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        native_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Only set resolution if camera supports higher resolution
        # Try 1920x1080 for HD cameras, fallback to native if not supported
        if native_width >= 1920 and native_height >= 1080:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif native_width >= 1280 and native_height >= 720:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # Otherwise use native resolution (don't force it)
        
        # Get actual camera resolution after setting
        self.actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set camera properties for smooth capture - use default auto settings
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for lower latency
        
        # Let camera use default auto-exposure and auto-gain
        # Don't override brightness/contrast to use camera defaults
        
        self.running = True
        logger.info(f"Camera {self.camera_id} started at {self.actual_width}x{self.actual_height}")
        
        while self.running:
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            self.frame_count += 1
            
            # Handle capture request
            if self.capture_requested:
                self._save_frame(frame)
                self.capture_requested = False
            
            # Skip frames for preview (performance) - only if needed
            if self.frame_skip > 1 and self.frame_count % self.frame_skip != 0:
                continue
            
            # Encode and emit preview frame
            jpeg_bytes = self._encode_frame(frame)
            if jpeg_bytes:
                self.frame_ready.emit(jpeg_bytes)
        
        cap.release()
        logger.info(f"Camera {self.camera_id} stopped")
    
    def _encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode frame to JPEG bytes - optimized for smooth preview."""
        try:
            # Calculate preview size based on actual frame size
            # Use smaller preview for smoother performance (854x480 is 480p, good balance)
            h, w = frame.shape[:2]
            
            # Target 854x480 for smooth 30fps preview (16:9 aspect ratio)
            if w > 854 or h > 480:
                preview_frame = cv2.resize(frame, (854, 480), interpolation=cv2.INTER_LINEAR)
            else:
                preview_frame = frame
            
            # Encode with moderate quality for speed (85 is good balance)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            _, jpeg_bytes = cv2.imencode('.jpg', preview_frame, encode_param)
            return jpeg_bytes.tobytes()
        except Exception as e:
            logger.error(f"Frame encoding error: {e}")
            return None
    
    def _save_frame(self, frame: np.ndarray):
        """Save captured frame to file."""
        try:
            # Save full resolution
            output_path = self.output_path or "capture.jpg"
            cv2.imwrite(output_path, frame)
            self.capture_ready.emit(output_path)
            logger.info(f"Photo saved: {output_path}")
        except Exception as e:
            logger.error(f"Save frame error: {e}")
            self.error_occurred.emit(f"Failed to save photo: {e}")
    
    def capture(self, output_path: str):
        """Request a photo capture."""
        self.output_path = output_path
        self.capture_requested = True
    
    def stop(self):
        """Stop the camera thread."""
        self.running = False
        self.wait(1000)


class CameraManager:
    """Manages camera operations and settings."""
    
    def __init__(self):
        self.camera_thread: Optional[CameraThread] = None
        self.current_camera_id = 0
        self.frame_callback: Optional[Callable] = None
        self.capture_callback: Optional[Callable] = None
    
    def detect_cameras(self) -> List[Tuple[int, str]]:
        """Detect available cameras with friendly names."""
        cameras = []
        
        # Try to get camera names from Windows
        camera_names = self._get_windows_camera_names()
        
        for i in range(5):  # Check first 5 indices
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        
                        # Use friendly name if available
                        name = camera_names.get(i, f"Camera {i}")
                        display_name = f"{name} ({width}x{height})"
                        cameras.append((i, display_name))
                cap.release()
            except Exception as e:
                logger.debug(f"Camera {i} not available: {e}")
        
        return cameras
    
    def _get_windows_camera_names(self) -> dict:
        """Get camera friendly names from Windows registry."""
        camera_names = {}
        
        try:
            import winreg
            
            # Try Windows registry paths for camera devices
            registry_paths = [
                r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{e5323777-f976-4f5b-9b55-b94699c46e44}",
                r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{65e8773d-8f56-11d0-a3b9-00a0c9223196}",
            ]
            
            for key_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    idx = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, idx)
                            # Extract device info
                            if "usb" in subkey_name.lower() or "camera" in subkey_name.lower():
                                # Parse device index from name
                                parts = subkey_name.split('#')
                                for part in parts:
                                    if part.isdigit():
                                        cam_idx = int(part)
                                        camera_names[cam_idx] = f"USB Camera {cam_idx + 1}"
                            idx += 1
                        except WindowsError:
                            break
                    winreg.CloseKey(key)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Registry query failed: {e}")
        
        # Fallback to WMI if registry didn't work
        if not camera_names:
            try:
                import subprocess
                result = subprocess.run(
                    ['wmic', 'path', 'Win32_PnPEntity', 'where', 'Service="usbvideo"', 'get', 'Name'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for idx, line in enumerate(lines):
                    if line.strip():
                        camera_names[idx] = line.strip()
            except Exception as e:
                logger.debug(f"WMI query failed: {e}")
        
        return camera_names
    
    def start_camera(self, camera_id: int = 0, fps: int = 30,
                     frame_callback: Callable = None,
                     capture_callback: Callable = None):
        """Start camera capture."""
        self.stop_camera()
        
        self.current_camera_id = camera_id
        self.frame_callback = frame_callback
        self.capture_callback = capture_callback
        
        self.camera_thread = CameraThread(camera_id, fps=fps)
        
        if frame_callback:
            self.camera_thread.frame_ready.connect(frame_callback)
        if capture_callback:
            self.camera_thread.capture_ready.connect(capture_callback)
        
        self.camera_thread.error_occurred.connect(self._on_error)
        self.camera_thread.start()
    
    def stop_camera(self):
        """Stop camera capture."""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None
    
    def capture_photo(self, output_path: str):
        """Capture a photo."""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.capture(output_path)
            return True
        return False
    
    def is_running(self) -> bool:
        """Check if camera is running."""
        return self.camera_thread is not None and self.camera_thread.isRunning()
    
    def _on_error(self, message: str):
        """Handle camera errors."""
        logger.error(f"Camera error: {message}")


class WebcamClient:
    """Legacy webcam client for compatibility."""
    
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None
    
    def connect(self) -> bool:
        """Connect to webcam."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            return self.cap.isOpened()
        except Exception as e:
            logger.error(f"Webcam connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from webcam."""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def get_frame_for_preview(self) -> Optional[bytes]:
        """Get frame encoded for preview."""
        frame = self.capture_frame()
        if frame is not None:
            preview_frame = cv2.resize(frame, (640, 480))
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
            _, jpeg_bytes = cv2.imencode('.jpg', preview_frame, encode_param)
            return jpeg_bytes.tobytes()
        return None
