"""AIra Pro Photobooth System - Countdown Overlay
Animated countdown widget for photo capture.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QRadialGradient, QLinearGradient


class CountdownOverlay(QWidget):
    """Animated countdown overlay for photo capture."""

    countdown_finished = pyqtSignal()
    countdown_tick = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.countdown_seconds = 3
        self.current_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_countdown)

        # Animation pulse
        self._pulse = 0
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.setInterval(30)

        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.count_label = QLabel("3")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("color: transparent; background-color: transparent;")
        font = QFont("Georgia", 180, QFont.Weight.Bold)
        self.count_label.setFont(font)

        self.subtitle_label = QLabel("GET READY")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            color: rgba(255,255,255,0.9);
            background-color: transparent;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 8px;
        """)

        layout.addStretch()
        layout.addWidget(self.count_label)
        layout.addSpacing(8)
        layout.addWidget(self.subtitle_label)
        layout.addStretch()

    def start_countdown(self, seconds: int = 3):
        self.countdown_seconds = seconds
        self.current_count = seconds
        self._pulse = 0

        self._update_display()
        self.show()
        self.raise_()

        self._pulse_timer.start()
        self.timer.start(1000)
        print(f"[COUNTDOWN] Countdown started: {seconds} seconds")

    def _update_countdown(self):
        self.current_count -= 1
        self._pulse = 0

        if self.current_count > 0:
            self._update_display()
            self.countdown_tick.emit(self.current_count)
        else:
            self._finish_countdown()

    def _update_pulse(self):
        self._pulse = min(self._pulse + 3, 100)
        self.update()

    def _update_display(self):
        self.count_label.setText(str(self.current_count))
        if self.current_count > 1:
            self.subtitle_label.setText("GET READY")
        elif self.current_count == 1:
            self.subtitle_label.setText("SMILE ✦")
        else:
            self.subtitle_label.setText("CAPTURING…")

    def _finish_countdown(self):
        self.timer.stop()
        self._pulse_timer.stop()
        self.count_label.setText("✓")
        self.subtitle_label.setText("CAPTURED")

        QTimer.singleShot(600, self.hide)
        self.countdown_finished.emit()
        print("[COUNTDOWN] Countdown finished - capture triggered")

    def cancel_countdown(self):
        self.timer.stop()
        self._pulse_timer.stop()
        self.hide()
        print("[COUNTDOWN] Countdown cancelled")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Deep black semi-transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 200))

        cx = self.width() // 2
        cy = self.height() // 2
        r = min(self.width(), self.height()) // 3

        # Outer glow ring (pulsing)
        pulse_r = r + int(self._pulse * 0.25)
        glow = QRadialGradient(cx, cy, pulse_r + 20)
        glow.setColorAt(0.7, QColor(212, 175, 55, 0))
        glow.setColorAt(0.85, QColor(212, 175, 55, 60))
        glow.setColorAt(1.0, QColor(212, 175, 55, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - pulse_r - 20, cy - pulse_r - 20,
                            (pulse_r + 20) * 2, (pulse_r + 20) * 2)

        # Gold ring
        pen = QPen(QColor("#D4AF37"))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Inner thin ring
        pen2 = QPen(QColor(255, 215, 0, 80))
        pen2.setWidth(1)
        painter.setPen(pen2)
        painter.drawEllipse(cx - r + 8, cy - r + 8, (r - 8) * 2, (r - 8) * 2)

        # Draw number with gold gradient
        count_text = self.count_label.text()
        font = QFont("Georgia", int(r * 0.9), QFont.Weight.Bold)
        painter.setFont(font)
        grad = QLinearGradient(cx, cy - r // 2, cx, cy + r // 2)
        grad.setColorAt(0.0, QColor("#FFD700"))
        grad.setColorAt(0.5, QColor("#D4AF37"))
        grad.setColorAt(1.0, QColor("#B8860B"))
        painter.setPen(QPen(QBrush(grad), 1))
        painter.drawText(self.rect().adjusted(0, -40, 0, 0),
                         Qt.AlignmentFlag.AlignCenter, count_text)

        # Corner brackets
        blen = 20
        boff = 12
        bracket_pen = QPen(QColor("#D4AF37"))
        bracket_pen.setWidth(2)
        painter.setPen(bracket_pen)
        # TL
        painter.drawLine(boff, boff, boff + blen, boff)
        painter.drawLine(boff, boff, boff, boff + blen)
        # TR
        painter.drawLine(self.width() - boff, boff, self.width() - boff - blen, boff)
        painter.drawLine(self.width() - boff, boff, self.width() - boff, boff + blen)
        # BL
        painter.drawLine(boff, self.height() - boff, boff + blen, self.height() - boff)
        painter.drawLine(boff, self.height() - boff, boff, self.height() - boff - blen)
        # BR
        painter.drawLine(self.width() - boff, self.height() - boff,
                         self.width() - boff - blen, self.height() - boff)
        painter.drawLine(self.width() - boff, self.height() - boff,
                         self.width() - boff, self.height() - boff - blen)

        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # keep count_label invisible — we paint manually
        self.count_label.setStyleSheet("color: transparent; background-color: transparent;")
