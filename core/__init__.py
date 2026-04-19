"""AIra Pro Photobooth System - Core Modules
Camera, compositing, and session management.
"""

from .camera import CameraManager, WebcamClient
from .compositor import ImageCompositor
from .session_manager import SessionManager

__all__ = ['CameraManager', 'WebcamClient', 'ImageCompositor', 'SessionManager']
