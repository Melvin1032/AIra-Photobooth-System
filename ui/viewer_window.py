"""
SnapFrame Pro - Viewer Window
Secondary display window for client viewing.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont


class ViewerWindow(QMainWindow):
    """Secondary window for client photo viewing."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("SnapFrame Pro - Viewer Display")
        self.setMinimumSize(800, 600)
        
        # State
        self.frame_overlay_pixmap = None
        self.current_pixmap = None
        self.is_showing_final = False
        
        self._setup_ui()
        self._apply_styling()
        
        # Show idle screen initially
        self.show_idle_screen()
    
    def _setup_ui(self):
        """Setup the viewer window UI."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main display label
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setMinimumSize(800, 600)
        layout.addWidget(self.display_label)
        
        # Status overlay (for countdown, messages)
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
        """Apply black/gold styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QLabel {
                background-color: #0a0a0a;
                color: #ffffff;
            }
        """)
    
    def show_idle_screen(self):
        """Show idle/attract screen."""
        self.is_showing_final = False
        
        # Create idle screen with logo/message
        pixmap = QPixmap(800, 600)
        pixmap.fill(QColor("#0a0a0a"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw decorative border
        pen = painter.pen()
        pen.setColor(QColor("#D4AF37"))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(20, 20, 760, 560)
        
        # Draw title
        painter.setPen(QColor("#FFD700"))
        font = QFont("Segoe UI", 48, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "📷 SnapFrame Pro")
        
        # Draw subtitle
        font = QFont("Segoe UI", 24)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        rect = pixmap.rect().adjusted(0, 100, 0, 0)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Touch screen to start!")
        
        painter.end()
        
        self.display_label.setPixmap(pixmap)
        self.status_label.hide()
        print("[MOCK] Viewer: Showing idle screen")
    
    def update_live_preview(self, frame_data: bytes = None):
        """Update live preview display with actual camera feed."""
        if self.is_showing_final:
            return
        
        if frame_data:
            # Load actual camera frame
            pixmap = QPixmap()
            pixmap.loadFromData(frame_data)
            if not pixmap.isNull():
                # Scale to fit display while maintaining aspect ratio
                label_size = self.display_label.size()
                scaled = pixmap.scaled(
                    label_size.width(),
                    label_size.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.display_label.setPixmap(scaled)
                return
        
        # Fallback to placeholder if no frame data
        pixmap = QPixmap(800, 600)
        pixmap.fill(QColor("#1a1a1a"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor("#666"))
        font = QFont("Segoe UI", 24)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "📷 Waiting for camera...")
        painter.end()
        
        self.display_label.setPixmap(pixmap)
    
    def set_frame_overlay(self, frame_path: str):
        """Set frame overlay image."""
        if frame_path:
            self.frame_overlay_pixmap = QPixmap(frame_path)
        else:
            self.frame_overlay_pixmap = None
    
    def show_countdown(self, count: int):
        """Show countdown number."""
        self.status_label.setText(str(count))
        self.status_label.show()
        
        # Update display with countdown overlay
        self.update_live_preview()
        print(f"[MOCK] Viewer: Countdown {count}")
    
    def show_final_photo(self, photo_path: str):
        """Show final captured/composited photo."""
        self.is_showing_final = True
        
        pixmap = QPixmap(photo_path)
        if pixmap.isNull():
            # Create placeholder
            pixmap = QPixmap(800, 600)
            pixmap.fill(QColor("#1a1a1a"))
            
            painter = QPainter(pixmap)
            painter.setPen(QColor("#FFD700"))
            font = QFont("Segoe UI", 36)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "📷 Final Photo\n(Mock)")
            painter.end()
        else:
            # Scale to fit
            pixmap = pixmap.scaled(
                800, 600,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        
        self.display_label.setPixmap(pixmap)
        self.status_label.hide()
        print("[MOCK] Viewer: Showing final photo")
    
    def clear_final_photo(self):
        """Clear final photo and return to live preview."""
        self.is_showing_final = False
        self.show_idle_screen()
        print("[MOCK] Viewer: Cleared final photo")
    
    def show_message(self, message: str, duration: int = 3000):
        """Show a temporary message."""
        self.status_label.setText(message)
        self.status_label.show()
        
        QTimer.singleShot(duration, self.status_label.hide)
        print(f"[MOCK] Viewer: Message '{message}'")
    
    def closeEvent(self, event):
        """Handle window close - hide instead of close."""
        event.ignore()
        self.hide()
        print("[MOCK] Viewer window hidden (not closed)")
