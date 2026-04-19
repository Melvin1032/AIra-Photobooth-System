"""AIra Pro Photobooth System - Session Log Table
Professional session history table with edit/delete actions.
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, 
    QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap


class SessionLogTable(QTableWidget):
    """Session log table with photo previews and action buttons."""
    
    reprint_requested = pyqtSignal(int)  # session_id
    delete_requested = pyqtSignal(int)  # session_id
    edit_requested = pyqtSignal(int)  # session_id
    
    def __init__(self):
        super().__init__()
        
        # Setup columns - add Photo preview and Actions columns
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels([
            "ID", "Client", "Frame", "Photo", "Shots", 
            "Payment", "Status", "Time", "Actions"
        ])
        
        # Setup header with professional styling
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Client
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Frame
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Photo (80px)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Shots
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Payment
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Time
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)  # Actions (120px)
        
        self.setColumnWidth(3, 80)   # Photo
        self.setColumnWidth(8, 120)  # Actions
        
        # Row height
        self.verticalHeader().setDefaultSectionSize(60)
        
        # Hide vertical header
        self.verticalHeader().setVisible(False)
        
        # Enable alternating row colors
        self.setAlternatingRowColors(True)
        
        # Selection behavior
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Store photo preview widgets
        self.photo_previews = {}
        
        # Apply professional styling
        self.apply_stylesheet()
    
    def apply_stylesheet(self):
        """Apply professional black/gold styling."""
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                gridline-color: #2d2d2d;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #FFD700;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #D4AF37;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #2d2d2d;
            }
            QTableWidget::item:selected {
                background-color: #D4AF37;
                color: #000000;
            }
            QTableWidget::item:alternate {
                background-color: #252525;
            }
        """)
    
    def add_session(self, session_id: int, client_name: str, frame_name: str,
                    amount: float = 0.0, payment_status: str = "Unpaid", 
                    shots: int = 0, status: str = "Completed", timestamp: str = ""):
        """Add session to table."""
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        # Format timestamp if provided
        if not timestamp:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add items with proper formatting
        items = [
            str(session_id),
            client_name or "Anonymous",
            frame_name,
            "",  # Photo preview (widget will be added)
            str(shots),
            f"₱{amount:.0f}",
            payment_status,
            timestamp
        ]
        
        for col, text in enumerate(items):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row_position, col, item)
        
        # Add photo preview placeholder
        photo_label = QLabel("No Photo")
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_label.setStyleSheet("""
            border: 2px dashed #666;
            border-radius: 6px;
            background-color: #1a1a1a;
            color: #888;
            font-size: 10px;
        """)
        self.setCellWidget(row_position, 3, photo_label)
        self.photo_previews[row_position] = photo_label
        
        # Add action buttons
        self._add_action_buttons(row_position, session_id)
    
    def _add_action_buttons(self, row: int, session_id: int):
        """Add edit and delete buttons to actions column."""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(2, 2, 2, 2)
        actions_layout.setSpacing(4)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Edit Session")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(session_id))
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setToolTip("Delete Session")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(session_id))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addStretch()
        
        self.setCellWidget(row, 8, actions_widget)
    
    def update_photo_preview(self, session_id: int, photo_path: str):
        """Update photo preview for a session."""
        # Find row with matching session ID
        for row in range(self.rowCount()):
            if self.item(row, 0).text() == str(session_id):
                pixmap = QPixmap(photo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        70, 50,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    # Update label with gold border
                    self.photo_previews[row].setPixmap(scaled_pixmap)
                    self.photo_previews[row].setText("")
                    self.photo_previews[row].setStyleSheet(
                        "border: 2px solid #FFD700; border-radius: 6px; background-color: #000;"
                    )
                break
    
    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        item = self.itemAt(event.pos())
        if item:
            row = item.row()
            session_id = int(self.item(row, 0).text())
            
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #D4AF37;
                }
                QMenu::item:selected {
                    background-color: #D4AF37;
                    color: #000000;
                }
            """)
            
            edit_action = menu.addAction("✏️ Edit Session")
            delete_action = menu.addAction("🗑️ Delete Session")
            menu.addSeparator()
            reprint_action = menu.addAction("🖨️ Reprint")
            
            action = menu.exec(self.mapToGlobal(event.pos()))
            
            if action == edit_action:
                self.edit_requested.emit(session_id)
            elif action == delete_action:
                self.delete_requested.emit(session_id)
            elif action == reprint_action:
                self.reprint_requested.emit(session_id)
    
    def load_mock_data(self):
        """Load sample session data for testing."""
        mock_sessions = [
            {"id": 1, "client": "John Doe", "frame": "Classic Gold", "amount": 500, 
             "payment": "Paid", "shots": 3, "status": "Completed", "time": "14:30:25"},
            {"id": 2, "client": "Jane Smith", "frame": "Floral Border", "amount": 500, 
             "payment": "Unpaid", "shots": 2, "status": "Pending", "time": "14:45:10"},
            {"id": 3, "client": "Michael Chen", "frame": "Modern Minimalist", "amount": 750, 
             "payment": "Paid", "shots": 4, "status": "Completed", "time": "15:00:33"},
            {"id": 4, "client": "Sarah Wilson", "frame": "Classic Gold", "amount": 500, 
             "payment": "Paid", "shots": 2, "status": "Completed", "time": "15:15:45"},
            {"id": 5, "client": "Robert Brown", "frame": "Vintage Style", "amount": 600, 
             "payment": "Unpaid", "shots": 3, "status": "Pending", "time": "15:30:12"},
            {"id": 6, "client": "Emily Davis", "frame": "Floral Border", "amount": 500, 
             "payment": "Paid", "shots": 2, "status": "Completed", "time": "15:45:28"},
            {"id": 7, "client": "David Martinez", "frame": "Modern Minimalist", "amount": 750, 
             "payment": "Paid", "shots": 4, "status": "Completed", "time": "16:00:55"},
            {"id": 8, "client": "Lisa Anderson", "frame": "Classic Gold", "amount": 500, 
             "payment": "Unpaid", "shots": 2, "status": "Pending", "time": "16:15:18"},
            {"id": 9, "client": "James Taylor", "frame": "Vintage Style", "amount": 600, 
             "payment": "Paid", "shots": 3, "status": "Completed", "time": "16:30:42"},
            {"id": 10, "client": "Maria Garcia", "frame": "Floral Border", "amount": 500, 
             "payment": "Paid", "shots": 2, "status": "Completed", "time": "16:45:05"},
        ]
        
        for session in mock_sessions:
            self.add_session(
                session_id=session["id"],
                client_name=session["client"],
                frame_name=session["frame"],
                amount=session["amount"],
                payment_status=session["payment"],
                shots=session["shots"],
                status=session["status"],
                timestamp=session["time"]
            )
