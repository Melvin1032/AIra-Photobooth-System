"""AIra Pro Photobooth System - Print Dialog
Print confirmation and settings dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


class PrintDialog(QDialog):
    """Print confirmation and settings dialog."""
    
    def __init__(self, photo_path: str = None, parent=None):
        super().__init__(parent)
        
        self.photo_path = photo_path
        self.print_copies = 1
        
        self.setWindowTitle("Print Photo")
        self.setMinimumSize(500, 600)
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🖨️ Print Photo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Photo preview
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #D4AF37;
                border-radius: 10px;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_label = QLabel("No photo selected")
        self.preview_label.setFixedSize(400, 300)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            background-color: #0a0a0a;
            border-radius: 8px;
            color: #888;
        """)
        
        if self.photo_path:
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    400, 300,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
        
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview_frame)
        
        # Print settings
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        settings_layout = QVBoxLayout(settings_frame)
        
        # Printer selection
        printer_layout = QHBoxLayout()
        printer_label = QLabel("Printer:")
        printer_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        self.printer_combo = QComboBox()
        self.printer_combo.addItems([
            "Default Printer",
            "Canon SELPHY CP1300",
            "Epson PictureMate",
            "HP Sprocket"
        ])
        self.printer_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #D4AF37;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #D4AF37;
            }
        """)
        printer_layout.addWidget(printer_label)
        printer_layout.addWidget(self.printer_combo)
        settings_layout.addLayout(printer_layout)
        
        # Copies
        copies_layout = QHBoxLayout()
        copies_label = QLabel("Copies:")
        copies_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 10)
        self.copies_spin.setValue(1)
        self.copies_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #D4AF37;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        copies_layout.addWidget(copies_label)
        copies_layout.addWidget(self.copies_spin)
        copies_layout.addStretch()
        settings_layout.addLayout(copies_layout)
        
        # Auto print checkbox
        self.auto_print_check = QCheckBox("Auto-print on capture")
        self.auto_print_check.setStyleSheet("color: #ffffff;")
        settings_layout.addWidget(self.auto_print_check)
        
        layout.addWidget(settings_frame)
        
        # Info label
        info_label = QLabel("💡 This is a UI preview. Printing functionality will be connected to backend.")
        info_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.print_btn = QPushButton("🖨️ Print")
        self.print_btn.setFixedHeight(45)
        self.print_btn.setDefault(True)
        self.print_btn.clicked.connect(self._on_print)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.print_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _apply_styling(self):
        """Apply black/gold styling."""
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #FFD700;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D4AF37;
                color: #000000;
            }
            QPushButton:default {
                background-color: #D4AF37;
                color: #000000;
            }
            QPushButton:default:hover {
                background-color: #FFD700;
            }
        """)
    
    def _on_print(self):
        """Handle print button."""
        self.print_copies = self.copies_spin.value()
        printer = self.printer_combo.currentText()
        
        print(f"[MOCK] Print requested:")
        print(f"  - Printer: {printer}")
        print(f"  - Copies: {self.print_copies}")
        print(f"  - Auto-print: {self.auto_print_check.isChecked()}")
        
        self.accept()
    
    def get_print_settings(self) -> dict:
        """Get selected print settings."""
        return {
            'printer': self.printer_combo.currentText(),
            'copies': self.copies_spin.value(),
            'auto_print': self.auto_print_check.isChecked()
        }
