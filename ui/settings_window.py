"""
AIra Pro Photobooth - Settings Window
Professional settings dialog with tabbed interface
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QComboBox, QSpinBox, QCheckBox, QLineEdit, QPushButton,
    QGroupBox, QFormLayout, QRadioButton, QButtonGroup, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Color scheme
DARK_BG = "#0A0A0A"
CARD_BG = "#1A1A1A"
INPUT_BG = "#2A2A2A"
GOLD = "#D4AF37"
GREEN = "#4CAF50"
BLUE = "#4A90E2"
RED = "#E74C3C"
WHITE = "#FFFFFF"
GRAY = "#888888"


class SettingsWindow(QDialog):
    """Settings dialog window."""
    
    settings_changed = pyqtSignal(dict)  # Emit when settings are saved
    
    def __init__(self, config_path: str = "config.json"):
        super().__init__()
        self.config_path = Path(config_path)
        self.current_settings = {}
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the settings window UI."""
        self.setWindowTitle("⚙️ AIra Pro Settings")
        self.setMinimumSize(800, 700)
        self.resize(900, 750)
        self.setStyleSheet(f"""
            QDialog {{
                background: {DARK_BG};
            }}
            QLabel {{
                color: {WHITE};
                font-size: 13px;
            }}
            QGroupBox {{
                color: {GOLD};
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {GOLD};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QTabWidget::pane {{
                border: 1px solid #333;
                border-radius: 5px;
                background: {CARD_BG};
            }}
            QTabBar::tab {{
                background: {INPUT_BG};
                color: {WHITE};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QTabBar::tab:selected {{
                background: {GOLD};
                color: {DARK_BG};
                font-weight: bold;
            }}
            QComboBox, QSpinBox, QLineEdit {{
                background: {INPUT_BG};
                color: {WHITE};
                border: 1px solid #444;
                border-radius: 5px;
                padding: 6px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QCheckBox {{
                color: {WHITE};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {GOLD};
                border-radius: 3px;
                background: {INPUT_BG};
            }}
            QCheckBox::indicator:checked {{
                background: {GOLD};
            }}
            QRadioButton {{
                color: {WHITE};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {GOLD};
                border-radius: 9px;
                background: {INPUT_BG};
            }}
            QRadioButton::indicator:checked {{
                background: {GOLD};
                border: 4px solid {DARK_BG};
            }}
            QPushButton {{
                background: {GOLD};
                color: {DARK_BG};
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #E5C048;
            }}
            QPushButton:pressed {{
                background: #C49F2F;
            }}
            QPushButton#secondary {{
                background: {INPUT_BG};
                color: {WHITE};
                border: 1px solid {GOLD};
            }}
            QPushButton#secondary:hover {{
                background: {CARD_BG};
            }}
            QPushButton#danger {{
                background: {RED};
                color: {WHITE};
            }}
            QPushButton#danger:hover {{
                background: #C0392B;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {GOLD}; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Customize your photobooth experience")
        subtitle.setStyleSheet(f"color: {GRAY}; font-size: 12px;")
        layout.addWidget(subtitle)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self._create_camera_tab()
        self._create_display_tab()
        self._create_print_tab()
        self._create_qr_tab()
        self._create_storage_tab()
        self._create_network_tab()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.setObjectName("danger")
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        btn_layout.addWidget(self.reset_btn)
        
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_camera_tab(self):
        """Create camera settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Camera Selection
        camera_group = QGroupBox("📷 Camera")
        camera_layout = QFormLayout(camera_group)
        
        self.camera_index = QComboBox()
        self.camera_index.addItems(["Camera 0 (Default)", "Camera 1", "Camera 2", "Camera 3"])
        camera_layout.addRow("Camera Device:", self.camera_index)
        
        self.camera_resolution = QComboBox()
        self.camera_resolution.addItems([
            "1920x1080 (Full HD)",
            "1280x720 (HD)",
            "2560x1440 (2K)",
            "3840x2160 (4K)"
        ])
        camera_layout.addRow("Resolution:", self.camera_resolution)
        
        self.camera_fps = QSpinBox()
        self.camera_fps.setRange(10, 60)
        self.camera_fps.setValue(15)
        camera_layout.addRow("Frame Rate (FPS):", self.camera_fps)
        
        layout.addWidget(camera_group)
        
        # Image Settings
        image_group = QGroupBox("🎨 Image Quality")
        image_layout = QFormLayout(image_group)
        
        self.image_quality = QSpinBox()
        self.image_quality.setRange(50, 100)
        self.image_quality.setValue(90)
        self.image_quality.setSuffix("%")
        image_layout.addRow("JPEG Quality:", self.image_quality)
        
        self.mirror_mode = QCheckBox("Mirror/Flip Preview")
        self.mirror_mode.setChecked(True)
        image_layout.addRow(self.mirror_mode)
        
        self.auto_focus = QCheckBox("Auto-Focus")
        self.auto_focus.setChecked(True)
        image_layout.addRow(self.auto_focus)
        
        layout.addWidget(image_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "📷 Camera")
    
    def _create_display_tab(self):
        """Create display settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Countdown Settings
        countdown_group = QGroupBox("⏱️ Countdown")
        countdown_layout = QFormLayout(countdown_group)
        
        self.countdown_duration = QSpinBox()
        self.countdown_duration.setRange(1, 10)
        self.countdown_duration.setValue(5)
        self.countdown_duration.setSuffix(" seconds")
        countdown_layout.addRow("Countdown Duration:", self.countdown_duration)
        
        self.countdown_sound = QCheckBox("Play Beep Sound")
        self.countdown_sound.setChecked(True)
        countdown_layout.addRow(self.countdown_sound)
        
        layout.addWidget(countdown_group)
        
        # Preview Settings
        preview_group = QGroupBox("👁️ Photo Preview")
        preview_layout = QFormLayout(preview_group)
        
        self.preview_duration = QSpinBox()
        self.preview_duration.setRange(3, 30)
        self.preview_duration.setValue(10)
        self.preview_duration.setSuffix(" seconds")
        preview_layout.addRow("Show Preview For:", self.preview_duration)
        
        self.show_countdown_overlay = QCheckBox("Show Countdown Overlay")
        self.show_countdown_overlay.setChecked(True)
        preview_layout.addRow(self.show_countdown_overlay)
        
        layout.addWidget(preview_group)
        
        # UI Settings
        ui_group = QGroupBox("🎨 User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.theme = QComboBox()
        self.theme.addItems(["Dark (Default)", "Light", "High Contrast"])
        ui_layout.addRow("Theme:", self.theme)
        
        self.idle_message = QLineEdit()
        self.idle_message.setText("Tap the button to start!")
        self.idle_message.setPlaceholderText("Message shown on idle screen")
        ui_layout.addRow("Idle Screen Message:", self.idle_message)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "🎨 Display")
    
    def _create_print_tab(self):
        """Create print settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Print Settings
        print_group = QGroupBox("🖨️ Printer")
        print_layout = QFormLayout(print_group)
        
        self.auto_print = QCheckBox("Auto-Print After Capture")
        self.auto_print.setChecked(False)
        print_layout.addRow(self.auto_print)
        
        self.print_copies = QSpinBox()
        self.print_copies.setRange(1, 10)
        self.print_copies.setValue(1)
        self.print_copies.setSuffix(" copies")
        print_layout.addRow("Default Copies:", self.print_copies)
        
        self.print_quality = QComboBox()
        self.print_quality.addItems(["Draft (Fast)", "Normal", "High Quality"])
        self.print_quality.setCurrentIndex(1)
        print_layout.addRow("Print Quality:", self.print_quality)
        
        self.paper_size = QComboBox()
        self.paper_size.addItems(["4x6 inches", "5x7 inches", "A4"])
        print_layout.addRow("Paper Size:", self.paper_size)
        
        layout.addWidget(print_group)
        
        # Print Dialog
        dialog_group = QGroupBox("💬 Print Dialog")
        dialog_layout = QFormLayout(dialog_group)
        
        self.show_print_dialog = QCheckBox("Show Print Dialog Before Printing")
        self.show_print_dialog.setChecked(True)
        dialog_layout.addRow(self.show_print_dialog)
        
        self.show_retake_option = QCheckBox("Show Retake Option")
        self.show_retake_option.setChecked(True)
        dialog_layout.addRow(self.show_retake_option)
        
        layout.addWidget(dialog_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "🖨️ Print")
    
    def _create_qr_tab(self):
        """Create QR code settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # QR Code Settings
        qr_group = QGroupBox("📱 QR Code")
        qr_layout = QFormLayout(qr_group)
        
        self.qr_enabled = QCheckBox("Enable QR Code Generation")
        self.qr_enabled.setChecked(True)
        qr_layout.addRow(self.qr_enabled)
        
        self.qr_size = QComboBox()
        self.qr_size.addItems(["Small (300x300)", "Medium (400x400)", "Large (500x500)"])
        self.qr_size.setCurrentIndex(1)
        qr_layout.addRow("QR Code Size:", self.qr_size)
        
        self.qr_visible_by_default = QCheckBox("Show QR on Client Display by Default")
        self.qr_visible_by_default.setChecked(True)
        qr_layout.addRow(self.qr_visible_by_default)
        
        layout.addWidget(qr_group)
        
        # Download Page
        download_group = QGroupBox("🌐 Download Page")
        download_layout = QFormLayout(download_group)
        
        self.download_title = QLineEdit()
        self.download_title.setText("Your Photo is Ready!")
        download_layout.addRow("Page Title:", self.download_title)
        
        self.download_message = QLineEdit()
        self.download_message.setText("Scan the QR code or tap the button below to download")
        download_layout.addRow("Instructions:", self.download_message)
        
        layout.addWidget(download_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "📱 QR Code")
    
    def _create_storage_tab(self):
        """Create storage settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Export Settings
        export_group = QGroupBox("💾 Export")
        export_layout = QFormLayout(export_group)
        
        self.auto_export_usb = QCheckBox("Auto-Export to USB Drive")
        self.auto_export_usb.setChecked(False)
        export_layout.addRow(self.auto_export_usb)
        
        self.export_folder = QLineEdit()
        self.export_folder.setPlaceholderText("Select export folder...")
        export_layout.addRow("Export Folder:", self.export_folder)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.clicked.connect(self._browse_export_folder)
        export_layout.addRow("", browse_btn)
        
        layout.addWidget(export_group)
        
        # Cleanup
        cleanup_group = QGroupBox("🗑️ Auto-Cleanup")
        cleanup_layout = QFormLayout(cleanup_group)
        
        self.auto_cleanup = QCheckBox("Auto-Delete Old Photos")
        self.auto_cleanup.setChecked(False)
        cleanup_layout.addRow(self.auto_cleanup)
        
        self.cleanup_days = QSpinBox()
        self.cleanup_days.setRange(7, 365)
        self.cleanup_days.setValue(30)
        self.cleanup_days.setSuffix(" days")
        self.cleanup_days.setEnabled(False)
        self.auto_cleanup.toggled.connect(self.cleanup_days.setEnabled)
        cleanup_layout.addRow("Delete Photos Older Than:", self.cleanup_days)
        
        layout.addWidget(cleanup_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "💾 Storage")
    
    def _create_network_tab(self):
        """Create network settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Network Mode
        network_group = QGroupBox("🌐 Network")
        network_layout = QFormLayout(network_group)
        
        self.default_network_mode = QComboBox()
        self.default_network_mode.addItems(["Internet Mode (Cloudflare)", "Local Network Only"])
        network_layout.addRow("Default Mode:", self.default_network_mode)
        
        self.qr_server_port = QSpinBox()
        self.qr_server_port.setRange(8000, 9000)
        self.qr_server_port.setValue(8080)
        network_layout.addRow("QR Server Port:", self.qr_server_port)
        
        layout.addWidget(network_group)
        
        # Cloudflare
        cloudflare_group = QGroupBox("☁️ Cloudflare Tunnel")
        cloudflare_layout = QFormLayout(cloudflare_group)
        
        self.cloudflare_auto_start = QCheckBox("Auto-Start Cloudflare Tunnel")
        self.cloudflare_auto_start.setChecked(True)
        cloudflare_layout.addRow(self.cloudflare_auto_start)
        
        info_label = QLabel("Note: Cloudflare generates a new URL each time the app starts")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {GRAY}; font-size: 11px;")
        cloudflare_layout.addRow("", info_label)
        
        layout.addWidget(cloudflare_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "🌐 Network")
    
    def _load_settings(self):
        """Load settings from config.json."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.current_settings = json.load(f)
                
                # Apply settings to UI
                self._apply_settings_to_ui()
                logger.info(f"Settings loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            QMessageBox.warning(self, "Warning", f"Could not load settings: {e}")
    
    def _apply_settings_to_ui(self):
        """Apply loaded settings to UI controls."""
        settings = self.current_settings
        
        # Camera settings
        if 'camera' in settings:
            cam = settings['camera']
            self.camera_fps.setValue(cam.get('fps', 15))
            self.image_quality.setValue(cam.get('quality', 90))
        
        if 'mirror_mode' in settings:
            self.mirror_mode.setChecked(settings['mirror_mode'])
        
        # Display settings
        if 'countdown_duration' in settings:
            self.countdown_duration.setValue(settings['countdown_duration'])
        
        if 'preview_duration' in settings:
            self.preview_duration.setValue(settings['preview_duration'])
        
        if 'idle_message' in settings:
            self.idle_message.setText(settings['idle_message'])
        
        # Print settings
        if 'print' in settings:
            prt = settings['print']
            self.auto_print.setChecked(prt.get('auto_print', False))
            self.print_copies.setValue(prt.get('copies', 1))
        
        # QR settings
        if 'qr_code' in settings:
            qr = settings['qr_code']
            self.qr_enabled.setChecked(qr.get('enabled', True))
            self.qr_visible_by_default.setChecked(qr.get('visible_by_default', True))
        
        if 'download_message' in settings:
            self.download_message.setText(settings['download_message'])
        
        # Storage settings
        if 'storage' in settings:
            stor = settings['storage']
            self.auto_export_usb.setChecked(stor.get('auto_export_usb', False))
            self.auto_cleanup.setChecked(stor.get('auto_cleanup', False))
            self.cleanup_days.setValue(stor.get('cleanup_days', 30))
        
        # Network settings
        if 'network' in settings:
            net = settings['network']
            self.qr_server_port.setValue(net.get('port', 8080))
            self.cloudflare_auto_start.setChecked(net.get('cloudflare_auto_start', True))
    
    def _collect_settings(self):
        """Collect all settings from UI."""
        settings = self.current_settings.copy()
        
        # Camera
        settings['camera'] = {
            'fps': self.camera_fps.value(),
            'quality': self.image_quality.value(),
            'frame_skip': 2
        }
        settings['mirror_mode'] = self.mirror_mode.isChecked()
        
        # Display
        settings['countdown_duration'] = self.countdown_duration.value()
        settings['preview_duration'] = self.preview_duration.value()
        settings['idle_message'] = self.idle_message.text()
        
        # Print
        settings['print'] = {
            'auto_print': self.auto_print.isChecked(),
            'copies': self.print_copies.value(),
            'quality': self.print_quality.currentText(),
            'paper_size': self.paper_size.currentText()
        }
        
        # QR Code
        settings['qr_code'] = {
            'enabled': self.qr_enabled.isChecked(),
            'visible_by_default': self.qr_visible_by_default.isChecked()
        }
        settings['download_title'] = self.download_title.text()
        settings['download_message'] = self.download_message.text()
        
        # Storage
        settings['storage'] = {
            'auto_export_usb': self.auto_export_usb.isChecked(),
            'auto_cleanup': self.auto_cleanup.isChecked(),
            'cleanup_days': self.cleanup_days.value()
        }
        
        # Network
        settings['network'] = {
            'port': self.qr_server_port.value(),
            'cloudflare_auto_start': self.cloudflare_auto_start.isChecked()
        }
        
        return settings
    
    def _save_settings(self):
        """Save settings to config.json."""
        try:
            settings = self._collect_settings()
            
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"Settings saved to {self.config_path}")
            
            QMessageBox.information(
                self, 
                "Success", 
                "✅ Settings saved successfully!\n\nSome settings may require restarting the app."
            )
            
            # Emit signal
            self.settings_changed.emit(settings)
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._apply_settings_to_ui()
            QMessageBox.information(self, "Reset Complete", "Settings have been reset to defaults.")
    
    def _browse_export_folder(self):
        """Browse for export folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Export Folder",
            str(Path.cwd())
        )
        if folder:
            self.export_folder.setText(folder)
