"""AIra Pro Photobooth System - Session Log Table
Professional session history table with edit/delete actions.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont


class SessionLogTable(QTableWidget):
    """Session log table with photo previews and action buttons."""

    reprint_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    edit_requested = pyqtSignal(int)
    download_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setColumnCount(9)
        self.setHorizontalHeaderLabels([
            "ID", "CLIENT", "FRAME", "PHOTO", "SHOTS",
            "PAYMENT", "STATUS", "TIME", "ACTIONS"
        ])

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(3, 72)
        self.setColumnWidth(8, 128)

        self.verticalHeader().setDefaultSectionSize(64)
        self.verticalHeader().setVisible(False)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setShowGrid(False)

        self.photo_previews = {}

        self.apply_stylesheet()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                color: #d0d0d0;
                border: none;
                gridline-color: transparent;
                font-family: 'Segoe UI';
                font-size: 12px;
                outline: none;
            }
            QHeaderView {
                background-color: #111111;
            }
            QHeaderView::section {
                background-color: #111111;
                color: #D4AF37;
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid #2a2a2a;
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QTableWidget::item {
                padding: 6px 12px;
                border-bottom: 1px solid #1a1a1a;
            }
            QTableWidget::item:selected {
                background-color: #1e1a0e;
                color: #FFD700;
                border-left: 2px solid #D4AF37;
            }
            QTableWidget::item:alternate {
                background-color: #151515;
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

    def add_session(self, session_id: int, client_name: str, frame_name: str,
                    amount: float = 0.0, payment_status: str = "Unpaid",
                    shots: int = 0, status: str = "Completed", timestamp: str = "",
                    photo_path: str = None):
        row_position = self.rowCount()
        self.insertRow(row_position)

        if not timestamp:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M")

        # Payment badge color
        payment_color = {"Paid": "#27ae60", "Unpaid": "#c0392b", "Partial": "#e67e22"}.get(payment_status, "#888")

        items = [
            (str(session_id), "#555"),
            (client_name or "Anonymous", "#e8e8e8"),
            (frame_name, "#aaaaaa"),
            ("", None),  # Photo widget
            (str(shots), "#888"),
            (f"₱{amount:.0f}", "#D4AF37"),
            (payment_status, payment_color),
            (timestamp, "#555"),
        ]

        for col, (text, color) in enumerate(items):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if color:
                item.setForeground(QColor(color))
            self.setItem(row_position, col, item)

        # Photo preview
        photo_label = QLabel()
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_label.setFixedSize(70, 62)

        if photo_path and Path(photo_path).exists():
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(64, 56,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                photo_label.setPixmap(scaled)
                photo_label.setStyleSheet("""
                    border: 1px solid #D4AF37;
                    border-radius: 3px;
                    background-color: #0d0d0d;
                    padding: 1px;
                """)
            else:
                photo_label.setText("—")
                photo_label.setStyleSheet("color: #333; font-size: 16px;")
        else:
            photo_label.setText("—")
            photo_label.setStyleSheet("color: #333; font-size: 16px;")

        self.setCellWidget(row_position, 3, photo_label)
        self.photo_previews[row_position] = photo_label

        self._add_action_buttons(row_position, session_id)

    def _add_action_buttons(self, row: int, session_id: int):
        actions_widget = QWidget()
        actions_widget.setStyleSheet("background: transparent;")
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 4, 4, 4)
        actions_layout.setSpacing(4)

        BTN_STYLE = """
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 3px;
                font-size: {fs}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
        """

        edit_btn = QPushButton("✏")
        edit_btn.setFixedSize(30, 30)
        edit_btn.setToolTip("Edit")
        edit_btn.setStyleSheet(BTN_STYLE.format(
            bg="#1c3a5a", fg="#64b5f6", hover="#1e4d7a", fs=13
        ))
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(session_id))

        delete_btn = QPushButton("✕")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setToolTip("Delete")
        delete_btn.setStyleSheet(BTN_STYLE.format(
            bg="#3a1a1a", fg="#ef5350", hover="#4e2020", fs=12
        ))
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(session_id))

        download_btn = QPushButton("PNG")
        download_btn.setFixedSize(44, 30)
        download_btn.setToolTip("Download as PNG")
        download_btn.setStyleSheet(BTN_STYLE.format(
            bg="#1a3a25", fg="#66bb6a", hover="#1e4e30", fs=9
        ))
        download_btn.clicked.connect(lambda: self.download_requested.emit(session_id))

        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addWidget(download_btn)
        actions_layout.addStretch()

        self.setCellWidget(row, 8, actions_widget)

    def update_photo_preview(self, session_id: int, photo_path: str):
        for row in range(self.rowCount()):
            if self.item(row, 0).text() == str(session_id):
                pixmap = QPixmap(photo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        64, 56,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.photo_previews[row].setPixmap(scaled_pixmap)
                    self.photo_previews[row].setText("")
                    self.photo_previews[row].setStyleSheet(
                        "border: 1px solid #D4AF37; border-radius: 3px; background: #0d0d0d; padding: 1px;"
                    )
                break

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            row = item.row()
            session_id = int(self.item(row, 0).text())

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
                    color: #000;
                    border-radius: 3px;
                }
                QMenu::separator {
                    height: 1px;
                    background: #2a2a2a;
                    margin: 3px 10px;
                }
            """)

            edit_action = menu.addAction("✏  Edit Session")
            delete_action = menu.addAction("✕  Delete Session")
            menu.addSeparator()
            reprint_action = menu.addAction("⎙  Reprint")

            action = menu.exec(self.mapToGlobal(event.pos()))

            if action == edit_action:
                self.edit_requested.emit(session_id)
            elif action == delete_action:
                self.delete_requested.emit(session_id)
            elif action == reprint_action:
                self.reprint_requested.emit(session_id)

    def clear_sessions(self):
        self.setRowCount(0)
        self.photo_previews.clear()

    def load_mock_data(self):
        mock_sessions = [
            {"id": 1, "client": "John Doe", "frame": "Classic Gold", "amount": 500,
             "payment": "Paid", "shots": 3, "status": "Completed", "time": "14:30"},
            {"id": 2, "client": "Jane Smith", "frame": "Floral Border", "amount": 500,
             "payment": "Unpaid", "shots": 2, "status": "Pending", "time": "14:45"},
            {"id": 3, "client": "Michael Chen", "frame": "Modern Minimalist", "amount": 750,
             "payment": "Paid", "shots": 4, "status": "Completed", "time": "15:00"},
            {"id": 4, "client": "Sarah Wilson", "frame": "Classic Gold", "amount": 500,
             "payment": "Paid", "shots": 2, "status": "Completed", "time": "15:15"},
            {"id": 5, "client": "Robert Brown", "frame": "Vintage Style", "amount": 600,
             "payment": "Unpaid", "shots": 3, "status": "Pending", "time": "15:30"},
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
