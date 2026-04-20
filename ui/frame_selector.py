"""AIra Pro Photobooth System - Frame Selector
Grid-based frame selection with thumbnails and metadata display.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QGridLayout, QFrame, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QFont, QPen


class FrameSelector(QWidget):
    """Frame selection widget with thumbnail grid."""

    frame_selected = pyqtSignal(int, dict, str)
    frame_deleted = pyqtSignal(int)
    frame_edit_requested = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.frames = {}
        self.selected_frame_id = None
        self.event_id = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("FRAMES")
        self.title_label.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: bold;
            color: #D4AF37;
            letter-spacing: 4px;
            padding: 4px 0px;
            background: transparent;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.add_btn = QPushButton("＋ ADD")
        self.add_btn.setFixedHeight(28)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D4AF37;
                border: 1px solid #D4AF37;
                border-radius: 3px;
                padding: 2px 10px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #D4AF37;
                color: #000000;
            }
        """)
        self.add_btn.clicked.connect(self._on_add_frame)
        header_layout.addWidget(self.add_btn)

        layout.addLayout(header_layout)

        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #2a2a2a;")
        layout.addWidget(divider)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #111;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: #D4AF37;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(2, 4, 2, 4)

        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)

        # Status bar
        self.status_label = QLabel("Select a frame to begin")
        self.status_label.setStyleSheet("""
            color: #555;
            font-size: 10px;
            letter-spacing: 1px;
            padding: 3px 0px;
            background: transparent;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def set_event_id(self, event_id: int):
        self.event_id = event_id
        self.load_frames_for_event(event_id)

    def load_frames_for_event(self, event_id: int):
        self.clear_frames()

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

    def add_frame(self, frame_id: int, name: str, slots: int = 2, price: float = 500, image_path: str = ""):
        metadata = {
            'frame_id': frame_id,
            'frame_name': name,
            'slots': slots,
            'price': price,
            'image_path': image_path
        }
        self.frames[frame_id] = metadata

        card = self._create_frame_card(frame_id, metadata)

        row = (len(self.frames) - 1) // 2
        col = (len(self.frames) - 1) % 2
        self.grid_layout.addWidget(card, row, col)

    def _create_frame_card(self, frame_id: int, metadata: dict) -> QFrame:
        is_selected = (frame_id == self.selected_frame_id)

        card = QFrame()
        card.setFixedSize(148, 190)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        border_color = "#D4AF37" if is_selected else "#2e2e2e"
        bg_color = "#1e1a0e" if is_selected else "#191919"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # Thumbnail
        thumb = QLabel()
        thumb.setFixedSize(132, 100)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet("""
            background-color: #0d0d0d;
            border-radius: 4px;
        """)

        image_path = metadata.get('image_path', '')
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(132, 100,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            else:
                pixmap = self._create_placeholder_thumbnail(frame_id, metadata['frame_name'])
        else:
            pixmap = self._create_placeholder_thumbnail(frame_id, metadata['frame_name'])

        thumb.setPixmap(pixmap)
        layout.addWidget(thumb, alignment=Qt.AlignmentFlag.AlignCenter)

        # Name
        name_label = QLabel(metadata['frame_name'])
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            color: #e8e8e8;
            font-weight: 600;
            font-size: 11px;
            background: transparent;
        """)
        layout.addWidget(name_label)

        # Slots + price row
        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(4)

        slots_label = QLabel(f"✦ {metadata['slots']} shots")
        slots_label.setStyleSheet("color: #666; font-size: 9px; background: transparent;")
        meta_row.addWidget(slots_label)

        meta_row.addStretch()

        price_label = QLabel(f"₱{metadata['price']:.0f}")
        price_label.setStyleSheet("color: #D4AF37; font-weight: bold; font-size: 10px; background: transparent;")
        meta_row.addWidget(price_label)

        layout.addLayout(meta_row)

        card.setProperty("frame_id", frame_id)
        card.mousePressEvent = lambda e, fid=frame_id: self._on_frame_clicked(fid)

        card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos, fid=frame_id: self._show_context_menu(pos, fid)
        )

        return card

    def _create_placeholder_thumbnail(self, frame_id: int, name: str) -> QPixmap:
        pixmap = QPixmap(132, 100)
        pixmap.fill(QColor("#0d0d0d"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor("#2a2a2a"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(6, 6, 120, 88)

        # Inner decorative corners
        cp = QPen(QColor("#D4AF37"))
        cp.setWidth(1)
        painter.setPen(cp)
        clen = 10
        # TL
        painter.drawLine(6, 6, 6 + clen, 6)
        painter.drawLine(6, 6, 6, 6 + clen)
        # BR
        painter.drawLine(126, 94, 126 - clen, 94)
        painter.drawLine(126, 94, 126, 94 - clen)

        painter.setPen(QColor("#333"))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, f"Frame {frame_id}")

        painter.end()
        return pixmap

    def _on_frame_clicked(self, frame_id: int):
        self.selected_frame_id = frame_id
        metadata = self.frames.get(frame_id, {})

        self._update_selection_visuals()

        image_path = metadata.get('image_path', '')
        self.frame_selected.emit(frame_id, metadata, image_path)

        self.status_label.setText(f"✦  {metadata.get('frame_name', 'Unknown')}")
        print(f"[FRAME] Frame {frame_id} selected: {metadata.get('frame_name')}")

    def _update_selection_visuals(self):
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                frame_id = widget.property("frame_id")
                if frame_id == self.selected_frame_id:
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: #1e1a0e;
                            border: 1px solid #D4AF37;
                            border-radius: 6px;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: #191919;
                            border: 1px solid #2e2e2e;
                            border-radius: 6px;
                        }
                        QFrame:hover {
                            background-color: #1d1d1d;
                            border: 1px solid #444;
                            border-radius: 6px;
                        }
                    """)

    def _show_context_menu(self, pos, frame_id: int):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #D4AF37;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: #D4AF37;
                color: #000000;
                border-radius: 3px;
            }
        """)

        edit_action = menu.addAction("✏  Edit Frame")
        delete_action = menu.addAction("✕  Delete Frame")

        action = menu.exec(self.mapToGlobal(pos))

        if action == edit_action:
            self._edit_frame(frame_id)
        elif action == delete_action:
            self._confirm_delete_frame(frame_id)

    def _edit_frame(self, frame_id: int):
        if frame_id not in self.frames:
            return

        metadata = self.frames[frame_id]
        current_name = metadata.get('frame_name', 'Unknown')

        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, "Edit Frame", "Frame name:", text=current_name
        )

        if ok and new_name:
            metadata['frame_name'] = new_name
            self.frames[frame_id] = metadata
            self.frame_edit_requested.emit(frame_id, new_name)
            self.rebuild_grid()
            print(f"[FRAME] Frame {frame_id} renamed to '{new_name}'")

    def _confirm_delete_frame(self, frame_id: int):
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
        if frame_id in self.frames:
            del self.frames[frame_id]
            self.frame_deleted.emit(frame_id)
            self.rebuild_grid()
            print(f"[FRAME] Frame {frame_id} deleted")

    def rebuild_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        frames_list = list(self.frames.items())
        for idx, (frame_id, metadata) in enumerate(frames_list):
            card = self._create_frame_card(frame_id, metadata)
            row = idx // 2
            col = idx % 2
            self.grid_layout.addWidget(card, row, col)

        self.status_label.setText(f"{len(self.frames)} frames available")

    def clear_frames(self):
        self.frames.clear()
        self.selected_frame_id = None

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.status_label.setText("No frames available")

    def _on_add_frame(self):
        if not self.event_id:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return

        from PyQt6.QtWidgets import QFileDialog, QInputDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Frame Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        name, ok = QInputDialog.getText(self, "Frame Name", "Enter frame name:")
        if not ok or not name:
            return

        slots_text, ok = QInputDialog.getText(self, "Number of Shots", "Enter number of shots:", text="2")
        if not ok:
            return

        try:
            slots = int(slots_text)
        except ValueError:
            slots = 2

        price_text, ok = QInputDialog.getText(self, "Price", "Enter price (₱):", text="500")
        if not ok:
            return

        try:
            price = float(price_text)
        except ValueError:
            price = 500.0

        from pathlib import Path
        import shutil

        frames_dir = Path("frames") / f"event_{self.event_id}"
        frames_dir.mkdir(parents=True, exist_ok=True)

        dest_path = frames_dir / Path(file_path).name
        shutil.copy2(file_path, dest_path)

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

            self.load_frames_for_event(self.event_id)
            print(f"[FRAME] Added frame: {name} (ID: {frame_id})")
        finally:
            session_manager.close()
