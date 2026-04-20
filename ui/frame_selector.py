"""AIra Pro Photobooth System - Frame Selector
Grid-based frame selection with thumbnails and metadata display.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QGridLayout, QFrame, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor


class FrameSelector(QWidget):
    """Frame selection widget with thumbnail grid."""
    
    frame_selected = pyqtSignal(int, dict, str)  # frame_id, metadata, image_path
    frame_deleted = pyqtSignal(int)  # frame_id
    frame_edit_requested = pyqtSignal(int, str)  # frame_id, new_name
    
    def __init__(self):
        super().__init__()
        
        self.frames = {}  # frame_id -> metadata
        self.selected_frame_id = None
        self.event_id = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("📷 Available Frames")
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #FFD700;
            padding: 5px;
        """)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Add frame button
        self.add_btn = QPushButton("+ Add Frame")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #FFD700;
                border: 2px solid #D4AF37;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D4AF37;
                color: #000000;
            }
        """)
        self.add_btn.clicked.connect(self._on_add_frame)
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area for frame grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #D4AF37;
                border-radius: 6px;
            }
        """)
        
        # Grid container
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)
        
        # Status label
        self.status_label = QLabel("Select a frame to begin")
        self.status_label.setStyleSheet("""
            color: #888;
            font-size: 12px;
            padding: 5px;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def set_event_id(self, event_id: int):
        """Set current event and load its frames."""
        self.event_id = event_id
        self.load_frames_for_event(event_id)
    
    def load_frames_for_event(self, event_id: int):
        """Load frames for a specific event from database."""
        self.clear_frames()
        
        # Import here to avoid circular dependency
        from core.session_manager import SessionManager
        session_manager = SessionManager()
        
        try:
            frames = session_manager.get_frames_for_event(event_id)
            
            for frame_data in frames:
                self.add_frame(
                    frame_id=frame_data["id"],
                    name=frame_data["name"],
                    slots=frame_data["slots"],
                    price=frame_data["price"],
                    image_path=frame_data.get("image_path", "")
                )
            
            self.status_label.setText(f"{len(frames)} frames available")
        finally:
            session_manager.close()
    
    def load_mock_frames(self):
        """Load mock frame data for testing."""
        self.clear_frames()
        
        mock_frames = [
            {"id": 1, "name": "Classic Gold Frame", "slots": 2, "price": 500},
            {"id": 2, "name": "Floral Border", "slots": 1, "price": 500},
            {"id": 3, "name": "Modern Minimalist", "slots": 4, "price": 750},
            {"id": 4, "name": "Vintage Style", "slots": 3, "price": 600},
            {"id": 5, "name": "Elegant Black", "slots": 2, "price": 550},
        ]
        
        for frame_data in mock_frames:
            self.add_frame(
                frame_id=frame_data["id"],
                name=frame_data["name"],
                slots=frame_data["slots"],
                price=frame_data["price"]
            )
        
        self.status_label.setText(f"{len(mock_frames)} frames available")
    
    def add_frame(self, frame_id: int, name: str, slots: int = 2, price: float = 500):
        """Add a frame to the grid."""
        metadata = {
            'frame_id': frame_id,
            'frame_name': name,
            'slots': slots,
            'price': price
        }
        self.frames[frame_id] = metadata
        
        # Create frame card
        card = self._create_frame_card(frame_id, metadata)
        
        # Add to grid
        row = (len(self.frames) - 1) // 2
        col = (len(self.frames) - 1) % 2
        self.grid_layout.addWidget(card, row, col)
    
    def _create_frame_card(self, frame_id: int, metadata: dict) -> QFrame:
        """Create a frame selection card."""
        card = QFrame()
        card.setFixedSize(180, 220)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 2px solid #D4AF37;
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: #3d3d3d;
                border: 3px solid #FFD700;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Thumbnail placeholder
        thumb = QLabel()
        thumb.setFixedSize(150, 120)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create placeholder image with frame number
        pixmap = self._create_placeholder_thumbnail(frame_id, metadata['frame_name'])
        thumb.setPixmap(pixmap)
        thumb.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 6px;
        """)
        layout.addWidget(thumb, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Frame name
        name_label = QLabel(metadata['frame_name'])
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            color: #FFD700;
            font-weight: bold;
            font-size: 12px;
        """)
        layout.addWidget(name_label)
        
        # Slots info
        slots_label = QLabel(f"📷 {metadata['slots']} shot{'s' if metadata['slots'] > 1 else ''}")
        slots_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slots_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(slots_label)
        
        # Price
        price_label = QLabel(f"₱{metadata['price']:.0f}")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        price_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 13px;")
        layout.addWidget(price_label)
        
        # Store reference
        card.setProperty("frame_id", frame_id)
        card.mousePressEvent = lambda e, fid=frame_id: self._on_frame_clicked(fid)
        
        # Context menu
        card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos, fid=frame_id: self._show_context_menu(pos, fid)
        )
        
        return card
    
    def _create_placeholder_thumbnail(self, frame_id: int, name: str) -> QPixmap:
        """Create a placeholder thumbnail image."""
        pixmap = QPixmap(150, 120)
        pixmap.fill(QColor("#1a1a1a"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        painter.setPen(QColor("#D4AF37"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(5, 5, 140, 110)
        
        # Draw frame number
        painter.setPen(QColor("#FFD700"))
        painter.setFont(painter.font())
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, f"Frame {frame_id}")
        
        painter.end()
        return pixmap
    
    def _on_frame_clicked(self, frame_id: int):
        """Handle frame selection."""
        self.selected_frame_id = frame_id
        metadata = self.frames.get(frame_id, {})
        
        # Update visual selection
        self._update_selection_visuals()
        
        # Emit signal
        self.frame_selected.emit(frame_id, metadata, "")
        
        self.status_label.setText(f"Selected: {metadata.get('frame_name', 'Unknown')}")
        print(f"[MOCK] Frame {frame_id} selected: {metadata.get('frame_name')}")
    
    def _update_selection_visuals(self):
        """Update visual selection state of frame cards."""
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                frame_id = widget.property("frame_id")
                if frame_id == self.selected_frame_id:
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: #D4AF37;
                            border: 3px solid #FFD700;
                            border-radius: 10px;
                        }
                    """)
                    # Update text colors for contrast
                    for child in widget.findChildren(QLabel):
                        if "font-weight: bold" in child.styleSheet():
                            child.setStyleSheet("color: #000000; font-weight: bold; font-size: 12px;")
                else:
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: #2d2d2d;
                            border: 2px solid #D4AF37;
                            border-radius: 10px;
                        }
                        QFrame:hover {
                            background-color: #3d3d3d;
                            border: 3px solid #FFD700;
                        }
                    """)
                    # Reset text colors
                    for child in widget.findChildren(QLabel):
                        if "font-weight: bold" in child.styleSheet():
                            child.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 12px;")
    
    def _show_context_menu(self, pos, frame_id: int):
        """Show context menu for frame management."""
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
        
        # Add Edit action
        edit_action = menu.addAction("✏️ Edit Frame")
        
        # Add Delete action
        delete_action = menu.addAction("🗑️ Delete Frame")
        
        action = menu.exec(self.mapToGlobal(pos))
        
        if action == edit_action:
            self._edit_frame(frame_id)
        elif action == delete_action:
            self._confirm_delete_frame(frame_id)
    
    def _edit_frame(self, frame_id: int):
        """Edit frame name."""
        if frame_id not in self.frames:
            return
        
        metadata = self.frames[frame_id]
        current_name = metadata.get('frame_name', 'Unknown')
        
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, "Edit Frame", "Frame name:",
            text=current_name
        )
        
        if ok and new_name:
            metadata['frame_name'] = new_name
            self.frames[frame_id] = metadata
            self.frame_edit_requested.emit(frame_id, new_name)
            self.rebuild_grid()
            print(f"[MOCK] Frame {frame_id} renamed to '{new_name}'")
    
    def _confirm_delete_frame(self, frame_id: int):
        """Confirm and delete frame."""
        from PyQt6.QtWidgets import QMessageBox
        
        metadata = self.frames.get(frame_id, {})
        frame_name = metadata.get('frame_name', 'Unknown')
        
        reply = QMessageBox.question(
            self,
            "Delete Frame",
            f"Are you sure you want to delete '{frame_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_frame(frame_id)
    
    def delete_frame(self, frame_id: int):
        """Delete a frame from the grid."""
        if frame_id in self.frames:
            del self.frames[frame_id]
            self.frame_deleted.emit(frame_id)
            self.rebuild_grid()
            print(f"[MOCK] Frame {frame_id} deleted")
    
    def rebuild_grid(self):
        """Rebuild the frame grid."""
        # Clear existing widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Re-add all frames
        frames_list = list(self.frames.items())
        for idx, (frame_id, metadata) in enumerate(frames_list):
            card = self._create_frame_card(frame_id, metadata)
            row = idx // 2
            col = idx % 2
            self.grid_layout.addWidget(card, row, col)
        
        self.status_label.setText(f"{len(self.frames)} frames available")
    
    def clear_frames(self):
        """Clear all frames from the grid."""
        self.frames.clear()
        self.selected_frame_id = None
        
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.status_label.setText("No frames available")
    
    def _on_add_frame(self):
        """Handle add frame button."""
        if not self.event_id:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return
        
        # Open file dialog to select frame image
        from PyQt6.QtWidgets import QFileDialog, QInputDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Frame Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if not file_path:
            return
        
        # Get frame name
        name, ok = QInputDialog.getText(self, "Frame Name", "Enter frame name:")
        if not ok or not name:
            return
        
        # Get slots
        slots_text, ok = QInputDialog.getText(self, "Number of Shots", "Enter number of shots:", text="2")
        if not ok:
            return
        
        try:
            slots = int(slots_text)
        except ValueError:
            slots = 2
        
        # Get price
        price_text, ok = QInputDialog.getText(self, "Price", "Enter price (₱):", text="500")
        if not ok:
            return
        
        try:
            price = float(price_text)
        except ValueError:
            price = 500.0
        
        # Copy frame to frames directory
        from pathlib import Path
        import shutil
        
        frames_dir = Path("frames") / f"event_{self.event_id}"
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = frames_dir / Path(file_path).name
        shutil.copy2(file_path, dest_path)
        
        # Add to database
        from core.session_manager import SessionManager
        session_manager = SessionManager()
        
        try:
            frame_id = session_manager.add_frame(
                self.event_id,
                name=name,
                image_path=str(dest_path),
                slots=slots,
                price=price
            )
            
            # Reload frames
            self.load_frames_for_event(self.event_id)
            print(f"[FRAME] Added frame: {name} (ID: {frame_id})")
        finally:
            session_manager.close()
