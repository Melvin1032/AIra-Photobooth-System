"""
SnapFrame Pro - Performance Optimizations
All performance optimization implementations for low-end PCs.
Includes: SQLite WAL mode, frame pre-caching, memory cleanup, and more.
"""

import logging
import gc
import time
from pathlib import Path
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Central performance optimization manager."""
    
    def __init__(self):
        self.cached_frames = {}  # frame_id -> (PIL.Image, metadata)
        self.memory_limit_mb = 500  # Max memory usage
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # Cleanup every 60 seconds
    
    # ==========================================
    # 1. SQLITE WAL MODE & DATABASE OPTIMIZATION
    # ==========================================
    
    @staticmethod
    def enable_sqlite_wal_mode(db_connection) -> bool:
        """
        Enable WAL (Write-Ahead Logging) mode for better database performance.
        
        Benefits:
        - Better concurrent read/write performance
        - Faster writes (no journal file sync)
        - Safer transactions (atomic commits)
        
        Args:
            db_connection: SQLite connection object
            
        Returns:
            True if successful
        """
        try:
            cursor = db_connection.cursor()
            
            # Enable WAL mode
            cursor.execute("PRAGMA journal_mode=WAL;")
            result = cursor.fetchone()
            logger.info(f"SQLite journal mode: {result[0]}")
            
            # Optimize synchronous mode (faster writes)
            # NORMAL = sync on critical writes only (safe for this use case)
            cursor.execute("PRAGMA synchronous=NORMAL;")
            
            # Increase cache size (2 MB = -2000 pages)
            cursor.execute("PRAGMA cache_size=-2000;")
            
            # Enable foreign keys (for CASCADE deletes)
            cursor.execute("PRAGMA foreign_keys=ON;")
            
            # Optimize temp store (use memory instead of disk)
            cursor.execute("PRAGMA temp_store=MEMORY;")
            
            db_connection.commit()
            
            logger.info("SQLite optimizations enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable SQLite WAL mode: {e}")
            return False
    
    @staticmethod
    def optimize_database(db_connection) -> dict:
        """
        Run full database optimization suite.
        
        Args:
            db_connection: SQLite connection
            
        Returns:
            Dict with optimization results
        """
        try:
            cursor = db_connection.cursor()
            results = {}
            
            # Vacuum database (reclaim unused space)
            logger.info("Running VACUUM...")
            cursor.execute("VACUUM;")
            results['vacuum'] = True
            
            # Analyze tables (update query planner stats)
            logger.info("Running ANALYZE...")
            cursor.execute("ANALYZE;")
            results['analyze'] = True
            
            # Get database size
            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size;")
            page_size = cursor.fetchone()[0]
            
            db_size_mb = (page_count * page_size) / (1024 * 1024)
            results['database_size_mb'] = round(db_size_mb, 2)
            
            logger.info(f"Database optimized: {db_size_mb:.2f} MB")
            return results
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return {'error': str(e)}
    
    # ==========================================
    # 2. FRAME PRE-CACHING
    # ==========================================
    
    def preload_frame(self, frame_id: int, png_path: str, 
                     output_size: tuple) -> bool:
        """
        Pre-load and resize frame template for faster compositing.
        
        This avoids re-loading and resizing the frame PNG for every shot.
        
        Args:
            frame_id: Frame ID for caching
            png_path: Path to frame PNG file
            output_size: (width, height) for final output
            
        Returns:
            True if successfully cached
        """
        try:
            # Load frame image
            frame_image = Image.open(png_path).convert('RGBA')
            
            # Resize to output size (use BILINEAR for speed)
            frame_image = frame_image.resize(output_size, Image.BILINEAR)
            
            # Cache in memory
            self.cached_frames[frame_id] = {
                'image': frame_image,
                'size': output_size,
                'loaded_at': time.time(),
                'png_path': png_path
            }
            
            logger.info(f"Frame {frame_id} pre-cached at {output_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to preload frame {frame_id}: {e}")
            return False
    
    def get_cached_frame(self, frame_id: int) -> Optional[Image.Image]:
        """
        Get pre-cached frame image.
        
        Args:
            frame_id: Frame ID
            
        Returns:
            PIL Image or None if not cached
        """
        if frame_id in self.cached_frames:
            cache = self.cached_frames[frame_id]
            logger.debug(f"Frame cache hit for {frame_id}")
            return cache['image']
        
        logger.debug(f"Frame cache miss for {frame_id}")
        return None
    
    def clear_frame_cache(self, frame_id: Optional[int] = None):
        """
        Clear frame cache to free memory.
        
        Args:
            frame_id: Specific frame to clear, or None to clear all
        """
        if frame_id:
            if frame_id in self.cached_frames:
                del self.cached_frames[frame_id]
                logger.info(f"Cleared frame cache for {frame_id}")
        else:
            count = len(self.cached_frames)
            self.cached_frames.clear()
            logger.info(f"Cleared all frame caches ({count} frames)")
    
    # ==========================================
    # 3. MEMORY CLEANUP & MANAGEMENT
    # ==========================================
    
    def cleanup_memory(self, force: bool = False) -> dict:
        """
        Aggressive memory cleanup to prevent RAM bloat.
        
        Args:
            force: Force cleanup regardless of interval
            
        Returns:
            Dict with cleanup stats
        """
        now = time.time()
        
        # Skip if not enough time passed (unless forced)
        if not force and (now - self.last_cleanup) < self.cleanup_interval:
            return {'skipped': True}
        
        stats = {
            'frames_cleared': 0,
            'objects_collected': 0,
            'memory_freed_mb': 0
        }
        
        try:
            # 1. Clear old frame caches (older than 10 minutes)
            old_frames = []
            for frame_id, cache in self.cached_frames.items():
                age = now - cache['loaded_at']
                if age > 600:  # 10 minutes
                    old_frames.append(frame_id)
            
            for frame_id in old_frames:
                del self.cached_frames[frame_id]
                stats['frames_cleared'] += 1
            
            # 2. Force garbage collection
            stats['objects_collected'] = gc.collect()
            
            # 3. Clear Python's internal free lists
            gc.collect(0)  # Clear young generation
            gc.collect(1)  # Clear middle generation
            gc.collect(2)  # Clear old generation
            
            # 4. Get current memory usage (if psutil available)
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                current_memory = process.memory_info().rss / (1024 * 1024)
                stats['current_memory_mb'] = round(current_memory, 2)
            except:
                pass
            
            self.last_cleanup = now
            
            logger.info(f"Memory cleanup: {stats['frames_cleared']} frames cleared, "
                       f"{stats['objects_collected']} objects collected")
            
            return stats
            
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
            return {'error': str(e)}
    
    def should_cleanup(self) -> bool:
        """Check if memory cleanup should run."""
        return (time.time() - self.last_cleanup) >= self.cleanup_interval
    
    def release_large_objects(self, *objects):
        """
        Safely release large objects from memory.
        
        Args:
            *objects: PIL Images, numpy arrays, or other large objects
        """
        for obj in objects:
            if obj is not None:
                try:
                    # Close PIL images properly
                    if hasattr(obj, 'close'):
                        obj.close()
                    # Delete reference
                    del obj
                except:
                    pass
        
        # Force garbage collection
        gc.collect()
    
    # ==========================================
    # 4. COMPOSITING OPTIMIZATION
    # ==========================================
    
    @staticmethod
    def fast_composite(frame_image: Image.Image, 
                      photo: Image.Image,
                      slot_rect: tuple,
                      fit_mode: str = 'fill') -> Image.Image:
        """
        Fast photo compositing with optimized resize.
        
        Args:
            frame_image: Frame template (RGBA)
            photo: Photo to place (RGB or RGBA)
            slot_rect: (x, y, width, height) for slot
            fit_mode: 'fill', 'fit', or 'stretch'
            
        Returns:
            Composited image
        """
        # Convert photo to RGBA if needed
        if photo.mode != 'RGBA':
            photo = photo.convert('RGBA')
        
        x, y, w, h = slot_rect
        
        # Resize photo based on fit mode
        if fit_mode == 'stretch':
            # Simple stretch (fastest, but distorts)
            photo = photo.resize((w, h), Image.BILINEAR)
        
        elif fit_mode == 'fit':
            # Letterbox (maintains aspect ratio)
            photo.thumbnail((w, h), Image.BILINEAR)
            # Center in slot
            offset_x = (w - photo.width) // 2
            offset_y = (h - photo.height) // 2
            x += offset_x
            y += offset_y
        
        else:  # 'fill' (default)
            # Crop to fill (best for portraits)
            photo_ratio = photo.width / photo.height
            slot_ratio = w / h
            
            if photo_ratio > slot_ratio:
                # Photo is wider - crop sides
                new_width = int(photo.height * slot_ratio)
                left = (photo.width - new_width) // 2
                photo = photo.crop((left, 0, left + new_width, photo.height))
            else:
                # Photo is taller - crop top/bottom
                new_height = int(photo.width / slot_ratio)
                top = (photo.height - new_height) // 2
                photo = photo.crop((0, top, photo.width, top + new_height))
            
            # Resize to slot size
            photo = photo.resize((w, h), Image.BILINEAR)
        
        # Paste photo onto frame using alpha mask
        frame_image.paste(photo, (x, y), photo)
        
        return frame_image
    
    # ==========================================
    # 5. PERFORMANCE MONITORING
    # ==========================================
    
    @staticmethod
    def measure_execution_time(func):
        """
        Decorator to measure function execution time.
        
        Usage:
            @measure_execution_time
            def composite_photos():
                ...
        """
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed = end_time - start_time
            
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
            
            # Warn if too slow
            if elapsed > 3.0:
                logger.warning(f"{func.__name__} is slow: {elapsed:.3f}s")
            
            return result
        
        return wrapper
    
    def get_memory_usage(self) -> float:
        """
        Get current process memory usage in MB.
        
        Returns:
            Memory usage in MB, or -1 if unable to determine
        """
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / (1024 * 1024)
            return round(memory_mb, 2)
        except:
            return -1
    
    def check_memory_limit(self) -> bool:
        """
        Check if memory usage exceeds limit.
        
        Returns:
            True if over limit
        """
        current = self.get_memory_usage()
        if current > 0:
            return current > self.memory_limit_mb
        return False


# Performance optimization presets for different hardware levels
class OptimizationPresets:
    """Pre-configured optimization presets."""
    
    LOW_END_PC = {
        'live_view_fps': 15,
        'frame_skip_rate': 2,  # Process every 2nd frame
        'jpeg_quality': 75,
        'ui_throttle_ms': 66,  # 15 updates/sec
        'preview_resolution': (640, 480),
        'cache_size_mb': 100,
        'memory_limit_mb': 500,
        'use_fast_transformation': True,
        'disable_animations': True
    }
    
    MID_RANGE_PC = {
        'live_view_fps': 20,
        'frame_skip_rate': 1,
        'jpeg_quality': 85,
        'ui_throttle_ms': 50,  # 20 updates/sec
        'preview_resolution': (800, 600),
        'cache_size_mb': 200,
        'memory_limit_mb': 700,
        'use_fast_transformation': True,
        'disable_animations': False
    }
    
    HIGH_END_PC = {
        'live_view_fps': 30,
        'frame_skip_rate': 1,
        'jpeg_quality': 90,
        'ui_throttle_ms': 33,  # 30 updates/sec
        'preview_resolution': (1280, 720),
        'cache_size_mb': 500,
        'memory_limit_mb': 1000,
        'use_fast_transformation': False,
        'disable_animations': False
    }
