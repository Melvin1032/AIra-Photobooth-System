"""
SnapFrame Pro - Operator Window
Main operator dashboard with complete UI.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFrame, QSplitter,
    QMessageBox, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QFont

from config import config
from ui.frame_selector import FrameSelector
from ui.session_log_table import SessionLogTable
from ui.countdown_overlay import CountdownOverlay
from ui.print_dialog import PrintDialog
from ui.viewer_window import ViewerWindow
from core.camera import CameraManager
from core.compositor import ImageCompositor
from core.session_manager import SessionManager


class OperatorWindow(QMainWindow):
    """Main operator dashboard window."""
    
    capture_requested = pyqtSignal()
    countdown_started = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"{config.app_name} v{config.version} - Operator Dashboard")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # State
        self.current_event_id = None
        self.current_frame_id = None
        self.current_frame_metadata = None
        self.captured_photos = []
        self.current_slot_index = 0
        self.is_countdown_active = False
        self.is_dark_mode = True
        self.preview_mode = "live"  # "live", "countdown", "review"
        
        # Review timer
        self.review_timer = QTimer()
        self.review_timer.setSingleShot(True)
        self.review_timer.timeout.connect(self._return_to_live_preview)
        
        # Viewer window
        self.viewer_window = None
        
        # Core components
        self.camera_manager = CameraManager()
        self.compositor = ImageCompositor()
        self.session_manager = SessionManager()
        
        # Camera preview timer - 30 FPS for smoothness
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._update_preview)
        self.preview_timer.setInterval(33)  # ~30 FPS
        
        # Available cameras list
        self.available_cameras = []
        self.current_camera_index = 0
        self.camera_combo = None  # Will be created in UI
        
        self._setup_ui()
        self._apply_theme()
        self._load_mock_data()
        self._initialize_camera()
    
    def _setup_ui(self):
        """Setup the complete UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # === TOP BAR ===
        main_layout.addWidget(self._create_top_bar())
        
        # === MAIN CONTENT AREA ===
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel - Frame Selection
        left_panel = self._create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Center Panel - Preview & Controls
        center_panel = self._create_center_panel()
        content_splitter.addWidget(center_panel)
        
        # Right Panel - Session Info
        right_panel = self._create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([300, 700, 400])
        
        main_layout.addWidget(content_splitter, stretch=1)
        
        # === BOTTOM BAR - Session Log ===
        main_layout.addWidget(self._create_bottom_panel())
    
    def _create_top_bar(self) -> QFrame:
        """Create the top navigation bar."""
        bar = QFrame()
        bar.setFixedHeight(70)
        bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:0.5 #2d2d2d, stop:1 #1a1a1a);
                border-bottom: 3px solid #D4AF37;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Logo/Title
        title = QLabel(f"📷 {config.app_name}")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #FFD700;
            background: transparent;
        """)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Event label - minimal styling
        self.event_label = QLabel("Event: Not Selected")
        self.event_label.setStyleSheet("""
            font-size: 14px;
            color: #cccccc;
            background: transparent;
            padding: 5px 12px;
            border: 1px solid #444;
            border-radius: 4px;
        """)
        layout.addWidget(self.event_label)
        
        layout.addStretch()
        
        # Event management buttons (hidden initially)
        self.edit_event_btn = QPushButton("✏️ Edit Event")
        self.edit_event_btn.setFixedHeight(40)
        self.edit_event_btn.setVisible(False)
        self.edit_event_btn.clicked.connect(self._edit_current_event)
        layout.addWidget(self.edit_event_btn)
        
        self.delete_event_btn = QPushButton("🗑️ Delete Event")
        self.delete_event_btn.setFixedHeight(40)
        self.delete_event_btn.setVisible(False)
        self.delete_event_btn.clicked.connect(self._delete_current_event)
        layout.addWidget(self.delete_event_btn)
        
        layout.addSpacing(10)
        
        # Theme toggle
        self.theme_btn = QPushButton("🌙 Dark")
        self.theme_btn.setFixedHeight(40)
        self.theme_btn.setFixedWidth(100)
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)
        
        # Camera selector dropdown
        layout.addSpacing(10)
        camera_label = QLabel("📷 Camera:")
        camera_label.setStyleSheet("color: #cccccc; background: transparent;")
        layout.addWidget(camera_label)
        
        self.camera_combo = QComboBox()
        self.camera_combo.setFixedHeight(40)
        self.camera_combo.setFixedWidth(250)
        self.camera_combo.setStyleSheet("""
            QComboBox {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #D4AF37;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: #ffffff;
                selection-background-color: #D4AF37;
                selection-color: #000000;
            }
        """)
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        layout.addWidget(self.camera_combo)
        
        # Refresh camera button
        refresh_camera_btn = QPushButton("🔄")
        refresh_camera_btn.setFixedSize(40, 40)
        refresh_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #333;
                border-color: #D4AF37;
            }
        """)
        refresh_camera_btn.setToolTip("Refresh camera list")
        refresh_camera_btn.clicked.connect(self._refresh_cameras)
        layout.addWidget(refresh_camera_btn)
        
        layout.addSpacing(10)
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(50, 50)
        settings_btn.setStyleSheet("font-size: 20px;")
        settings_btn.clicked.connect(self._show_settings)
        layout.addWidget(settings_btn)
        
        return bar
    
    def _create_left_panel(self) -> QFrame:
        """Create the left panel with frame selector."""
        panel = QFrame()
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(350)
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Panel title - minimal gold
        title = QLabel("🖼️ Frame Selection")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #D4AF37;
            padding: 5px;
            border-bottom: 1px solid #3d3d3d;
        """)
        layout.addWidget(title)
        
        # Frame selector
        self.frame_selector = FrameSelector()
        self.frame_selector.frame_selected.connect(self._on_frame_selected)
        self.frame_selector.frame_deleted.connect(self._on_frame_deleted)
        self.frame_selector.frame_edit_requested.connect(self._on_frame_edit)
        layout.addWidget(self.frame_selector)
        
        return panel
    
    def _create_center_panel(self) -> QFrame:
        """Create the center panel with preview and controls."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Preview area - maximize container, minimal border
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 1px solid #2d2d2d;
                border-radius: 4px;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(2, 2, 2, 2)
        preview_layout.setSpacing(0)
        
        self.preview_label = QLabel("📷 Live Preview")
        # Set 16:9 aspect ratio (1280x720 scaled down)
        self.preview_label.setMinimumSize(640, 360)
        self.preview_label.setSizePolicy(
            self.preview_label.sizePolicy().horizontalPolicy().Expanding,
            self.preview_label.sizePolicy().verticalPolicy().Expanding
        )
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            background-color: #000000;
            color: #444;
            font-size: 18px;
        """)
        preview_layout.addWidget(self.preview_label, stretch=1)
        
        # Countdown overlay
        self.countdown_overlay = CountdownOverlay(self.preview_label)
        self.countdown_overlay.countdown_finished.connect(self._on_countdown_finished)
        
        layout.addWidget(preview_frame, stretch=1)
        
        # Selected frame info - minimal styling
        self.selected_frame_label = QLabel("Frame: Not Selected")
        self.selected_frame_label.setStyleSheet("""
            font-size: 13px;
            color: #cccccc;
            padding: 6px;
            background-color: #252525;
            border-radius: 4px;
        """)
        self.selected_frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.selected_frame_label)
        
        # Shot status - minimal styling
        self.shot_status = QLabel("Ready to capture")
        self.shot_status.setStyleSheet("""
            font-size: 14px;
            color: #4CAF50;
            font-weight: bold;
            padding: 8px;
            background-color: #252525;
            border-radius: 4px;
        """)
        self.shot_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.shot_status)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.capture_btn = QPushButton("📸 CAPTURE")
        self.capture_btn.setFixedHeight(60)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #D4AF37, stop:1 #FFD700);
                color: #000000;
                border: 3px solid #FFD700;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:1 #D4AF37);
            }
            QPushButton:pressed {
                background-color: #B8860B;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
                border-color: #666;
            }
        """)
        self.capture_btn.clicked.connect(self._on_capture_clicked)
        controls_layout.addWidget(self.capture_btn, stretch=2)
        
        self.print_btn = QPushButton("🖨️ Print")
        self.print_btn.setFixedHeight(60)
        self.print_btn.clicked.connect(self._on_print_clicked)
        controls_layout.addWidget(self.print_btn, stretch=1)
        
        self.viewer_btn = QPushButton("👁️ Viewer")
        self.viewer_btn.setFixedHeight(60)
        self.viewer_btn.clicked.connect(self._toggle_viewer)
        controls_layout.addWidget(self.viewer_btn, stretch=1)
        
        layout.addLayout(controls_layout)
        
        return panel
    
    def _create_right_panel(self) -> QFrame:
        """Create the right panel with session info."""
        panel = QFrame()
        panel.setMinimumWidth(250)
        panel.setMaximumWidth(350)
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Panel title - minimal gold
        title = QLabel("👤 Session Info")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #D4AF37;
            padding: 5px;
            border-bottom: 1px solid #3d3d3d;
        """)
        layout.addWidget(title)
        
        # Client name input - minimal styling
        client_label = QLabel("Client Name:")
        client_label.setStyleSheet("color: #aaaaaa; font-weight: bold;")
        layout.addWidget(client_label)
        
        self.client_name_input = QLineEdit()
        self.client_name_input.setPlaceholderText("Enter client name...")
        self.client_name_input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #D4AF37;
            }
        """)
        layout.addWidget(self.client_name_input)
        
        # Payment status - minimal styling
        payment_label = QLabel("Payment Status:")
        payment_label.setStyleSheet("color: #aaaaaa; font-weight: bold;")
        layout.addWidget(payment_label)
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Unpaid", "Paid", "Partial"])
        self.payment_combo.setStyleSheet("""
            QComboBox {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: #ffffff;
                selection-background-color: #D4AF37;
            }
        """)
        layout.addWidget(self.payment_combo)
        
        # Session stats - minimal styling
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        self.shots_taken_label = QLabel("Shots: 0 / 0")
        self.shots_taken_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        stats_layout.addWidget(self.shots_taken_label)
        
        self.amount_label = QLabel("Amount: ₱0")
        self.amount_label.setStyleSheet("color: #4CAF50; font-size: 13px; font-weight: bold;")
        stats_layout.addWidget(self.amount_label)
        
        layout.addWidget(stats_frame)
        
        # Action buttons
        layout.addSpacing(20)
        
        new_session_btn = QPushButton("🆕 New Session")
        new_session_btn.setFixedHeight(45)
        new_session_btn.clicked.connect(self._on_new_session)
        layout.addWidget(new_session_btn)
        
        usb_export_btn = QPushButton("💾 USB Export")
        usb_export_btn.setFixedHeight(45)
        usb_export_btn.clicked.connect(self._on_usb_export)
        layout.addWidget(usb_export_btn)
        
        csv_export_btn = QPushButton("📊 CSV Export")
        csv_export_btn.setFixedHeight(45)
        csv_export_btn.clicked.connect(self._on_csv_export)
        layout.addWidget(csv_export_btn)
        
        layout.addStretch()
        
        return panel
    
    def _create_bottom_panel(self) -> QFrame:
        """Create the bottom panel with session log."""
        panel = QFrame()
        panel.setMinimumHeight(200)
        panel.setMaximumHeight(300)
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Panel title with button - minimal gold
        header_layout = QHBoxLayout()
        
        title = QLabel("📋 Session Log")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #D4AF37;
            padding: 5px;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        create_event_btn = QPushButton("➕ Create Event")
        create_event_btn.setFixedHeight(35)
        create_event_btn.clicked.connect(self._on_create_event)
        header_layout.addWidget(create_event_btn)
        
        load_event_btn = QPushButton("📂 Load Event")
        load_event_btn.setFixedHeight(35)
        load_event_btn.clicked.connect(self._on_load_event)
        header_layout.addWidget(load_event_btn)
        
        layout.addLayout(header_layout)
        
        # Session log table
        self.session_log = SessionLogTable()
        self.session_log.reprint_requested.connect(self._on_reprint)
        self.session_log.delete_requested.connect(self._on_delete_session)
        self.session_log.edit_requested.connect(self._on_edit_session)
        layout.addWidget(self.session_log)
        
        return panel
    
    def _apply_theme(self):
        """Apply the current theme (dark/light)."""
        if self.is_dark_mode:
            self.setStyleSheet(self._get_dark_stylesheet())
            self.theme_btn.setText("🌙 Dark")
        else:
            self.setStyleSheet(self._get_light_stylesheet())
            self.theme_btn.setText("☀️ Light")
    
    def _get_dark_stylesheet(self) -> str:
        """Get dark theme stylesheet - minimal professional."""
        return """
            QMainWindow {
                background-color: #0a0a0a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #252525;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
                border-color: #D4AF37;
                color: #D4AF37;
            }
            QPushButton:pressed {
                background-color: #D4AF37;
                color: #000000;
            }
            QLabel {
                background-color: transparent;
            }
            QLineEdit {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
            }
        """
    
    def _get_light_stylesheet(self) -> str:
        """Get light theme stylesheet - minimal professional."""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #ffffff;
                color: #000000;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #D4AF37;
                color: #8B6914;
            }
            QLabel {
                background-color: transparent;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
            }
        """
    
    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        try:
            self.is_dark_mode = not self.is_dark_mode
            self._apply_theme()
            
            # Update component styles - check if methods exist
            if hasattr(self.frame_selector, 'apply_stylesheet'):
                self.frame_selector.apply_stylesheet()
            if hasattr(self.session_log, 'apply_stylesheet'):
                self.session_log.apply_stylesheet()
            
            # Update theme button text
            self.theme_btn.setText("🌙 Dark" if self.is_dark_mode else "☀️ Light")
            
            print(f"[THEME] Changed to: {'Dark' if self.is_dark_mode else 'Light'}")
        except Exception as e:
            print(f"[ERROR] Theme toggle failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_mock_data(self):
        """Load mock data for testing."""
        # Load mock sessions
        self.session_log.load_mock_data()
        
        # Load mock frames
        self.frame_selector.load_mock_frames()
    
    def _initialize_camera(self):
        """Initialize camera and start preview."""
        try:
            # Detect and populate available cameras, but don't auto-start
            # The camera will be started after UI is fully ready
            self._refresh_cameras(auto_start=False)
            
            # Now start the camera once
            if self.available_cameras:
                selected_idx = self.camera_combo.currentIndex()
                if selected_idx < 0:
                    selected_idx = 0
                    self.camera_combo.setCurrentIndex(0)
                
                camera_id = self.available_cameras[selected_idx][0]
                self._start_camera(camera_id)
            else:
                print("[CAMERA] No cameras detected - using mock mode")
                self.shot_status.setText("No camera - Mock mode")
            
        except Exception as e:
            print(f"[CAMERA] Error initializing: {e}")
            self.shot_status.setText("Camera error - Mock mode")
    
    def _refresh_cameras(self, auto_start=True):
        """Detect and populate available cameras in the dropdown.
        
        Args:
            auto_start: Whether to automatically start the first camera (default True)
        """
        # Stop current camera if running
        was_running = self.camera_manager.is_running()
        current_camera_id = None
        if was_running:
            current_camera_id = self.camera_manager.current_camera_id
            self.camera_manager.stop_camera()
        
        # Detect available cameras
        self.available_cameras = self.camera_manager.detect_cameras()
        
        # Block signals to prevent triggering _on_camera_changed while populating
        self.camera_combo.blockSignals(True)
        
        # Clear and repopulate dropdown
        self.camera_combo.clear()
        
        if self.available_cameras:
            print(f"[CAMERA] Detected {len(self.available_cameras)} camera(s):")
            for idx, (cam_id, cam_name) in enumerate(self.available_cameras):
                print(f"  - [{cam_id}] {cam_name}")
                self.camera_combo.addItem(cam_name, cam_id)
                
                # Select previously used camera if available
                if current_camera_id is not None and cam_id == current_camera_id:
                    self.camera_combo.setCurrentIndex(idx)
            
            # If no camera was selected, select the first one
            if self.camera_combo.currentIndex() < 0 and self.camera_combo.count() > 0:
                self.camera_combo.setCurrentIndex(0)
            
            # Re-enable signals
            self.camera_combo.blockSignals(False)
            
            # Only auto-start if requested (prevents double-start on init)
            if auto_start:
                # Start camera (either previous one or first available)
                selected_idx = self.camera_combo.currentIndex()
                camera_id = self.available_cameras[selected_idx][0]
                self._start_camera(camera_id)
        else:
            self.camera_combo.addItem("No cameras found")
            self.camera_combo.setEnabled(False)
            self.camera_combo.blockSignals(False)
            print("[CAMERA] No cameras detected - using mock mode")
            self.shot_status.setText("No camera - Mock mode")
    
    def _start_camera(self, camera_id: int):
        """Start camera with given ID."""
        # Stop any existing camera
        self.camera_manager.stop_camera()
        
        # Start camera with 30 FPS for smoothness
        self.camera_manager.start_camera(
            camera_id=camera_id,
            fps=30,
            frame_callback=self._on_camera_frame,
            capture_callback=self._on_photo_captured
        )
        
        # Start preview timer
        if not self.preview_timer.isActive():
            self.preview_timer.start()
        
        self.shot_status.setText("Camera connected - Ready")
        print(f"[CAMERA] Started camera {camera_id}")
    
    def _on_camera_changed(self, index: int):
        """Handle camera selection change from dropdown."""
        if index < 0 or not self.available_cameras:
            return
        
        # Get selected camera ID
        camera_id = self.camera_combo.currentData()
        if camera_id is None:
            return
        
        # Don't switch if same camera
        if self.camera_manager.is_running() and self.camera_manager.current_camera_id == camera_id:
            return
        
        print(f"[CAMERA] Switching to camera {camera_id}")
        self.shot_status.setText(f"Switching camera...")
        
        # Start the selected camera
        self._start_camera(camera_id)
    
    def _on_camera_frame(self, jpeg_bytes: bytes):
        """Handle camera frame for preview."""
        self.current_frame_bytes = jpeg_bytes
    
    def _update_preview(self):
        """Update preview label with current frame - show full image."""
        if hasattr(self, 'current_frame_bytes') and self.current_frame_bytes:
            # ALWAYS show live preview (even during review)
            pixmap = QPixmap()
            pixmap.loadFromData(self.current_frame_bytes)
            if not pixmap.isNull():
                # Get label size
                label_size = self.preview_label.size()
                
                # Scale to fit within container while showing FULL image (no cropping)
                scaled = pixmap.scaled(
                    label_size.width(),
                    label_size.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.preview_label.setPixmap(scaled)
                self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Also update viewer window with live preview
                if self.viewer_window and not self.viewer_window.is_showing_final:
                    self.viewer_window.update_live_preview(self.current_frame_bytes)
    
    def _on_photo_captured(self, photo_path: str):
        """Handle captured photo from camera."""
        print(f"[CAMERA] Photo captured: {photo_path}")
        
        # Add to captured photos
        self.captured_photos.append(photo_path)
        self.current_slot_index += 1
        
        # Show small review overlay (live preview continues!)
        self._show_photo_overlay(photo_path)
        
        # Update viewer with final photo
        if self.viewer_window:
            self.viewer_window.show_final_photo(photo_path)
        
        # Clear overlay after 3 seconds
        self.review_timer.start(3000)
    
    def _show_photo_overlay(self, photo_path: str):
        """Show small captured photo overlay on top of live preview."""
        self.preview_mode = "review"
        self.shot_status.setText(f"✓ Photo {self.current_slot_index} captured!")
        
        # Create small thumbnail overlay (clients can still see live preview)
        pixmap = QPixmap(photo_path)
        if not pixmap.isNull():
            # Scale to small thumbnail (20% of preview size)
            thumb_size = min(self.preview_label.width(), self.preview_label.height()) // 5
            thumb = pixmap.scaled(
                thumb_size, thumb_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            # Position in bottom-right corner
            # Note: This is simplified - in full implementation, use a separate QLabel overlay
            print(f"[UI] Showing photo thumbnail overlay: {photo_path}")
    
    # === EVENT HANDLERS ===
    
    def _on_frame_selected(self, frame_id: int, metadata: dict, image_path: str):
        """Handle frame selection."""
        self.current_frame_id = frame_id
        self.current_frame_metadata = metadata
        
        frame_name = metadata.get('frame_name', 'Unknown')
        slots = metadata.get('slots', 2)
        
        self.selected_frame_label.setText(f"Frame: {frame_name} ({slots} shots)")
        self.shot_status.setText(f"Ready - {slots} shots remaining")
        
        # Update viewer if open
        if self.viewer_window:
            self.viewer_window.set_frame_overlay(image_path)
    
    def _on_frame_deleted(self, frame_id: int):
        """Handle frame deletion."""
        print(f"[MOCK] Frame {frame_id} deleted")
    
    def _on_frame_edit(self, frame_id: int, new_name: str):
        """Handle frame edit."""
        print(f"[MOCK] Frame {frame_id} renamed to '{new_name}'")
    
    def _on_capture_clicked(self):
        """Handle capture button click."""
        if not self.current_frame_id:
            QMessageBox.warning(self, "No Frame", "Please select a frame first.")
            return
        
        if self.is_countdown_active:
            return
        
        self.is_countdown_active = True
        self.capture_btn.setEnabled(False)
        
        # Start countdown
        self.preview_mode = "countdown"
        self.countdown_overlay.start_countdown(3)
        
        # Update viewer
        if self.viewer_window:
            self.viewer_window.show_countdown(3)
        
        print("[MOCK] Capture initiated - countdown started")
    
    def _on_countdown_finished(self):
        """Handle countdown completion."""
        # Trigger actual photo capture
        self._trigger_capture()
    
    def _trigger_capture(self):
        """Trigger actual photo capture."""
        from datetime import datetime
        from pathlib import Path
        
        # Generate output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = self.client_name_input.text() or "Anonymous"
        output_dir = Path("events/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"capture_{timestamp}.jpg")
        
        if self.camera_manager.is_running():
            # Use real camera
            success = self.camera_manager.capture_photo(output_path)
            if success:
                self.preview_mode = "review"
                self.shot_status.setText("Capturing...")
                print(f"[CAMERA] Capture triggered: {output_path}")
            else:
                self._mock_capture(output_path)
        else:
            # Use mock capture
            self._mock_capture(output_path)
    
    def _mock_capture(self, output_path: str):
        """Create mock capture when camera unavailable."""
        # Create a mock image
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (1280, 720), color=(100, 150, 200))
        draw = ImageDraw.Draw(img)
        draw.text((640, 360), "Mock Capture", fill=(255, 255, 255))
        img.save(output_path)
        
        # Simulate the capture callback
        self._on_photo_captured(output_path)
        print(f"[MOCK] Photo saved: {output_path}")
    
    def _show_captured_photo_review(self, photo_path: str):
        """Show captured photo for review."""
        # Load and display actual captured photo
        pixmap = QPixmap(photo_path)
        if pixmap.isNull():
            # Fallback to mock display if image can't be loaded
            pixmap = QPixmap(600, 450)
            pixmap.fill(QColor("#2d2d2d"))
            
            painter = QPainter(pixmap)
            painter.setPen(QColor("#FFD700"))
            font = QFont("Segoe UI", 24)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, 
                            f"📷 Captured Photo\n(Mock)\n\nReviewing...")
            painter.end()
        else:
            # Scale to fit preview area
            pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        
        self.preview_label.setPixmap(pixmap)
        self.shot_status.setText("Photo captured - Reviewing (3s)...")
    
    def _return_to_live_preview(self):
        """Clear review overlay - live preview never stops."""
        self.preview_mode = "live"
        self.is_countdown_active = False
        self.capture_btn.setEnabled(True)
        
        # Live preview continues - just update status
        self.shot_status.setText("Ready to capture")
        
        # Reset viewer
        if self.viewer_window:
            self.viewer_window.show_idle_screen()
        
        print("[MOCK] Returned to live preview")
    
    def _on_print_clicked(self):
        """Handle print button click."""
        dialog = PrintDialog(parent=self)
        if dialog.exec() == PrintDialog.DialogCode.Accepted:
            settings = dialog.get_print_settings()
            print(f"[MOCK] Print settings: {settings}")
    
    def _toggle_viewer(self):
        """Toggle viewer window visibility."""
        if not self.viewer_window:
            self.viewer_window = ViewerWindow()
        
        if self.viewer_window.isVisible():
            self.viewer_window.hide()
            self.viewer_btn.setText("👁️ Viewer")
        else:
            self.viewer_window.show()
            self.viewer_btn.setText("👁️ Hide Viewer")
            self.viewer_window.show_idle_screen()
    
    def _on_new_session(self):
        """Handle new session button."""
        self.client_name_input.clear()
        self.payment_combo.setCurrentIndex(0)
        self.captured_photos.clear()
        self.current_slot_index = 0
        self.shots_taken_label.setText("Shots: 0 / 0")
        self.amount_label.setText("Amount: ₱0")
        print("[MOCK] New session started")
    
    def _on_usb_export(self):
        """Handle USB export button."""
        QMessageBox.information(
            self,
            "USB Export",
            "USB Export functionality will be connected to backend.\n\n(UI Test Mode)"
        )
    
    def _on_csv_export(self):
        """Handle CSV export button."""
        QMessageBox.information(
            self,
            "CSV Export",
            "CSV Export functionality will be connected to backend.\n\n(UI Test Mode)"
        )
    
    def _on_create_event(self):
        """Handle create event button."""
        name, ok = QInputDialog.getText(self, "Create Event", "Event name:")
        if ok and name:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
            
            self.current_event_id = 1  # Mock ID
            self.event_label.setText(f"Event: {name}")
            
            # Show event management buttons
            self.edit_event_btn.setVisible(True)
            self.delete_event_btn.setVisible(True)
            
            # Load frames for this event
            self.frame_selector.set_event_id(self.current_event_id)
            
            print(f"[MOCK] Event created: {name}")
    
    def _on_load_event(self):
        """Handle load event button."""
        # Mock event selection
        events = [
            "Wedding - Santos & Reyes (2026-04-15)",
            "Birthday Party - Alex (2026-04-20)",
            "Corporate Event - XYZ Corp (2026-04-25)"
        ]
        
        event, ok = QInputDialog.getItem(
            self, "Load Event", "Select event:", events, 0, False
        )
        
        if ok and event:
            self.current_event_id = 1  # Mock ID
            self.event_label.setText(f"Event: {event.split(' (')[0]}")
            
            # Show event management buttons
            self.edit_event_btn.setVisible(True)
            self.delete_event_btn.setVisible(True)
            
            # Load frames
            self.frame_selector.set_event_id(self.current_event_id)
            
            print(f"[MOCK] Event loaded: {event}")
    
    def _edit_current_event(self):
        """Edit current event."""
        if not self.current_event_id:
            return
        
        current_name = self.event_label.text().replace("Event: ", "")
        new_name, ok = QInputDialog.getText(
            self, "Edit Event", "Event name:", text=current_name
        )
        
        if ok and new_name:
            self.event_label.setText(f"Event: {new_name}")
            print(f"[MOCK] Event renamed to: {new_name}")
    
    def _delete_current_event(self):
        """Delete current event."""
        if not self.current_event_id:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Event",
            "Are you sure you want to delete this event?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_event_id = None
            self.event_label.setText("Event: Not Selected")
            self.edit_event_btn.setVisible(False)
            self.delete_event_btn.setVisible(False)
            self.frame_selector.clear_frames()
            print("[MOCK] Event deleted")
    
    def _on_reprint(self, session_id: int):
        """Handle reprint request."""
        print(f"[MOCK] Reprint requested for session {session_id}")
        QMessageBox.information(self, "Reprint", f"Reprint session {session_id}\n\n(UI Test Mode)")
    
    def _on_delete_session(self, session_id: int):
        """Handle session deletion."""
        reply = QMessageBox.question(
            self,
            "Delete Session",
            f"Delete session {session_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print(f"[MOCK] Session {session_id} deleted")
    
    def _on_edit_session(self, session_id: int):
        """Handle session edit."""
        new_name, ok = QInputDialog.getText(
            self, "Edit Session", "Client name:"
        )
        
        if ok:
            print(f"[MOCK] Session {session_id} client renamed to: {new_name}")
    
    def _show_settings(self):
        """Show settings dialog."""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog will be implemented here.\n\n(UI Test Mode)"
        )
    
    def closeEvent(self, event):
        """Handle window close."""
        # Stop camera
        if self.camera_manager:
            self.camera_manager.stop_camera()
        
        # Stop preview timer
        if self.preview_timer:
            self.preview_timer.stop()
        
        # Close database
        if self.session_manager:
            self.session_manager.close()
        
        # Close viewer window
        if self.viewer_window:
            self.viewer_window.close()
        
        event.accept()
