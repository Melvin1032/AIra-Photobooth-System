"""AIra Pro Photobooth System - USB Export Module
Detects USB removable drives and copies photos with progress tracking.
Optimized for low-end PCs with background thread processing.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

logger = logging.getLogger(__name__)


class USBExportWorker(QThread):
    """Background worker for USB export."""
    
    progress_updated = pyqtSignal(int, str)  # percentage, status
    export_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, source_paths: List[str], dest_dir: str):
        super().__init__()
        self.source_paths = source_paths
        self.dest_dir = dest_dir
        self.running = True
    
    def run(self):
        """Execute the export operation."""
        try:
            total = len(self.source_paths)
            
            for i, source_path in enumerate(self.source_paths):
                if not self.running:
                    self.export_completed.emit(False, "Export cancelled")
                    return
                
                # Update progress
                progress = int((i / total) * 100)
                filename = Path(source_path).name
                self.progress_updated.emit(progress, f"Copying {filename}...")
                
                # Copy file
                dest_path = Path(self.dest_dir) / filename
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied: {source_path} -> {dest_path}")
            
            self.progress_updated.emit(100, "Export complete!")
            self.export_completed.emit(True, f"Successfully exported {total} files")
            
        except Exception as e:
            logger.error(f"USB export error: {e}")
            self.export_completed.emit(False, f"Export failed: {e}")
    
    def stop(self):
        """Stop the export operation."""
        self.running = False


class USBExporter(QDialog):
    """USB export dialog with drive selection and progress tracking."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export to USB")
        self.setMinimumSize(500, 400)
        self.worker = None
        
        self._setup_ui()
        self._scan_drives()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📱 USB Export")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Drive selection
        layout.addWidget(QLabel("Select USB Drive:"))
        self.drive_list = QListWidget()
        self.drive_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #D4AF37;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #D4AF37;
                color: #000000;
            }
        """)
        layout.addWidget(self.drive_list)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Drives")
        refresh_btn.clicked.connect(self._scan_drives)
        layout.addWidget(refresh_btn)
        
        # Progress section
        self.progress_label = QLabel("Ready to export")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #D4AF37;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #D4AF37;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("📤 Export Photos")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #D4AF37;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFD700;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.export_btn.clicked.connect(self._start_export)
        button_layout.addWidget(self.export_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _scan_drives(self):
        """Scan for removable drives."""
        self.drive_list.clear()
        
        # Windows drive letters
        import string
        from ctypes import windll
        
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive = f"{letter}:\\"
                # Check if removable
                drive_type = windll.kernel32.GetDriveTypeW(drive)
                if drive_type == 2:  # DRIVE_REMOVABLE
                    # Get volume label
                    try:
                        import ctypes
                        buf = ctypes.create_unicode_buffer(1024)
                        windll.kernel32.GetVolumeInformationW(
                            drive, buf, 1024, None, None, None, None, 0
                        )
                        label = buf.value or "Removable Drive"
                        drives.append((drive, label))
                    except:
                        drives.append((drive, "Removable Drive"))
            bitmask >>= 1
        
        if drives:
            for drive, label in drives:
                self.drive_list.addItem(f"{label} ({drive})")
        else:
            self.drive_list.addItem("No USB drives detected")
    
    def export_event(self, event_id: int, session_manager):
        """Export all photos from an event."""
        self.event_id = event_id
        self.session_manager = session_manager
        
        # Get all photos for this event
        self.photos_to_export = []
        sessions = session_manager.get_sessions_for_event(event_id)
        
        for session in sessions:
            photos = session_manager.get_photos_for_session(session['id'])
            for photo in photos:
                if photo.get('raw_path'):
                    self.photos_to_export.append(photo['raw_path'])
                if photo.get('processed_path'):
                    self.photos_to_export.append(photo['processed_path'])
        
        if not self.photos_to_export:
            QMessageBox.information(
                self,
                "No Photos",
                "No photos found for this event."
            )
            return
        
        self.progress_label.setText(f"Ready to export {len(self.photos_to_export)} photos")
        self.exec()
    
    def _start_export(self):
        """Start the export process."""
        if not self.drive_list.currentItem():
            QMessageBox.warning(self, "No Drive", "Please select a USB drive.")
            return
        
        # Extract drive letter from selection
        drive_text = self.drive_list.currentItem().text()
        if "No USB drives" in drive_text:
            QMessageBox.warning(self, "No Drive", "No USB drive selected.")
            return
        
        drive_letter = drive_text.split("(")[1].split(")")[0]
        
        # Create destination directory
        dest_dir = Path(drive_letter) / "AIra_Photobooth_Export"
        dest_dir.mkdir(exist_ok=True)
        
        # Create event subdirectory
        event = self.session_manager.get_event(self.event_id)
        if event:
            event_dir = dest_dir / f"{event['name']}_{event['date']}"
            event_dir.mkdir(exist_ok=True)
            dest_dir = event_dir
        
        # Disable export button
        self.export_btn.setEnabled(False)
        self.export_btn.setText("Exporting...")
        
        # Start worker thread
        self.worker = USBExportWorker(self.photos_to_export, str(dest_dir))
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.export_completed.connect(self._export_completed)
        self.worker.start()
    
    def _update_progress(self, percentage: int, status: str):
        """Update progress bar and label."""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(status)
    
    def _export_completed(self, success: bool, message: str):
        """Handle export completion."""
        self.export_btn.setEnabled(True)
        self.export_btn.setText("📤 Export Photos")
        
        if success:
            QMessageBox.information(self, "Export Complete", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Export Failed", message)
    
    def closeEvent(self, event):
        """Handle dialog close."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)
        event.accept()
