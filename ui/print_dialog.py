"""AIra Pro Photobooth System - Print Dialog
Print confirmation and settings dialog.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QCheckBox, QFrame, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QPen
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo

logger = logging.getLogger(__name__)


class PrintDialog(QDialog):
    """Print confirmation and settings dialog."""

    def __init__(self, photo_path: str = None, parent=None):
        super().__init__(parent)

        self.photo_path = photo_path
        self.print_copies = 1

        self.setWindowTitle("Print Photo")
        self.setMinimumSize(480, 580)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title bar
        title_bar = QFrame()
        title_bar.setFixedHeight(52)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #0d0d0d;
                border-bottom: 1px solid #2a2a2a;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 16, 0)

        title_label = QLabel("PRINT PHOTO")
        title_label.setStyleSheet("""
            color: #D4AF37;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 4px;
            background: transparent;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #555;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover { color: #ef5350; }
        """)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)

        layout.addWidget(title_bar)

        # Body
        body = QWidget()
        body.setStyleSheet("background-color: #111111;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(16)

        # Photo preview
        preview_container = QFrame()
        preview_container.setFixedHeight(260)
        preview_container.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
            }
        """)
        preview_inner = QVBoxLayout(preview_container)
        preview_inner.setContentsMargins(8, 8, 8, 8)

        self.preview_label = QLabel("No photo selected")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            background-color: transparent;
            color: #333;
            font-size: 12px;
            letter-spacing: 1px;
        """)

        if self.photo_path:
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    440, 244,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)

        preview_inner.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(preview_container)

        # Settings
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #151515;
                border: 1px solid #1e1e1e;
                border-radius: 4px;
            }
        """)
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(16, 12, 16, 12)
        settings_layout.setSpacing(10)

        LABEL_STYLE = "color: #888; font-size: 10px; letter-spacing: 2px; font-weight: bold; background: transparent;"
        COMBO_STYLE = """
            QComboBox {
                background-color: #0d0d0d;
                color: #e0e0e0;
                border: 1px solid #2a2a2a;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QComboBox:focus { border-color: #D4AF37; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #D4AF37;
            }
            QComboBox QAbstractItemView {
                background-color: #151515;
                color: #e0e0e0;
                selection-background-color: #D4AF37;
                selection-color: #000;
                border: 1px solid #2a2a2a;
            }
        """

        # Printer row
        printer_layout = QHBoxLayout()
        printer_label = QLabel("PRINTER")
        printer_label.setStyleSheet(LABEL_STYLE)
        printer_label.setFixedWidth(70)
        self.printer_combo = QComboBox()
        self.printer_combo.setStyleSheet(COMBO_STYLE)
        self._load_printers()
        printer_layout.addWidget(printer_label)
        printer_layout.addWidget(self.printer_combo)
        settings_layout.addLayout(printer_layout)

        # Copies row
        copies_layout = QHBoxLayout()
        copies_label = QLabel("COPIES")
        copies_label.setStyleSheet(LABEL_STYLE)
        copies_label.setFixedWidth(70)

        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 10)
        self.copies_spin.setValue(1)
        self.copies_spin.setFixedWidth(80)
        self.copies_spin.setStyleSheet("""
            QSpinBox {
                background-color: #0d0d0d;
                color: #e0e0e0;
                border: 1px solid #2a2a2a;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QSpinBox:focus { border-color: #D4AF37; }
            QSpinBox::up-button, QSpinBox::down-button { width: 20px; }
        """)
        copies_layout.addWidget(copies_label)
        copies_layout.addWidget(self.copies_spin)
        copies_layout.addStretch()
        settings_layout.addLayout(copies_layout)

        # Auto print
        self.auto_print_check = QCheckBox("Auto-print on capture")
        self.auto_print_check.setStyleSheet("""
            QCheckBox {
                color: #555;
                font-size: 11px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 14px; height: 14px;
                border: 1px solid #333;
                border-radius: 2px;
                background: #0d0d0d;
            }
            QCheckBox::indicator:checked {
                background: #D4AF37;
                border-color: #D4AF37;
            }
        """)
        settings_layout.addWidget(self.auto_print_check)

        body_layout.addWidget(settings_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #555;
                border: 1px solid #2a2a2a;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:hover { color: #888; border-color: #444; }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        self.print_btn = QPushButton("PRINT")
        self.print_btn.setFixedHeight(40)
        self.print_btn.setDefault(True)
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #D4AF37;
                color: #000000;
                border: none;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 3px;
            }
            QPushButton:hover { background-color: #FFD700; }
            QPushButton:pressed { background-color: #B8860B; }
            QPushButton:disabled { background-color: #2a2a2a; color: #444; }
        """)
        self.print_btn.clicked.connect(self._on_print)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.print_btn)
        body_layout.addLayout(btn_layout)

        layout.addWidget(body)

    def _apply_styling(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #111111;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
            }
        """)

    def _load_printers(self):
        self.printer_combo.clear()

        printers = QPrinterInfo.availablePrinters()
        printer_names = [p.printerName() for p in printers]

        if printer_names:
            self.printer_combo.addItems(printer_names)
            default = QPrinterInfo.defaultPrinter()
            if default:
                index = self.printer_combo.findText(default.printerName())
                if index >= 0:
                    self.printer_combo.setCurrentIndex(index)
        else:
            self.printer_combo.addItem("No printers found")
            self.print_btn.setEnabled(False)

    def _on_print(self):
        if not self.photo_path:
            QMessageBox.warning(self, "No Photo", "No photo selected for printing.")
            return

        self.print_copies = self.copies_spin.value()
        printer_name = self.printer_combo.currentText()

        printer = QPrinter()
        if printer_name and printer_name != "No printers found":
            printer.setPrinterName(printer_name)

        printer.setCopyCount(self.print_copies)

        print_dialog = QPrintDialog(printer, self)

        if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self._perform_print(printer)

        self.accept()

    def _perform_print(self, printer: QPrinter):
        try:
            pixmap = QPixmap(self.photo_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Error", "Could not load photo for printing.")
                return

            painter = QPainter(printer)
            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)

            scaled_pixmap = pixmap.scaled(
                page_rect.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            x = (page_rect.width() - scaled_pixmap.width()) // 2
            y = (page_rect.height() - scaled_pixmap.height()) // 2

            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()

            logger.info(f"Printed {self.photo_path} with {self.print_copies} copies")
            QMessageBox.information(self, "Print Complete",
                                    f"Photo sent to printer.\nCopies: {self.print_copies}")

        except Exception as e:
            logger.error(f"Print error: {e}")
            QMessageBox.critical(self, "Print Error", f"Failed to print:\n{e}")

    def get_print_settings(self) -> dict:
        return {
            'printer': self.printer_combo.currentText(),
            'copies': self.copies_spin.value(),
            'auto_print': self.auto_print_check.isChecked()
        }
