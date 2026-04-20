"""AIra Pro Photobooth System - CSV Export Module
Exports session data to CSV format for reporting and accounting.
Optimized for low-end PCs using built-in csv module (no pandas required).
"""

import csv
import logging
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


class CSVExporter(QDialog):
    """CSV export dialog with options for session data export."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export to CSV")
        self.setMinimumSize(400, 300)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 CSV Export")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Export session data to CSV format for reporting and accounting.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Options
        layout.addSpacing(10)
        layout.addWidget(QLabel("Export Options:"))
        
        self.include_photos = QCheckBox("Include photo count")
        self.include_photos.setChecked(True)
        layout.addWidget(self.include_photos)
        
        self.include_payment = QCheckBox("Include payment details")
        self.include_payment.setChecked(True)
        layout.addWidget(self.include_payment)
        
        self.include_timestamp = QCheckBox("Include timestamps")
        self.include_timestamp.setChecked(True)
        layout.addWidget(self.include_timestamp)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 Export to CSV")
        export_btn.setStyleSheet("""
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
        """)
        export_btn.clicked.connect(self._export)
        button_layout.addWidget(export_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def export_sessions(self, event_id: int, session_manager):
        """Export sessions for an event to CSV."""
        self.event_id = event_id
        self.session_manager = session_manager
        
        # Get event info
        event = session_manager.get_event(event_id)
        if event:
            self.event_name = event['name']
            self.event_date = event['date']
        else:
            self.event_name = "Unknown"
            self.event_date = ""
        
        self.exec()
    
    def _export(self):
        """Execute the CSV export."""
        # Get save location
        default_name = f"AIra_Sessions_{self.event_name}_{self.event_date}.csv"
        default_name = default_name.replace(" ", "_").replace("/", "-")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV File",
            default_name,
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            # Get sessions
            sessions = self.session_manager.get_sessions_for_event(self.event_id)
            
            # Prepare CSV data
            headers = ["Session ID", "Client Name", "Frame", "Shots Taken"]
            
            if self.include_payment.isChecked():
                headers.extend(["Amount", "Payment Status"])
            
            if self.include_timestamp.isChecked():
                headers.append("Created At")
            
            if self.include_photos.isChecked():
                headers.append("Photo Count")
            
            rows = []
            for session in sessions:
                row = [
                    session['id'],
                    session['client_name'] or "Anonymous",
                    session.get('frame_name', 'Unknown'),
                    session['shots_taken'] or 0
                ]
                
                if self.include_payment.isChecked():
                    row.extend([
                        session['amount'] or 0,
                        session['payment_status'] or 'Unpaid'
                    ])
                
                if self.include_timestamp.isChecked():
                    row.append(session['created_at'])
                
                if self.include_photos.isChecked():
                    photos = self.session_manager.get_photos_for_session(session['id'])
                    row.append(len(photos))
                
                rows.append(row)
            
            # Write CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            
            logger.info(f"CSV exported: {file_path}")
            QMessageBox.information(
                self,
                "Export Complete",
                f"Successfully exported {len(rows)} sessions to:\n{file_path}"
            )
            self.accept()
            
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export CSV:\n{e}"
            )


def quick_export_sessions(event_id: int, session_manager, output_path: str):
    """Quick export sessions to CSV without UI.
    
    Args:
        event_id: Event ID to export
        session_manager: SessionManager instance
        output_path: Path to save CSV file
    
    Returns:
        bool: True if successful
    """
    try:
        sessions = session_manager.get_sessions_for_event(event_id)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Session ID", "Client Name", "Frame", 
                "Shots Taken", "Amount", "Payment Status", "Created At"
            ])
            
            for session in sessions:
                writer.writerow([
                    session['id'],
                    session['client_name'] or "Anonymous",
                    session.get('frame_name', 'Unknown'),
                    session['shots_taken'] or 0,
                    session['amount'] or 0,
                    session['payment_status'] or 'Unpaid',
                    session['created_at']
                ])
        
        logger.info(f"Quick CSV export: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Quick export failed: {e}")
        return False
