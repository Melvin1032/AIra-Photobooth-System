"""AIra Pro Photobooth System - Configuration Manager
Handles theme, settings, and preferences.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        
        # Default configuration
        return {
            "app_name": "AIra Pro Photobooth System",
            "version": "2.1.0",
            "ui": {
                "theme": "dark",
                "font_family": "Segoe UI",
                "font_size": 13
            }
        }
    
    def save_config(self):
        """Save configuration to JSON file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def get_theme(self) -> str:
        """Get UI theme (dark/light)."""
        return self.get('ui.theme', 'dark')
    
    def set_theme(self, theme: str):
        """Set UI theme."""
        self.set('ui.theme', theme)
        self.save_config()
    
    def get_font_size(self) -> int:
        """Get UI font size."""
        return self.get('ui.font_size', 13)
    
    def get_countdown_seconds(self) -> int:
        """Get countdown duration."""
        return 3  # Default 3 seconds
    
    @property
    def app_name(self) -> str:
        return self.get('app_name', 'AIra Pro Photobooth System')
    
    @property
    def version(self) -> str:
        return self.get('version', '2.1.0')


# Global config instance
config = Config()
