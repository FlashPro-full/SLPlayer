import json
import os
from pathlib import Path
from typing import Any, Dict

from utils.logger import get_logger
from utils.app_data import get_app_data_dir, get_settings_file

logger = get_logger(__name__)


class Settings:

    def __init__(self):
        self.config_dir = get_app_data_dir()
        self.config_file = get_settings_file()
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
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    settings = self.default_settings.copy()
                    settings.update(loaded)
                    settings = self._validate_settings(settings)
                    return settings
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in settings file, using defaults: {e}")
                return self.default_settings.copy()
            except Exception as e:
                logger.exception(f"Error loading settings: {e}")
                return self.default_settings.copy()
        else:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            return self.default_settings.copy()
    
    def save_settings(self):
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
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        keys = key.split('.')
        settings = self.settings
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        settings[keys[-1]] = value
        self.save_settings()
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        validated = self.default_settings.copy()
        validated.update(settings)
        
        if "window" in validated and isinstance(validated["window"], dict):
            window = validated["window"]
            for key in ["width", "height", "x", "y"]:
                if key in window:
                    try:
                        validated["window"][key] = int(window[key])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid window.{key}, using default")
                        validated["window"][key] = self.default_settings["window"][key]
        
        if "canvas" in validated and isinstance(validated["canvas"], dict):
            canvas = validated["canvas"]
            if "width" in canvas or "height" in canvas:
                if "width" in canvas:
                    try:
                        validated["canvas"]["width"] = int(canvas["width"])
                    except (ValueError, TypeError):
                        validated["canvas"]["width"] = self.default_settings.get("canvas", {}).get("width", 1920)
                if "height" in canvas:
                    try:
                        validated["canvas"]["height"] = int(canvas["height"])
                    except (ValueError, TypeError):
                        validated["canvas"]["height"] = self.default_settings.get("canvas", {}).get("height", 1080)
        
        if "auto_save" in validated:
            validated["auto_save"] = bool(validated["auto_save"])
        
        if "auto_save_interval" in validated:
            try:
                validated["auto_save_interval"] = int(validated["auto_save_interval"])
                if validated["auto_save_interval"] < 1:
                    validated["auto_save_interval"] = 300
            except (ValueError, TypeError):
                validated["auto_save_interval"] = 300
        
        return validated


settings = Settings()

