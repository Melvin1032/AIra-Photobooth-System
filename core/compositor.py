"""AIra Pro Photobooth System - Image Compositor
Handles photo compositing with frames.
"""

import logging
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class ImageCompositor:
    """Composites photos onto frame templates."""
    
    def __init__(self):
        self.frame_image: Optional[Image.Image] = None
        self.frame_metadata: Optional[dict] = None
        self.slots: List[Tuple[int, int, int, int]] = []  # (x, y, width, height) for each slot
    
    def load_frame(self, frame_path: str, metadata: dict = None) -> bool:
        """Load a frame template."""
        try:
            self.frame_image = Image.open(frame_path).convert('RGBA')
            self.frame_metadata = metadata or {}
            
            # Parse slot positions from metadata or use defaults
            self._parse_slots()
            
            logger.info(f"Frame loaded: {frame_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load frame: {e}")
            return False
    
    def _parse_slots(self):
        """Parse photo slot positions from metadata."""
        self.slots = []
        
        if self.frame_metadata and 'slots' in self.frame_metadata:
            # Check if slots is a list of position dicts or just a number
            slot_data = self.frame_metadata['slots']
            if isinstance(slot_data, list) and len(slot_data) > 0 and isinstance(slot_data[0], dict):
                # Use metadata slots with positions
                for slot in slot_data:
                    self.slots.append((slot['x'], slot['y'], slot['width'], slot['height']))
            else:
                # slots is just a number, use full frame area
                frame_width, frame_height = self.frame_image.size
                self.slots = [(0, 0, frame_width, frame_height)]
        else:
            # Default: use full frame area
            frame_width, frame_height = self.frame_image.size
            self.slots = [(0, 0, frame_width, frame_height)]
    
    def composite_photos(self, photo_paths: List[str], output_path: str) -> bool:
        """Composite photos onto frame and save."""
        try:
            if not self.frame_image:
                logger.error("No frame loaded")
                return False
            
            # Get frame dimensions
            frame_width, frame_height = self.frame_image.size
            
            # Start with the first photo as base (resized to frame dimensions)
            if not photo_paths:
                logger.error("No photos provided")
                return False
            
            photo_path = photo_paths[0]
            if not Path(photo_path).exists():
                logger.error(f"Photo not found: {photo_path}")
                return False
            
            # Load photo and resize to match frame dimensions
            photo = Image.open(photo_path).convert('RGBA')
            photo_resized = photo.resize((frame_width, frame_height), Image.Resampling.LANCZOS)
            
            # Create result by starting with the photo
            result = photo_resized
            
            # Overlay the frame on top of the photo
            # The frame should have transparent areas where the photo should show through
            if self.frame_image.mode == 'RGBA':
                # Frame has alpha channel, use it for blending
                result = Image.alpha_composite(result, self.frame_image)
            else:
                # Frame doesn't have alpha, paste it on top
                result.paste(self.frame_image, (0, 0), self.frame_image if self.frame_image.mode == 'RGBA' else None)
            
            # Convert to RGB for saving (remove alpha)
            result_rgb = Image.new('RGB', result.size, (255, 255, 255))
            result_rgb.paste(result, mask=result.split()[3] if result.mode == 'RGBA' else None)
            
            # Save result
            result_rgb.save(output_path, 'JPEG', quality=95)
            logger.info(f"Composited photo saved: {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Compositing failed: {e}")
            return False
    
    def _resize_to_fit(self, image: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
        """Resize image to fit within max_size while maintaining aspect ratio."""
        width, height = image.size
        max_width, max_height = max_size
        
        # Calculate scale factor
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h)
        
        # Resize
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def create_mock_composite(self, output_path: str, num_photos: int = 1) -> bool:
        """Create a mock composite for testing."""
        try:
            # Create a simple mock image
            width, height = 1200, 1800
            image = Image.new('RGB', (width, height), (240, 240, 240))
            draw = ImageDraw.Draw(image)
            
            # Draw frame border
            border_width = 50
            draw.rectangle([0, 0, width-1, height-1], outline='#D4AF37', width=border_width)
            
            # Draw photo placeholders
            photo_height = (height - 2 * border_width - (num_photos + 1) * 20) // num_photos
            photo_width = width - 2 * border_width - 40
            
            for i in range(num_photos):
                y = border_width + 20 + i * (photo_height + 20)
                x = border_width + 20
                
                # Draw placeholder
                draw.rectangle(
                    [x, y, x + photo_width, y + photo_height],
                    fill=(200, 200, 200),
                    outline='#666',
                    width=2
                )
                
                # Add text
                draw.text(
                    (x + photo_width//2, y + photo_height//2),
                    f"Photo {i+1}",
                    fill=(100, 100, 100)
                )
            
            # Save
            image.save(output_path, 'JPEG', quality=95)
            logger.info(f"Mock composite saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Mock compositing failed: {e}")
            return False
