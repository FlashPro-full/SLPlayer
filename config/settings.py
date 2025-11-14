"""
Application settings and configuration management
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

from utils.logger import get_logger

logger = get_logger(__name__)


class Settings:
    """Manages application settings"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".slplayer"
        self.config_file = self.config_dir / "settings.json"
        self.default_settings = {
            "window": {
                "width": 1400,
                "height": 900,
                "x": 100,
                "y": 100
            },
            "canvas": {
                "background_color": "#FFFFFF",
                "grid_enabled": False,
                "snap_to_grid": False,
                "grid_size": 10
            },
            "controller": {
                "default_port": 5000,
                "connection_timeout": 5
            },
            "language": "en",
            "recent_files": [],
            "auto_save": True,
            "auto_save_interval": 300,  # seconds
            "first_launch_complete": False,
            "license": {
                "api_url": "https://www.starled-italia.com/license/api",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_user": "",
                "smtp_password": "",
                "transfer_email": "license@starled-italia.com"
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.default_settings.copy()
                    settings.update(loaded)
                    return settings
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in settings file, using defaults: {e}")
                return self.default_settings.copy()
            except Exception as e:
                logger.exception(f"Error loading settings: {e}")
                return self.default_settings.copy()
        else:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except PermissionError as e:
            logger.error(f"Permission denied saving settings: {e}")
        except OSError as e:
            logger.error(f"OS error saving settings: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'window.width')"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set a setting value using dot notation"""
        keys = key.split('.')
        settings = self.settings
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        settings[keys[-1]] = value
        self.save_settings()


# Global settings instance
settings = Settings()

