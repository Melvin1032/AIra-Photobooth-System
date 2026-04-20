"""AIra Pro Photobooth System - Operator Window
Main operator dashboard with complete UI.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFrame, QSplitter,
    QMessageBox, QInputDialog, QFileDialog, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QFont, QLinearGradient, QPen

from config import config
from ui.frame_selector import FrameSelector
from ui.session_log_table import SessionLogTable
from ui.countdown_overlay import CountdownOverlay
from ui.print_dialog import PrintDialog
from ui.viewer_window import ViewerWindow
from core.camera import CameraManager
from core.compositor import ImageCompositor
from core.session_manager import SessionManager
from core.qr_server import QRCodeServer


# ── Shared Style Tokens ──────────────────────────────────────────────────────

GOLD       = "#D4AF37"
GOLD_BRIGHT= "#FFD700"
GOLD_DIM   = "#B8860B"
BG_DEEP    = "#080808"
BG_PANEL   = "#101010"
BG_CARD    = "#141414"
BG_INPUT   = "#0d0d0d"
BORDER     = "#1e1e1e"
BORDER_MID = "#2a2a2a"
TEXT_PRI   = "#e8e8e8"
TEXT_SEC   = "#888888"
TEXT_DIM   = "#444444"
GREEN      = "#27ae60"
RED        = "#e74c3c"

CAPTION_STYLE = f"""
    color: {GOLD};
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 3px;
    background: transparent;
"""

PANEL_TITLE_STYLE = f"""
    color: {GOLD};
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 4px;
    padding: 0px;
    background: transparent;
"""

LABEL_STYLE = f"""
    color: {TEXT_SEC};
    font-size: 10px;
    letter-spacing: 1px;
    background: transparent;
"""

INPUT_STYLE = f"""
    QLineEdit {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER_MID};
        border-radius: 3px;
        padding: 7px 10px;
        font-size: 12px;
    }}
    QLineEdit:focus {{
        border-color: {GOLD};
    }}
    QLineEdit::placeholder {{
        color: {TEXT_DIM};
    }}
"""

COMBO_STYLE = f"""
    QComboBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER_MID};
        border-radius: 3px;
        padding: 7px 10px;
        font-size: 12px;
    }}
    QComboBox:focus {{ border-color: {GOLD}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox::down-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {GOLD};
    }}
    QComboBox QAbstractItemView {{
        background-color: {BG_CARD};
        color: {TEXT_PRI};
        selection-background-color: {GOLD};
        selection-color: #000;
        border: 1px solid {BORDER_MID};
    }}
"""

def _btn(label: str, variant: str = "default", height: int = 36) -> QPushButton:
    """Helper to create styled buttons."""
    btn = QPushButton(label)
    btn.setFixedHeight(height)

    if variant == "primary":
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GOLD};
                color: #000000;
                border: none;
                border-radius: 3px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{ background-color: {GOLD_BRIGHT}; }}
            QPushButton:pressed {{ background-color: {GOLD_DIM}; }}
            QPushButton:disabled {{ background-color: #1e1e1e; color: {TEXT_DIM}; }}
        """)
    elif variant == "ghost":
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER_MID};
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {BG_CARD};
                color: {GOLD};
                border-color: {GOLD};
            }}
        """)
    elif variant == "danger":
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #c0392b;
                border: 1px solid #3a1a1a;
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #3a1a1a;
                color: {RED};
            }}
        """)
    else:  # default
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {TEXT_SEC};
                border: 1px solid {BORDER_MID};
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #1a1a1a;
                color: {TEXT_PRI};
                border-color: #3a3a3a;
            }}
            QPushButton:pressed {{
                background-color: {GOLD};
                color: #000;
            }}
        """)

    return btn


def _divider() -> QFrame:
    d = QFrame()
    d.setFixedHeight(1)
    d.setStyleSheet(f"background-color: {BORDER};")
    return d


# ── Main Window ───────────────────────────────────────────────────────────────

class OperatorWindow(QMainWindow):
    """Main operator dashboard window."""

    capture_requested = pyqtSignal()
    countdown_started = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{config.app_name} v{config.version} — Operator")
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
        self.preview_mode = "live"
        
        # Feature settings
        self.auto_print_enabled = False
        self.print_copies = 1
        self.qr_download_enabled = True
        self.raw_mode = False

        self.review_timer = QTimer()
        self.review_timer.setSingleShot(True)
        self.review_timer.timeout.connect(self._return_to_live_preview)

        self.viewer_window = None

        # Core components
        self.camera_manager = CameraManager()
        self.compositor = ImageCompositor()
        self.session_manager = SessionManager()
        self.qr_server = QRCodeServer()

        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._update_preview)
        self.preview_timer.setInterval(33)
        
        # Watchdog timer to detect freezes (optional, disabled by default)
        self.watchdog_timer = QTimer()
        self.watchdog_timer.setInterval(10000)  # Check every 10 seconds
        self.watchdog_timer.timeout.connect(self._watchdog_check)
        self.last_heartbeat = 0

        self.available_cameras = []
        self.current_camera_index = 0
        self.camera_combo = None

        self._setup_ui()
        self._apply_theme()
        self._initialize_camera()
        self._load_initial_data()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._create_top_bar())

        # Main splitter area
        splitter_wrap = QWidget()
        splitter_wrap.setStyleSheet(f"background-color: {BG_DEEP};")
        wrap_layout = QVBoxLayout(splitter_wrap)
        wrap_layout.setContentsMargins(10, 10, 10, 10)
        wrap_layout.setSpacing(10)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setStyleSheet("""
            QSplitter::handle { background-color: #1a1a1a; width: 1px; }
        """)

        content_splitter.addWidget(self._create_left_panel())
        content_splitter.addWidget(self._create_center_panel())
        content_splitter.addWidget(self._create_right_panel())
        content_splitter.setSizes([280, 720, 300])

        wrap_layout.addWidget(content_splitter, stretch=1)
        wrap_layout.addWidget(self._create_bottom_panel())

        root.addWidget(splitter_wrap, stretch=1)

    def _create_top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(56)
        bar.setStyleSheet(f"""
            QWidget {{
                background-color: #0a0a0a;
                border-bottom: 1px solid {BORDER};
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 16, 0)
        layout.setSpacing(0)

        # Logo mark
        logo_mark = QLabel("✦")
        logo_mark.setStyleSheet(f"color: {GOLD}; font-size: 14px; background: transparent;")
        layout.addWidget(logo_mark)
        layout.addSpacing(10)

        # App name
        title = QLabel(config.app_name.upper())
        title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 5px;
            background: transparent;
        """)
        layout.addWidget(title)

        layout.addSpacing(6)

        version_label = QLabel(f"v{config.version}")
        version_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px; background: transparent;")
        layout.addWidget(version_label)

        layout.addSpacing(24)

        # Event badge
        self.event_label = QLabel("NO EVENT SELECTED")
        self.event_label.setStyleSheet(f"""
            color: {TEXT_DIM};
            font-size: 9px;
            letter-spacing: 2px;
            background: transparent;
            padding: 4px 12px;
            border: 1px solid {BORDER};
            border-radius: 2px;
        """)
        layout.addWidget(self.event_label)

        layout.addStretch()

        # Event management
        self.edit_event_btn = _btn("✏  EDIT", "ghost", 32)
        self.edit_event_btn.setFixedWidth(80)
        self.edit_event_btn.setVisible(False)
        self.edit_event_btn.clicked.connect(self._edit_current_event)
        layout.addWidget(self.edit_event_btn)
        layout.addSpacing(4)

        self.delete_event_btn = _btn("✕  DEL", "danger", 32)
        self.delete_event_btn.setFixedWidth(80)
        self.delete_event_btn.setVisible(False)
        self.delete_event_btn.clicked.connect(self._delete_current_event)
        layout.addWidget(self.delete_event_btn)

        layout.addSpacing(16)

        # Theme toggle
        self.theme_btn = _btn("◑  DARK", "ghost", 32)
        self.theme_btn.setFixedWidth(90)
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        layout.addSpacing(16)

        # Camera label + combo
        cam_label = QLabel("CAM")
        cam_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px; letter-spacing: 2px; background: transparent;")
        layout.addWidget(cam_label)
        layout.addSpacing(8)

        self.camera_combo = QComboBox()
        self.camera_combo.setFixedHeight(32)
        self.camera_combo.setFixedWidth(220)
        self.camera_combo.setStyleSheet(COMBO_STYLE)
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        layout.addWidget(self.camera_combo)
        layout.addSpacing(4)

        refresh_btn = _btn("↻", "ghost", 32)
        refresh_btn.setFixedWidth(32)
        refresh_btn.setToolTip("Refresh cameras")
        refresh_btn.clicked.connect(self._refresh_cameras)
        layout.addWidget(refresh_btn)

        layout.addSpacing(12)

        settings_btn = _btn("⚙", "ghost", 32)
        settings_btn.setFixedWidth(36)
        settings_btn.clicked.connect(self._show_settings)
        layout.addWidget(settings_btn)

        return bar

    def _create_left_panel(self) -> QFrame:
        panel = QFrame()
        panel.setMinimumWidth(260)
        panel.setMaximumWidth(320)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("FRAMES")
        title.setStyleSheet(PANEL_TITLE_STYLE)
        layout.addWidget(title)
        layout.addWidget(_divider())

        self.frame_selector = FrameSelector()
        self.frame_selector.setStyleSheet("background: transparent;")
        self.frame_selector.frame_selected.connect(self._on_frame_selected)
        self.frame_selector.frame_deleted.connect(self._on_frame_deleted)
        self.frame_selector.frame_edit_requested.connect(self._on_frame_edit)
        layout.addWidget(self.frame_selector)

        return panel

    def _create_center_panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Preview container
        preview_frame = QFrame()
        preview_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border: 1px solid {BORDER};
                border-radius: 3px;
            }}
        """)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(1, 1, 1, 1)
        preview_layout.setSpacing(0)

        self.preview_label = QLabel("LIVE PREVIEW")
        self.preview_label.setMinimumSize(640, 360)
        from PyQt6.QtWidgets import QSizePolicy
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(f"""
            background-color: #000000;
            color: {TEXT_DIM};
            font-size: 11px;
            letter-spacing: 3px;
        """)
        preview_layout.addWidget(self.preview_label, stretch=1)

        self.countdown_overlay = CountdownOverlay(self.preview_label)
        self.countdown_overlay.countdown_finished.connect(self._on_countdown_finished)
        self.countdown_overlay.countdown_tick.connect(self._on_countdown_tick)

        layout.addWidget(preview_frame, stretch=1)

        # Frame info bar
        info_bar = QWidget()
        info_bar.setFixedHeight(30)
        info_bar.setStyleSheet(f"background: transparent;")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(4, 0, 4, 0)
        info_layout.setSpacing(8)

        self.selected_frame_label = QLabel("No frame selected")
        self.selected_frame_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent;")
        info_layout.addWidget(self.selected_frame_label)

        info_layout.addStretch()

        self.shot_status = QLabel("Ready")
        self.shot_status.setStyleSheet(f"color: {GREEN}; font-size: 11px; font-weight: bold; background: transparent;")
        info_layout.addWidget(self.shot_status)

        layout.addWidget(info_bar)

        # Controls row
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.capture_btn = QPushButton("⬤  CAPTURE")
        self.capture_btn.setFixedHeight(52)
        self.capture_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GOLD};
                color: #000000;
                border: none;
                border-radius: 3px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 3px;
            }}
            QPushButton:hover {{ background-color: {GOLD_BRIGHT}; }}
            QPushButton:pressed {{ background-color: {GOLD_DIM}; }}
            QPushButton:disabled {{
                background-color: #1a1a1a;
                color: {TEXT_DIM};
            }}
        """)
        self.capture_btn.clicked.connect(self._on_capture_clicked)
        controls_layout.addWidget(self.capture_btn, stretch=3)

        self.print_btn = _btn("⎙  PRINT", "ghost", 52)
        self.print_btn.clicked.connect(self._on_print_clicked)
        controls_layout.addWidget(self.print_btn, stretch=1)

        self.viewer_btn = _btn("◉  VIEWER", "ghost", 52)
        self.viewer_btn.clicked.connect(self._toggle_viewer)
        controls_layout.addWidget(self.viewer_btn, stretch=1)

        layout.addLayout(controls_layout)

        return panel

    def _create_right_panel(self) -> QFrame:
        panel = QFrame()
        panel.setMinimumWidth(240)
        panel.setMaximumWidth(300)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("SESSION")
        title.setStyleSheet(PANEL_TITLE_STYLE)
        layout.addWidget(title)
        layout.addWidget(_divider())

        # Client name
        layout.addSpacing(2)
        client_label = QLabel("CLIENT NAME")
        client_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(client_label)

        self.client_name_input = QLineEdit()
        self.client_name_input.setPlaceholderText("Enter name…")
        self.client_name_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.client_name_input)

        layout.addSpacing(6)

        # Payment
        payment_label = QLabel("PAYMENT")
        payment_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(payment_label)

        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Unpaid", "Paid", "Partial"])
        self.payment_combo.setStyleSheet(COMBO_STYLE)
        layout.addWidget(self.payment_combo)

        layout.addSpacing(8)
        layout.addWidget(_divider())
        layout.addSpacing(6)

        # Stats card
        stats_card = QFrame()
        stats_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 3px;
                padding: 2px;
            }}
        """)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(12, 10, 12, 10)
        stats_layout.setSpacing(6)

        self.shots_taken_label = QLabel("SHOTS  ·  0 / 0")
        self.shots_taken_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent;")
        stats_layout.addWidget(self.shots_taken_label)

        self.amount_label = QLabel("AMOUNT  ·  ₱0")
        self.amount_label.setStyleSheet(f"color: {GOLD}; font-size: 12px; font-weight: bold; background: transparent;")
        stats_layout.addWidget(self.amount_label)

        layout.addWidget(stats_card)
        layout.addSpacing(12)

        # Feature toggles
        features_label = QLabel("FEATURES")
        features_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(features_label)

        # Auto-print toggle
        auto_print_layout = QHBoxLayout()
        auto_print_layout.setSpacing(8)
        self.auto_print_check = QCheckBox("Auto-Print")
        self.auto_print_check.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_SEC};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {BORDER_MID};
                border-radius: 3px;
                background: {BG_INPUT};
            }}
            QCheckBox::indicator:checked {{
                background: {GOLD};
                border-color: {GOLD};
            }}
        """)
        self.auto_print_check.stateChanged.connect(self._on_auto_print_toggle)
        auto_print_layout.addWidget(self.auto_print_check)
        
        # Print copies spinner
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 10)
        self.copies_spin.setValue(1)
        self.copies_spin.setFixedWidth(50)
        self.copies_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {BG_INPUT};
                color: {TEXT_PRI};
                border: 1px solid {BORDER_MID};
                border-radius: 3px;
                padding: 2px;
                font-size: 11px;
            }}
        """)
        self.copies_spin.valueChanged.connect(self._on_copies_changed)
        auto_print_layout.addWidget(self.copies_spin)
        auto_print_layout.addWidget(QLabel("copies"))
        auto_print_layout.addStretch()
        layout.addLayout(auto_print_layout)

        # QR Code toggle
        self.qr_check = QCheckBox("QR Download")
        self.qr_check.setChecked(True)
        self.qr_check.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_SEC};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {BORDER_MID};
                border-radius: 3px;
                background: {BG_INPUT};
            }}
            QCheckBox::indicator:checked {{
                background: {GOLD};
                border-color: {GOLD};
            }}
        """)
        self.qr_check.stateChanged.connect(self._on_qr_toggle)
        layout.addWidget(self.qr_check)

        # Show/Hide QR button (for operator control)
        self.show_qr_btn = QPushButton("Hide QR on Display")
        self.show_qr_btn.setCheckable(True)
        self.show_qr_btn.setChecked(False)  # Default: QR is visible
        self.show_qr_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                color: {TEXT_SEC};
                border: 1px solid {BORDER_MID};
                border-radius: 3px;
                padding: 8px 12px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                border-color: {GOLD};
                color: {TEXT_PRI};
            }}
            QPushButton:checked {{
                background-color: {GOLD};
                color: #0a0a0a;
                border-color: {GOLD};
            }}
        """)
        self.show_qr_btn.clicked.connect(self._on_show_qr_toggle)
        layout.addWidget(self.show_qr_btn)

        # Raw mode toggle
        self.raw_mode_check = QCheckBox("Raw Photo Mode (No Frame)")
        self.raw_mode_check.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_SEC};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {BORDER_MID};
                border-radius: 3px;
                background: {BG_INPUT};
            }}
            QCheckBox::indicator:checked {{
                background: {GOLD};
                border-color: {GOLD};
            }}
        """)
        self.raw_mode_check.stateChanged.connect(self._on_raw_mode_toggle)
        layout.addWidget(self.raw_mode_check)

        layout.addSpacing(12)
        layout.addWidget(_divider())
        layout.addSpacing(6)

        # Action buttons
        new_session_btn = _btn("✦  NEW SESSION", "ghost", 36)
        new_session_btn.clicked.connect(self._on_new_session)
        layout.addWidget(new_session_btn)

        usb_export_btn = _btn("↓  USB EXPORT", "ghost", 36)
        usb_export_btn.clicked.connect(self._on_usb_export)
        layout.addWidget(usb_export_btn)

        csv_export_btn = _btn("⊞  CSV EXPORT", "ghost", 36)
        csv_export_btn.clicked.connect(self._on_csv_export)
        layout.addWidget(csv_export_btn)

        layout.addStretch()

        return panel

    def _create_bottom_panel(self) -> QFrame:
        panel = QFrame()
        panel.setMinimumHeight(190)
        panel.setMaximumHeight(280)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title = QLabel("SESSION LOG")
        title.setStyleSheet(PANEL_TITLE_STYLE)
        header.addWidget(title)
        header.addStretch()

        create_event_btn = _btn("＋  CREATE EVENT", "ghost", 28)
        create_event_btn.setFixedWidth(140)
        create_event_btn.clicked.connect(self._on_create_event)
        header.addWidget(create_event_btn)

        load_event_btn = _btn("⊙  LOAD EVENT", "ghost", 28)
        load_event_btn.setFixedWidth(130)
        load_event_btn.clicked.connect(self._on_load_event)
        header.addWidget(load_event_btn)

        layout.addLayout(header)
        layout.addWidget(_divider())

        self.session_log = SessionLogTable()
        self.session_log.reprint_requested.connect(self._on_reprint)
        self.session_log.delete_requested.connect(self._on_delete_session)
        self.session_log.edit_requested.connect(self._on_edit_session)
        self.session_log.download_requested.connect(self._on_download_photo)
        layout.addWidget(self.session_log)

        return panel

    # ── Theming ───────────────────────────────────────────────────────────────

    def _apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(self._get_dark_stylesheet())
            self.theme_btn.setText("◑  DARK")
        else:
            self.setStyleSheet(self._get_light_stylesheet())
            self.theme_btn.setText("◐  LIGHT")

    def _get_dark_stylesheet(self) -> str:
        return f"""
            QMainWindow {{ background-color: {BG_DEEP}; }}
            QWidget {{
                background-color: {BG_PANEL};
                color: {TEXT_PRI};
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }}
            QLabel {{ background-color: transparent; }}
            QSplitter::handle {{ background-color: {BORDER}; width: 1px; }}
        """

    def _get_light_stylesheet(self) -> str:
        return """
            QMainWindow { background-color: #f0f0f0; }
            QWidget {
                background-color: #fafafa;
                color: #111111;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QLabel { background-color: transparent; }
            QSplitter::handle { background-color: #ddd; width: 1px; }
            QPushButton {
                background-color: #ebebeb;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 6px 14px;
            }
            QPushButton:hover { background-color: #e0e0e0; border-color: #B8860B; color: #7a5c00; }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                color: #111;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 6px;
            }
        """

    def _toggle_theme(self):
        try:
            self.is_dark_mode = not self.is_dark_mode
            self._apply_theme()
            if hasattr(self.frame_selector, 'apply_stylesheet'):
                self.frame_selector.apply_stylesheet()
            if hasattr(self.session_log, 'apply_stylesheet'):
                self.session_log.apply_stylesheet()
            self.theme_btn.setText("◑  DARK" if self.is_dark_mode else "◐  LIGHT")
            print(f"[THEME] Changed to: {'Dark' if self.is_dark_mode else 'Light'}")
        except Exception as e:
            print(f"[ERROR] Theme toggle failed: {e}")
            import traceback
            traceback.print_exc()

    # ── Data Loading ──────────────────────────────────────────────────────────

    def _load_initial_data(self):
        events = self.session_manager.get_all_events()
        if events:
            self._load_event(events[0]['id'])
        else:
            self.event_label.setText("NO EVENT SELECTED")
            self.edit_event_btn.setVisible(False)
            self.delete_event_btn.setVisible(False)

    def _initialize_camera(self):
        try:
            self._refresh_cameras(auto_start=False)
            if self.available_cameras:
                selected_idx = self.camera_combo.currentIndex()
                if selected_idx < 0:
                    selected_idx = 0
                    self.camera_combo.setCurrentIndex(0)
                camera_id = self.available_cameras[selected_idx][0]
                self._start_camera(camera_id)
            else:
                print("[CAMERA] No cameras detected - using mock mode")
                self.shot_status.setText("No camera — mock mode")
        except Exception as e:
            print(f"[CAMERA] Error initializing: {e}")
            self.shot_status.setText("Camera error — mock mode")

    def _refresh_cameras(self, auto_start=True):
        was_running = self.camera_manager.is_running()
        current_camera_id = None
        if was_running:
            current_camera_id = self.camera_manager.current_camera_id
            self.camera_manager.stop_camera()

        self.available_cameras = self.camera_manager.detect_cameras()
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()

        if self.available_cameras:
            for idx, (cam_id, cam_name) in enumerate(self.available_cameras):
                self.camera_combo.addItem(cam_name, cam_id)
                if current_camera_id is not None and cam_id == current_camera_id:
                    self.camera_combo.setCurrentIndex(idx)
            if self.camera_combo.currentIndex() < 0 and self.camera_combo.count() > 0:
                self.camera_combo.setCurrentIndex(0)
            self.camera_combo.blockSignals(False)
            if auto_start:
                selected_idx = self.camera_combo.currentIndex()
                camera_id = self.available_cameras[selected_idx][0]
                self._start_camera(camera_id)
        else:
            self.camera_combo.addItem("No cameras found")
            self.camera_combo.setEnabled(False)
            self.camera_combo.blockSignals(False)
            self.shot_status.setText("No camera — mock mode")

    def _start_camera(self, camera_id: int):
        self.camera_manager.stop_camera()
        self.camera_manager.start_camera(
            camera_id=camera_id,
            fps=30,
            frame_callback=self._on_camera_frame,
            capture_callback=self._on_photo_captured
        )
        if not self.preview_timer.isActive():
            self.preview_timer.start()
        self.shot_status.setText("Camera connected")
        print(f"[CAMERA] Started camera {camera_id}")

    def _on_camera_changed(self, index: int):
        if index < 0 or not self.available_cameras:
            return
        camera_id = self.camera_combo.currentData()
        if camera_id is None:
            return
        if self.camera_manager.is_running() and self.camera_manager.current_camera_id == camera_id:
            return
        print(f"[CAMERA] Switching to camera {camera_id}")
        self._start_camera(camera_id)

    def _on_camera_frame(self, jpeg_bytes: bytes):
        self.current_frame_bytes = jpeg_bytes

    def _update_preview(self):
        try:
            # Update heartbeat for watchdog
            import time
            self.last_heartbeat = time.time()
            
            if not hasattr(self, 'current_frame_bytes') or not self.current_frame_bytes:
                return
            
            pixmap = QPixmap()
            pixmap.loadFromData(self.current_frame_bytes)
            if not pixmap.isNull():
                label_size = self.preview_label.size()
                scaled = pixmap.scaled(
                    label_size.width(),
                    label_size.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                if hasattr(self, 'frame_overlay_pixmap') and self.frame_overlay_pixmap and not self.frame_overlay_pixmap.isNull():
                    final_pixmap = QPixmap(scaled)
                    painter = QPainter(final_pixmap)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    overlay_scaled = self.frame_overlay_pixmap.scaled(
                        final_pixmap.width(), final_pixmap.height(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    x = (final_pixmap.width() - overlay_scaled.width()) // 2
                    y = (final_pixmap.height() - overlay_scaled.height()) // 2
                    painter.drawPixmap(x, y, overlay_scaled)
                    painter.end()
                    scaled = final_pixmap
                self.preview_label.setPixmap(scaled)
                self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Update viewer window if not showing final photo
                if self.viewer_window and not self.viewer_window.is_showing_final:
                    self.viewer_window.update_live_preview(self.current_frame_bytes)
                
        except Exception as e:
            # Don't let preview errors crash the app
            print(f"[PREVIEW] Error updating preview: {e}")

    # ── Photo Capture ─────────────────────────────────────────────────────────

    def _on_photo_captured(self, photo_path: str):
        print(f"[CAMERA] Photo captured: {photo_path}")

        # Determine which photo to use based on raw mode
        if self.raw_mode:
            # Raw mode: use photo without frame
            processed_path = photo_path
            display_path = photo_path
            print("[CAPTURE] Raw mode - no frame overlay")
        else:
            # Normal mode: composite with frame
            processed_path = photo_path
            display_path = photo_path
            
            # Check if frame is selected
            has_frame = hasattr(self, 'current_frame_image_path') and self.current_frame_image_path
            has_metadata = hasattr(self, 'current_frame_metadata') and self.current_frame_metadata
            
            print(f"[CAPTURE] Frame check - has_frame: {has_frame}, has_metadata: {has_metadata}")
            
            if has_frame and has_metadata:
                print(f"[CAPTURE] Loading frame: {self.current_frame_image_path}")
                frame_loaded = self.compositor.load_frame(self.current_frame_image_path, self.current_frame_metadata)
                print(f"[CAPTURE] Frame loaded: {frame_loaded}")
                
                if frame_loaded:
                    from pathlib import Path
                    output_dir = Path("events") / "output"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    client_name = getattr(self, 'current_client_name', 'Guest')
                    processed_path = str(output_dir / f"{client_name}_{timestamp}.jpg")
                    
                    print(f"[CAPTURE] Compositing photo to: {processed_path}")
                    composite_result = self.compositor.composite_photos([photo_path], processed_path)
                    
                    if composite_result:
                        print(f"[COMPOSITE] Photo composited successfully: {processed_path}")
                        display_path = processed_path
                    else:
                        print(f"[COMPOSITE] ERROR: Compositing failed! Using raw photo.")
                        processed_path = photo_path
                else:
                    print(f"[CAPTURE] ERROR: Failed to load frame! Using raw photo.")
                    processed_path = photo_path
            else:
                print(f"[CAPTURE] No frame selected - using raw photo")

        self.captured_photos.append(processed_path)
        self.current_slot_index += 1

        if hasattr(self, 'current_session_id') and self.current_session_id:
            self.session_manager.add_photo(
                self.current_session_id,
                slot_number=self.current_slot_index,
                raw_path=photo_path,
                processed_path=processed_path if processed_path != photo_path else None
            )
            self.session_manager.update_session(self.current_session_id, shots_taken=self.current_slot_index)

        # Generate QR code if enabled
        qr_image = None
        if self.qr_download_enabled and self.qr_server.base_url:
            # ALWAYS use the raw photo for QR code since compositing may fail
            # The QR server will copy it to events/output/ for serving
            from pathlib import Path
            qr_photo_path = photo_path  # Use raw photo path
            
            # If compositing succeeded and file exists, use processed path
            if Path(processed_path).exists() and processed_path != photo_path:
                qr_photo_path = processed_path
                print(f"[QR] Using composited photo for QR code: {qr_photo_path}")
            else:
                print(f"[QR] Using raw photo for QR code: {qr_photo_path}")
            
            qr_image = self.qr_server.generate_qr_code(qr_photo_path)
            if qr_image:
                print(f"[QR] Generated QR code for: {qr_photo_path}")

        # Update viewer with photo and optional QR code
        if self.viewer_window:
            if qr_image:
                self.viewer_window.set_qr_code(qr_image)
            # Only show QR if download is enabled AND operator hasn't hidden it
            qr_visible = self.qr_download_enabled and not self.show_qr_btn.isChecked()
            self.viewer_window.show_final_photo(display_path, show_qr=qr_visible)

        self._show_photo_overlay(display_path)

        # Auto-print if enabled
        if self.auto_print_enabled:
            self._auto_print_photo(processed_path)

        self._load_sessions_for_event(self.current_event_id)
        self.shots_taken_label.setText(f"SHOTS  ·  {self.current_slot_index}")
        self.review_timer.start(3000)

    def _auto_print_photo(self, photo_path: str):
        """Automatically print photo with configured copies."""
        try:
            from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo
            from PyQt6.QtGui import QPixmap, QPainter
            
            # Get default printer
            default_printer = QPrinterInfo.defaultPrinter()
            if not default_printer:
                print("[AUTO-PRINT] No printer found")
                return
            
            printer = QPrinter(default_printer)
            printer.setCopyCount(self.print_copies)
            
            # Print the photo
            pixmap = QPixmap(photo_path)
            if pixmap.isNull():
                print("[AUTO-PRINT] Failed to load photo")
                return
            
            painter = QPainter(printer)
            rect = painter.viewport()
            size = pixmap.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            print(f"[AUTO-PRINT] Printed {self.print_copies} copy/copies of photo")
            
        except Exception as e:
            print(f"[AUTO-PRINT] Error: {e}")

    def _show_photo_overlay(self, photo_path: str):
        self.preview_mode = "review"
        self.shot_status.setText(f"✓  Photo {self.current_slot_index} captured")
        print(f"[UI] Photo overlay: {photo_path}")

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _on_frame_selected(self, frame_id: int, metadata: dict, image_path: str):
        self.current_frame_id = frame_id
        self.current_frame_metadata = metadata
        self.current_frame_image_path = image_path

        frame_name = metadata.get('frame_name', 'Unknown')
        slots = metadata.get('slots', 2)
        price = metadata.get('price', 0)

        self.selected_frame_label.setText(f"{frame_name}  ·  {slots} shots")
        self.shot_status.setText(f"Ready  ·  {slots} shots")
        self.amount_label.setText(f"AMOUNT  ·  ₱{price:.0f}")

        if image_path:
            self.frame_overlay_pixmap = QPixmap(image_path)
        else:
            self.frame_overlay_pixmap = None

        if self.viewer_window:
            self.viewer_window.set_frame_overlay(image_path)

    def _on_frame_deleted(self, frame_id: int):
        self.session_manager.delete_frame(frame_id)
        self.frame_selector.load_frames_for_event(self.current_event_id)

    def _on_frame_edit(self, frame_id: int, new_name: str):
        self.session_manager.update_frame(frame_id, name=new_name)
        self.frame_selector.load_frames_for_event(self.current_event_id)

    def _on_capture_clicked(self):
        if not self.current_event_id:
            QMessageBox.warning(self, "No Event", "Please create or load an event first.")
            return
        if not self.current_frame_id:
            QMessageBox.warning(self, "No Frame", "Please select a frame first.")
            return
        if self.is_countdown_active:
            return

        # Always create a new session for each capture (1 picture = 1 ID)
        client_name = self.client_name_input.text()
        self.current_session_id = self.session_manager.create_session(
            self.current_event_id,
            client_name=client_name,
            frame_id=self.current_frame_id
        )
        # Reset for new session
        self.captured_photos.clear()
        self.current_slot_index = 0

        self.is_countdown_active = True
        self.capture_btn.setEnabled(False)
        self.preview_mode = "countdown"
        self.countdown_overlay.start_countdown(3)

        if self.viewer_window:
            self.viewer_window.show_countdown(3)

    def _on_countdown_tick(self, count: int):
        """Handle countdown tick - update viewer and play beep."""
        if self.viewer_window:
            self.viewer_window.show_countdown(count)
        # Play beep sound
        self._play_beep()
        print(f"[COUNTDOWN] Tick: {count}")

    def _play_beep(self):
        """Play a beep sound for countdown."""
        try:
            # Try using winsound on Windows
            import winsound
            winsound.Beep(1000, 200)  # 1000 Hz for 200ms
        except Exception:
            # Fallback: try using QSoundEffect
            try:
                from PyQt6.QtMultimedia import QSoundEffect
                from PyQt6.QtCore import QUrl
                # Create a simple beep using QSoundEffect if available
                # Note: This requires a sound file, so we'll skip if not available
                pass
            except Exception:
                pass

    def _on_countdown_finished(self):
        self._trigger_capture()

    def _trigger_capture(self):
        from datetime import datetime
        from pathlib import Path

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = self.client_name_input.text() or "Anonymous"
        output_dir = Path("events/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"capture_{timestamp}.jpg")

        if self.camera_manager.is_running():
            success = self.camera_manager.capture_photo(output_path)
            if success:
                self.preview_mode = "review"
            else:
                self._mock_capture(output_path)
        else:
            self._mock_capture(output_path)

    def _mock_capture(self, output_path: str):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1280, 720), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        draw.text((640, 360), "Mock Capture", fill=(212, 175, 55))
        img.save(output_path)
        self._on_photo_captured(output_path)

    def _show_captured_photo_review(self, photo_path: str):
        pixmap = QPixmap(photo_path)
        if pixmap.isNull():
            pixmap = QPixmap(600, 450)
            pixmap.fill(QColor(BG_CARD))
            painter = QPainter(pixmap)
            painter.setPen(QColor(GOLD))
            font = QFont("Georgia", 20)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "✓  Captured")
            painter.end()
        else:
            pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        self.preview_label.setPixmap(pixmap)

    def _return_to_live_preview(self):
        self.preview_mode = "live"
        self.is_countdown_active = False
        self.capture_btn.setEnabled(True)
        self.shot_status.setText("Ready")
        if self.viewer_window:
            self.viewer_window.show_idle_screen()

    def _on_print_clicked(self):
        photo_path = None
        if hasattr(self, 'captured_photos') and self.captured_photos:
            photo_path = self.captured_photos[-1]
        elif hasattr(self, 'current_session_id') and self.current_session_id:
            photos = self.session_manager.get_photos_for_session(self.current_session_id)
            if photos:
                photo_path = photos[-1].get('processed_path') or photos[-1].get('raw_path')

        dialog = PrintDialog(photo_path=photo_path, parent=self)
        if dialog.exec() == PrintDialog.DialogCode.Accepted:
            settings = dialog.get_print_settings()
            print(f"[PRINT] Settings: {settings}")

    def _toggle_viewer(self):
        if not self.viewer_window:
            self.viewer_window = ViewerWindow()
        if self.viewer_window.isVisible():
            self.viewer_window.hide()
            self.viewer_btn.setText("◉  VIEWER")
        else:
            self.viewer_window.show()
            self.viewer_btn.setText("◎  HIDE")
            if hasattr(self, 'current_frame_image_path') and self.current_frame_image_path:
                self.viewer_window.set_frame_overlay(self.current_frame_image_path)
            self.viewer_window.show_idle_screen()

    def _on_new_session(self):
        self.client_name_input.clear()
        self.payment_combo.setCurrentIndex(0)
        self.captured_photos.clear()
        self.current_slot_index = 0
        self.shots_taken_label.setText("SHOTS  ·  0 / 0")
        self.amount_label.setText("AMOUNT  ·  ₱0")
        self.current_session_id = None

    def _on_auto_print_toggle(self, state):
        """Toggle auto-print on capture."""
        self.auto_print_enabled = state == Qt.CheckState.Checked.value
        print(f"[SETTINGS] Auto-print: {'ON' if self.auto_print_enabled else 'OFF'}")

    def _on_copies_changed(self, value):
        """Change number of print copies."""
        self.print_copies = value
        print(f"[SETTINGS] Print copies: {value}")

    def _on_qr_toggle(self, state):
        """Toggle QR code download."""
        self.qr_download_enabled = state == Qt.CheckState.Checked.value
        print(f"[SETTINGS] QR Download: {'ON' if self.qr_download_enabled else 'OFF'}")

    def _on_show_qr_toggle(self):
        """Toggle QR code visibility on client display."""
        is_hidden = self.show_qr_btn.isChecked()
        if is_hidden:
            self.show_qr_btn.setText("Show QR on Display")
            print("[OPERATOR] QR code hidden on client display")
        else:
            self.show_qr_btn.setText("Hide QR on Display")
            print("[OPERATOR] QR code shown on client display")
        
        # Update viewer window
        if self.viewer_window:
            self.viewer_window.set_qr_visible(not is_hidden)

    def _on_raw_mode_toggle(self, state):
        """Toggle raw photo mode (no frame overlay)."""
        self.raw_mode = state == Qt.CheckState.Checked.value
        if self.viewer_window:
            self.viewer_window.toggle_raw_mode(self.raw_mode)
        print(f"[SETTINGS] Raw Mode: {'ON' if self.raw_mode else 'OFF'}")

    def _on_usb_export(self):
        if not self.current_event_id:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return
        from core.usb_exporter import USBExporter
        exporter = USBExporter(self)
        exporter.export_event(self.current_event_id, self.session_manager)

    def _on_csv_export(self):
        if not self.current_event_id:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return
        from core.csv_export import CSVExporter
        exporter = CSVExporter(self)
        exporter.export_sessions(self.current_event_id, self.session_manager)

    def _on_create_event(self):
        name, ok = QInputDialog.getText(self, "Create Event", "Event name:")
        if ok and name:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
            event_id = self.session_manager.create_event(name, date)
            self._load_event(event_id)

    def _on_load_event(self):
        events = self.session_manager.get_all_events()
        if not events:
            QMessageBox.information(self, "No Events", "No events found. Create one first.")
            return

        event_items = [(f"{e['name']} ({e['date']})", e['id']) for e in events]
        event_names = [item[0] for item in event_items]

        selected, ok = QInputDialog.getItem(self, "Load Event", "Select event:", event_names, 0, False)
        if ok and selected:
            event_id = next(item[1] for item in event_items if item[0] == selected)
            self._load_event(event_id)

    def _load_event(self, event_id: int):
        event = self.session_manager.get_event(event_id)
        if not event:
            QMessageBox.warning(self, "Error", "Event not found.")
            return

        self.current_event_id = event_id
        self.event_label.setText(event['name'].upper())
        self.edit_event_btn.setVisible(True)
        self.delete_event_btn.setVisible(True)
        self.frame_selector.set_event_id(event_id)
        self._load_sessions_for_event(event_id)

    def _load_sessions_for_event(self, event_id: int):
        self.session_log.clear_sessions()
        sessions = self.session_manager.get_sessions_for_event(event_id)

        for session in sessions:
            photos = self.session_manager.get_photos_for_session(session['id'])
            photo_path = None
            if photos:
                photo_path = photos[-1].get('processed_path') or photos[-1].get('raw_path')

            self.session_log.add_session(
                session_id=session['id'],
                client_name=session['client_name'] or "Anonymous",
                frame_name=session.get('frame_name', 'Unknown'),
                amount=session['amount'] or 0,
                payment_status=session['payment_status'] or 'Unpaid',
                shots=session['shots_taken'] or 0,
                status=session['status'] or 'Active',
                timestamp=session['created_at'].split(' ')[1] if ' ' in str(session['created_at']) else '',
                photo_path=photo_path
            )

    def _edit_current_event(self):
        if not self.current_event_id:
            return
        event = self.session_manager.get_event(self.current_event_id)
        if not event:
            return
        new_name, ok = QInputDialog.getText(self, "Edit Event", "Event name:", text=event['name'])
        if ok and new_name:
            self.session_manager.update_event(self.current_event_id, name=new_name)
            self.event_label.setText(new_name.upper())

    def _delete_current_event(self):
        if not self.current_event_id:
            return
        event = self.session_manager.get_event(self.current_event_id)
        event_name = event['name'] if event else "this event"

        reply = QMessageBox.question(
            self, "Delete Event",
            f"Delete '{event_name}'?\n\nAll sessions, photos and frames will be removed.\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.session_manager.delete_event(self.current_event_id)
            self.current_event_id = None
            self.event_label.setText("NO EVENT SELECTED")
            self.edit_event_btn.setVisible(False)
            self.delete_event_btn.setVisible(False)
            self.frame_selector.clear_frames()
            self.session_log.clear_sessions()

    def _on_reprint(self, session_id: int):
        session = self.session_manager.get_session(session_id)
        if not session:
            QMessageBox.warning(self, "Error", "Session not found.")
            return
        photos = self.session_manager.get_photos_for_session(session_id)
        if not photos:
            QMessageBox.information(self, "No Photos", "No photos in this session.")
            return
        from ui.print_dialog import PrintDialog
        dialog = PrintDialog(photos[-1].get('processed_path') or photos[-1].get('raw_path'), parent=self)
        if dialog.exec() == PrintDialog.DialogCode.Accepted:
            settings = dialog.get_print_settings()

    def _on_delete_session(self, session_id: int):
        reply = QMessageBox.question(
            self, "Delete Session",
            f"Delete session {session_id}?\n\nAll associated photos will be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.session_manager.delete_session(session_id)
            # Clear current_session_id if we deleted the current session
            if hasattr(self, 'current_session_id') and self.current_session_id == session_id:
                self.current_session_id = None
                self.captured_photos.clear()
                self.current_slot_index = 0
            self._load_sessions_for_event(self.current_event_id)

    def _on_edit_session(self, session_id: int):
        session = self.session_manager.get_session(session_id)
        if not session:
            return
        new_name, ok = QInputDialog.getText(
            self, "Edit Session", "Client name:", text=session['client_name'] or ""
        )
        if ok:
            self.session_manager.update_session(session_id, client_name=new_name)
            self._load_sessions_for_event(self.current_event_id)

    def _on_download_photo(self, session_id: int):
        from pathlib import Path
        photos = self.session_manager.get_photos_for_session(session_id)
        if not photos:
            QMessageBox.information(self, "No Photos", "No photos in this session.")
            return

        photo = photos[-1]
        photo_path = photo.get('processed_path') or photo.get('raw_path')

        if not photo_path or not Path(photo_path).exists():
            QMessageBox.warning(self, "Error", "Photo file not found.")
            return

        default_name = Path(photo_path).stem + ".png"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Photo as PNG", default_name, "PNG Images (*.png)"
        )

        if not save_path:
            return

        try:
            from PIL import Image
            img = Image.open(photo_path)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                    img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(save_path, 'PNG')
            QMessageBox.information(self, "Saved", f"Photo saved:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")

    def _show_settings(self):
        QMessageBox.information(self, "Settings", "Settings will be implemented here.")
    
    def _watchdog_check(self):
        """Watchdog to detect application freezes."""
        import time
        current_time = time.time()
        if self.last_heartbeat > 0 and (current_time - self.last_heartbeat) > 30:
            print("[WATCHDOG] Application may be frozen! Last heartbeat was 30+ seconds ago")
            # Could implement auto-recovery here if needed
        self.last_heartbeat = current_time

    def closeEvent(self, event):
        """Clean shutdown of all resources."""
        try:
            print("[SHUTDOWN] Closing application...")
            
            # Stop preview timer first
            if hasattr(self, 'preview_timer') and self.preview_timer:
                self.preview_timer.stop()
            
            # Stop review timer
            if hasattr(self, 'review_timer') and self.review_timer:
                self.review_timer.stop()
            
            # Stop camera
            if hasattr(self, 'camera_manager') and self.camera_manager:
                self.camera_manager.stop_camera()
            
            # Close viewer window
            if hasattr(self, 'viewer_window') and self.viewer_window:
                self.viewer_window.close()
            
            # Close database
            if hasattr(self, 'session_manager') and self.session_manager:
                self.session_manager.close()
            
            # QR server will auto-cleanup as daemon thread
            
            print("[SHUTDOWN] Cleanup complete")
            event.accept()
            
        except Exception as e:
            print(f"[SHUTDOWN] Error during cleanup: {e}")
            event.accept()  # Accept anyway to allow closing
