"""AIra Pro Photobooth System - Viewer Window
Secondary display window for client viewing.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
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

        self._setup_ui()
        self._apply_styling()

        self.show_idle_screen()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setMinimumSize(800, 600)
        layout.addWidget(self.display_label)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #FFD700;
            font-size: 48px;
            font-weight: bold;
            background-color: transparent;
        """)
        self.status_label.hide()
        layout.addWidget(self.status_label)

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
        self.status_label.setText(str(count))
        self.status_label.show()
        self.update_live_preview()
        print(f"[VIEWER] Countdown {count}")

    def show_final_photo(self, photo_path: str):
        self.is_showing_final = True

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
        print("[VIEWER] Showing final photo")

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
