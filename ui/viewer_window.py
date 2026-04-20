"""AIra Pro Photobooth System - Viewer Window
Secondary display window for client viewing.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QPen, QRadialGradient


class ViewerWindow(QMainWindow):
    """Secondary window for client photo viewing."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AIra Pro — Client Display")
        self.setMinimumSize(800, 600)

        self.frame_overlay_pixmap = None
        self.current_pixmap = None
        self.is_showing_final = False
        self.qr_pixmap = None
        self.qr_visible = True  # QR visibility controlled by operator
        self.show_qr_code = False
        self.raw_mode = False  # Raw photo mode (no frame overlay)
        self.current_photo_path = None

        self._setup_ui()
        self._apply_styling()

        self.show_idle_screen()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side - photo display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setMinimumSize(800, 600)
        left_layout.addWidget(self.display_label)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #FFD700;
            font-size: 48px;
            font-weight: bold;
            background-color: transparent;
        """)
        self.status_label.hide()
        left_layout.addWidget(self.status_label)

        # Countdown overlay (separate from status_label)
        self.countdown_overlay_label = QLabel(self.display_label)
        self.countdown_overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_overlay_label.setStyleSheet("""
            color: #FFD700;
            font-size: 120px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 160);
            border-radius: 30px;
        """)
        self.countdown_overlay_label.hide()

        main_layout.addWidget(left_widget, stretch=1)

        # Right side - QR code panel (hidden by default)
        self.qr_widget = QWidget()
        self.qr_widget.setFixedWidth(280)
        self.qr_widget.setStyleSheet("background-color: #0a0a0a;")
        
        qr_layout = QVBoxLayout(self.qr_widget)
        qr_layout.setContentsMargins(15, 30, 15, 30)
        qr_layout.setSpacing(20)
        qr_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top spacer for vertical centering
        qr_layout.addStretch(1)

        # Photo preview label
        photo_preview_title = QLabel("Your Photo")
        photo_preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_preview_title.setStyleSheet("""
            color: #D4AF37;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
            margin-bottom: 5px;
        """)
        qr_layout.addWidget(photo_preview_title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Photo preview (small thumbnail) - centered
        self.qr_photo_preview = QLabel()
        self.qr_photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_photo_preview.setStyleSheet("""
            background-color: #0d0d0d;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 3px;
        """)
        self.qr_photo_preview.setFixedSize(180, 135)
        self.qr_photo_preview.setScaledContents(True)
        qr_layout.addWidget(self.qr_photo_preview, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer between photo and QR
        qr_layout.addSpacing(25)

        # Separator line
        separator = QLabel()
        separator.setFixedSize(180, 1)
        separator.setStyleSheet("background-color: #2a2a2a;")
        qr_layout.addWidget(separator, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer after separator
        qr_layout.addSpacing(20)

        # QR Code label
        qr_title = QLabel("Scan to Download")
        qr_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_title.setStyleSheet("""
            color: #D4AF37;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
            margin-bottom: 5px;
        """)
        qr_layout.addWidget(qr_title, alignment=Qt.AlignmentFlag.AlignCenter)

        # QR Code image - centered with white background
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setStyleSheet("""
            background-color: white;
            border: 3px solid #D4AF37;
            border-radius: 8px;
            padding: 10px;
        """)
        self.qr_label.setFixedSize(260, 260)
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer before footer
        qr_layout.addSpacing(15)

        # Footer text
        footer_text = QLabel("AIra Photobooth")
        footer_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_text.setStyleSheet("""
            color: #555;
            font-size: 9px;
            letter-spacing: 1px;
            background: transparent;
        """)
        qr_layout.addWidget(footer_text, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bottom spacer for vertical centering
        qr_layout.addStretch(1)

        self.qr_widget.hide()
        main_layout.addWidget(self.qr_widget)

    def _apply_styling(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #030303; }
            QLabel { background-color: #030303; color: #ffffff; }
        """)

    def show_idle_screen(self):
        self.is_showing_final = False

        w, h = 800, 600
        pixmap = self._make_idle_pixmap(w, h)
        self.display_label.setPixmap(pixmap)
        self.status_label.hide()
        print("[VIEWER] Showing idle screen")

    def _make_idle_pixmap(self, w: int, h: int) -> QPixmap:
        pixmap = QPixmap(w, h)
        pixmap.fill(QColor("#030303"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Subtle radial glow in center
        glow = QRadialGradient(w // 2, h // 2, 300)
        glow.setColorAt(0.0, QColor(212, 175, 55, 20))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(0, 0, w, h, glow)

        # Outer border
        pen = QPen(QColor("#1e1e1e"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(16, 16, w - 32, h - 32)

        # Corner accents
        gold_pen = QPen(QColor("#D4AF37"))
        gold_pen.setWidth(2)
        painter.setPen(gold_pen)
        clen = 28
        off = 16
        # TL
        painter.drawLine(off, off, off + clen, off)
        painter.drawLine(off, off, off, off + clen)
        # TR
        painter.drawLine(w - off, off, w - off - clen, off)
        painter.drawLine(w - off, off, w - off, off + clen)
        # BL
        painter.drawLine(off, h - off, off + clen, h - off)
        painter.drawLine(off, h - off, off, h - off - clen)
        # BR
        painter.drawLine(w - off, h - off, w - off - clen, h - off)
        painter.drawLine(w - off, h - off, w - off, h - off - clen)

        # Center diamond ornament
        diamond_pen = QPen(QColor("#2a2a2a"))
        diamond_pen.setWidth(1)
        painter.setPen(diamond_pen)
        cx, cy, ds = w // 2, h // 2 - 40, 6
        points_x = [cx, cx + ds, cx, cx - ds]
        points_y = [cy - ds, cy, cy + ds, cy]
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QPolygon
        poly = QPolygon([QPoint(points_x[i], points_y[i]) for i in range(4)])
        painter.drawPolygon(poly)

        # Logo text
        painter.setPen(QColor("#D4AF37"))
        font = QFont("Georgia", 36, QFont.Weight.Bold)
        painter.setFont(font)
        text_rect = pixmap.rect().adjusted(0, -60, 0, -60)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "AIra Pro")

        # Subtitle
        font2 = QFont("Segoe UI", 11)
        painter.setFont(font2)
        painter.setPen(QColor("#444"))
        sub_rect = pixmap.rect().adjusted(0, 40, 0, 40)
        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, "PHOTOBOOTH  ✦  PROFESSIONAL SERIES")

        # Bottom tagline
        font3 = QFont("Segoe UI", 9)
        painter.setFont(font3)
        painter.setPen(QColor("#2a2a2a"))
        bottom_rect = pixmap.rect().adjusted(0, 160, 0, 160)
        painter.drawText(bottom_rect, Qt.AlignmentFlag.AlignCenter, "touch screen to begin")

        painter.end()
        return pixmap

    def update_live_preview(self, frame_data: bytes = None):
        if self.is_showing_final:
            return

        if frame_data:
            pixmap = QPixmap()
            pixmap.loadFromData(frame_data)
            if not pixmap.isNull():
                label_size = self.display_label.size()
                scaled = pixmap.scaled(
                    label_size.width(),
                    label_size.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                if self.frame_overlay_pixmap and not self.frame_overlay_pixmap.isNull():
                    final_pixmap = QPixmap(scaled)
                    painter = QPainter(final_pixmap)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                    overlay_scaled = self.frame_overlay_pixmap.scaled(
                        final_pixmap.width(),
                        final_pixmap.height(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )

                    x = (final_pixmap.width() - overlay_scaled.width()) // 2
                    y = (final_pixmap.height() - overlay_scaled.height()) // 2
                    painter.drawPixmap(x, y, overlay_scaled)
                    painter.end()
                    scaled = final_pixmap

                self.display_label.setPixmap(scaled)
                return

        # Fallback
        pixmap = QPixmap(800, 600)
        pixmap.fill(QColor("#030303"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#222"))
        font = QFont("Segoe UI", 14)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Waiting for camera…")
        painter.end()
        self.display_label.setPixmap(pixmap)

    def set_frame_overlay(self, frame_path: str):
        if frame_path:
            self.frame_overlay_pixmap = QPixmap(frame_path)
        else:
            self.frame_overlay_pixmap = None

    def show_countdown(self, count: int):
        """Show countdown number on viewer display as overlay."""
        self.is_showing_final = False
        
        # Position the countdown overlay in center of display
        display_rect = self.display_label.geometry()
        overlay_size = 200
        x = (display_rect.width() - overlay_size) // 2
        y = (display_rect.height() - overlay_size) // 2
        self.countdown_overlay_label.setGeometry(x, y, overlay_size, overlay_size)
        
        # Set the countdown number
        self.countdown_overlay_label.setText(str(count))
        self.countdown_overlay_label.show()
        self.countdown_overlay_label.raise_()
        
        # Hide after 900ms
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(900, self._hide_countdown_overlay)
        print(f"[VIEWER] Countdown {count}")
    
    def _hide_countdown_overlay(self):
        """Hide the countdown overlay."""
        self.countdown_overlay_label.hide()

    def show_final_photo(self, photo_path: str, show_qr: bool = False):
        self.is_showing_final = True
        self.current_photo_path = photo_path

        pixmap = QPixmap(photo_path)
        if pixmap.isNull():
            pixmap = QPixmap(800, 600)
            pixmap.fill(QColor("#030303"))
            painter = QPainter(pixmap)
            painter.setPen(QColor("#D4AF37"))
            font = QFont("Georgia", 30)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "✓  Photo Captured")
            painter.end()
        else:
            pixmap = pixmap.scaled(
                800, 600,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        self.display_label.setPixmap(pixmap)
        self.status_label.hide()
        
        # Update QR photo preview
        if not pixmap.isNull():
            preview_pixmap = pixmap.scaled(
                200, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.qr_photo_preview.setPixmap(preview_pixmap)
        
        # Show QR code if enabled
        self._update_qr_visibility()
            
        print("[VIEWER] Showing final photo")
    
    def _update_qr_visibility(self):
        """Update QR code visibility based on settings."""
        if self.qr_visible and self.qr_pixmap and self.is_showing_final:
            self.qr_label.setPixmap(self.qr_pixmap)
            self.qr_widget.show()
        else:
            self.qr_widget.hide()
    
    def set_qr_visible(self, visible: bool):
        """Set QR code visibility (controlled by operator)."""
        self.qr_visible = visible
        self._update_qr_visibility()
        print(f"[VIEWER] QR visibility: {'ON' if visible else 'OFF'}")

    def set_qr_code(self, qr_image):
        """Set QR code image to display."""
        if qr_image:
            # Convert PIL Image to QPixmap
            from PIL.ImageQt import ImageQt
            qimage = ImageQt(qr_image)
            self.qr_pixmap = QPixmap.fromImage(qimage)
            # Display QR at 230px to fit in 260px label with 10px padding + 3px border (total 46px margin)
            self.qr_label.setPixmap(self.qr_pixmap.scaled(230, 230, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        else:
            self.qr_pixmap = None

    def toggle_raw_mode(self, enabled: bool):
        """Toggle raw photo mode (no frame overlay)."""
        self.raw_mode = enabled
        print(f"[VIEWER] Raw mode: {'ON' if enabled else 'OFF'}")

    def clear_final_photo(self):
        self.is_showing_final = False
        self.show_idle_screen()
        print("[VIEWER] Cleared final photo")

    def show_message(self, message: str, duration: int = 3000):
        self.status_label.setText(message)
        self.status_label.show()
        QTimer.singleShot(duration, self.status_label.hide)
        print(f"[VIEWER] Message '{message}'")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        print("[VIEWER] Window hidden (not closed)")
