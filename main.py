"""
SnapFrame Pro - Main Entry Point
Photobooth application with complete testable UI.
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from config import config
from ui.operator_window import OperatorWindow


def setup_logging():
    """Setup application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )


def setup_application():
    """Setup QApplication with optimizations."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName(config.app_name)
    app.setApplicationVersion(config.version)
    app.setOrganizationName("SnapFrame")
    
    # Set default font
    font = QFont(config.get('ui.font_family', 'Segoe UI'), config.get_font_size())
    app.setFont(font)
    
    # Set Fusion style for consistent look
    app.setStyle('Fusion')
    
    return app


def main():
    """Main application entry point."""
    print("=" * 60)
    print(f"  {config.app_name} v{config.version}")
    print("  UI Test Mode - Mock Data Enabled")
    print("=" * 60)
    print()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {config.app_name} v{config.version}")
    
    # Setup application
    app = setup_application()
    
    # Create and show main window
    window = OperatorWindow()
    window.show()
    
    logger.info("Application started successfully")
    print("✅ Application started successfully!")
    print("📝 All buttons are clickable with console feedback")
    print("🎨 Theme toggle: Click '🌙 Dark' button in top bar")
    print("👁️ Viewer window: Click '👁️ Viewer' button")
    print("📸 Capture flow: Select frame → Click CAPTURE")
    print()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
