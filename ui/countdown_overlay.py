"""
SnapFrame Pro - Countdown Overlay
Animated countdown widget for photo capture.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush


class CountdownOverlay(QWidget):
    """Animated countdown overlay for photo capture."""
    
    countdown_finished = pyqtSignal()
    countdown_tick = pyqtSignal(int)  # remaining seconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.countdown_seconds = 3
        self.current_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_countdown)
        
        self._setup_ui()
        self.hide()
    
    def _setup_ui(self):
        """Setup the overlay UI."""
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Countdown label
        self.count_label = QLabel("3")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("""
            color: #FFD700;
            background-color: transparent;
        """)
        font = QFont("Segoe UI", 200, QFont.Weight.Bold)
        self.count_label.setFont(font)
        
        # Subtitle label
        self.subtitle_label = QLabel("Get Ready!")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            color: #ffffff;
            background-color: transparent;
            font-size: 36px;
            font-weight: bold;
        """)
        
        layout.addStretch()
        layout.addWidget(self.count_label)
        layout.addWidget(self.subtitle_label)
        layout.addStretch()
    
    def start_countdown(self, seconds: int = 3):
        """Start the countdown animation."""
        self.countdown_seconds = seconds
        self.current_count = seconds
        
        self._update_display()
        self.show()
        self.raise_()
        
        # Update every second
        self.timer.start(1000)
        print(f"[MOCK] Countdown started: {seconds} seconds")
    
    def _update_countdown(self):
        """Update countdown display."""
        self.current_count -= 1
        
        if self.current_count > 0:
            self._update_display()
            self.countdown_tick.emit(self.current_count)
        else:
            self._finish_countdown()
    
    def _update_display(self):
        """Update the countdown display."""
        self.count_label.setText(str(self.current_count))
        
        # Change subtitle based on count
        if self.current_count > 1:
            self.subtitle_label.setText("Get Ready!")
        elif self.current_count == 1:
            self.subtitle_label.setText("Smile!")
        else:
            self.subtitle_label.setText("Capturing...")
    
    def _finish_countdown(self):
        """Finish the countdown."""
        self.timer.stop()
        self.count_label.setText("✓")
        self.subtitle_label.setText("Captured!")
        
        # Hide after brief delay
        QTimer.singleShot(500, self.hide)
        self.countdown_finished.emit()
        print("[MOCK] Countdown finished - capture triggered")
    
    def cancel_countdown(self):
        """Cancel the countdown."""
        self.timer.stop()
        self.hide()
        print("[MOCK] Countdown cancelled")
    
    def paintEvent(self, event):
        """Paint semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent black background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        
        # Draw gold border
        pen = QPen(QColor("#D4AF37"))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect().adjusted(10, 10, -10, -10))
        
        painter.end()
    
    def resizeEvent(self, event):
        """Handle resize - adjust font size."""
        super().resizeEvent(event)
        
        # Adjust font size based on window size
        min_dim = min(self.width(), self.height())
        font_size = int(min_dim * 0.3)
        
        font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
        self.count_label.setFont(font)
