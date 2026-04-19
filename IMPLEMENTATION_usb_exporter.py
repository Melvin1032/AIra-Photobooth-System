"""
SnapFrame Pro - USB Export Module
Detects USB removable drives and copies photos with progress tracking.
Optimized for low-end PCs with background thread processing.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional
from threading import Thread
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class USBExporter(QObject):
    """USB drive detection and file export with progress tracking."""
    
    # Signals
    drive_detected = pyqtSignal(list)  # List of drive info dicts
    export_progress = pyqtSignal(int, int)  # current_bytes, total_bytes
    export_completed = pyqtSignal(str, bool, str)  # file_path, success, message
    export_started = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.usb_drives = []
    
    def detect_usb_drives(self) -> list:
        """
        Detect all connected USB removable drives.
        
        Returns:
            List of dicts with drive info:
            [
                {
                    'drive_letter': 'E:',
                    'mount_point': 'E:\\',
                    'free_space_gb': 45.2,
                    'total_space_gb': 64.0,
                    'label': 'USB DRIVE'
                }
            ]
        """
        try:
            import psutil
            
            usb_drives = []
            partitions = psutil.disk_partitions(all=False)
            
            for partition in partitions:
                # Check if removable drive
                if 'removable' in partition.opts.lower():
                    try:
                        # Get disk usage
                        usage = psutil.disk_usage(partition.mountpoint)
                        
                        # Get drive label if available
                        try:
                            label = self._get_volume_label(partition.mountpoint)
                        except:
                            label = 'USB DRIVE'
                        
                        drive_info = {
                            'drive_letter': partition.device,
                            'mount_point': partition.mountpoint,
                            'free_space_gb': round(usage.free / (1024**3), 2),
                            'total_space_gb': round(usage.total / (1024**3), 2),
                            'free_space_bytes': usage.free,
                            'label': label
                        }
                        
                        usb_drives.append(drive_info)
                        logger.info(f"USB drive detected: {drive_info['drive_letter']} "
                                  f"({drive_info['free_space_gb']} GB free)")
                        
                    except Exception as e:
                        logger.warning(f"Could not access partition {partition.mountpoint}: {e}")
            
            self.usb_drives = usb_drives
            if usb_drives:
                self.drive_detected.emit(usb_drives)
            
            return usb_drives
            
        except ImportError:
            logger.error("psutil not installed. Install with: pip install psutil")
            return []
        except Exception as e:
            logger.error(f"Failed to detect USB drives: {e}")
            return []
    
    def _get_volume_label(self, mount_point: str) -> str:
        """Get volume label for a drive."""
        try:
            # Windows-specific method to get volume label
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            
            volume_name_buffer = ctypes.create_unicode_buffer(1024)
            file_system_name_buffer = ctypes.create_unicode_buffer(1024)
            
            serial_number = ctypes.c_ulong()
            max_component_length = ctypes.c_ulong()
            file_system_flags = ctypes.c_ulong()
            
            result = kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(mount_point),
                volume_name_buffer,
                ctypes.sizeof(volume_name_buffer),
                ctypes.byref(serial_number),
                ctypes.byref(max_component_length),
                ctypes.byref(file_system_flags),
                file_system_name_buffer,
                ctypes.sizeof(file_system_name_buffer)
            )
            
            if result:
                return volume_name_buffer.value or 'USB DRIVE'
            else:
                return 'USB DRIVE'
                
        except:
            return 'USB DRIVE'
    
    def export_to_usb(self, file_path: str, drive_info: dict, 
                     preserve_filename: bool = True) -> None:
        """
        Export file to USB drive in background thread.
        
        Args:
            file_path: Path to file to copy
            drive_info: Drive info dict from detect_usb_drives()
            preserve_filename: If True, keep original filename
        """
        # Run export in background thread
        thread = Thread(
            target=self._export_worker,
            args=(file_path, drive_info, preserve_filename),
            daemon=True
        )
        thread.start()
    
    def _export_worker(self, file_path: str, drive_info: dict,
                      preserve_filename: bool) -> None:
        """Background worker for USB export."""
        try:
            self.export_started.emit()
            
            # Validate source file
            source = Path(file_path)
            if not source.exists():
                self.export_completed.emit(file_path, False, "Source file not found")
                return
            
            # Check file size vs free space
            file_size = source.stat().st_size
            if file_size > drive_info['free_space_bytes']:
                self.export_completed.emit(
                    file_path, False, 
                    f"Insufficient space. Need {file_size / (1024**2):.1f} MB, "
                    f"have {drive_info['free_space_gb']:.1f} GB free"
                )
                return
            
            # Determine destination path
            dest_dir = Path(drive_info['mount_point'])
            
            if preserve_filename:
                dest_path = dest_dir / source.name
            else:
                # Use timestamp-based naming
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = dest_dir / f"SnapFrame_{timestamp}{source.suffix}"
            
            # Check if file already exists on USB
            if dest_path.exists():
                # Add number suffix to avoid overwriting
                counter = 1
                while dest_path.exists():
                    dest_path = dest_dir / f"{source.stem}_{counter}{source.suffix}"
                    counter += 1
            
            # Copy file with progress tracking
            logger.info(f"Exporting to USB: {dest_path}")
            
            # Use shutil.copy2 for preserving metadata
            shutil.copy2(str(source), str(dest_path))
            
            # Verify file was copied
            if dest_path.exists():
                dest_size = dest_path.stat().st_size
                if abs(dest_size - file_size) < 1024:  # Allow 1KB tolerance
                    logger.info(f"Successfully exported to USB: {dest_path}")
                    self.export_completed.emit(
                        file_path, True,
                        f"Saved to {drive_info['drive_letter']}\\{dest_path.name}"
                    )
                else:
                    self.export_completed.emit(
                        file_path, False,
                        "File size mismatch after copy"
                    )
            else:
                self.export_completed.emit(
                    file_path, False,
                    "File not found after copy operation"
                )
            
            # Emit 100% progress
            self.export_progress.emit(file_size, file_size)
            
        except PermissionError as e:
            logger.error(f"USB drive is write-protected: {e}")
            self.export_completed.emit(
                file_path, False,
                "USB drive is write-protected"
            )
        except Exception as e:
            logger.error(f"USB export failed: {e}")
            self.export_completed.emit(
                file_path, False,
                f"Export failed: {str(e)}"
            )
    
    def check_free_space(self, drive_info: dict, required_mb: float) -> bool:
        """
        Check if USB drive has enough free space.
        
        Args:
            drive_info: Drive info dict
            required_mb: Required space in megabytes
            
        Returns:
            True if enough space available
        """
        required_bytes = required_mb * 1024 * 1024
        return drive_info['free_space_bytes'] > required_bytes
    
    def format_drive_info(self, drive_info: dict) -> str:
        """Format drive info for display."""
        return (
            f"{drive_info['drive_letter']} - {drive_info['label']}\n"
            f"Free: {drive_info['free_space_gb']:.1f} GB / "
            f"{drive_info['total_space_gb']:.1f} GB"
        )
