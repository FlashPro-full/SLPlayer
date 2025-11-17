"""
Application data directory utilities
Handles Windows AppData/Local path for production
"""
import os
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    """
    Get application data directory for production version.
    
    On Windows: C:/Users/{User}/AppData/Local/SLPlayer/
    On other platforms: ~/.slplayer/ (fallback)
    
    Returns:
        Path to application data directory
    """
    if sys.platform == "win32":
        # Windows: Use AppData/Local/SLPlayer
        app_data = os.getenv("LOCALAPPDATA")
        if app_data:
            return Path(app_data) / "SLPlayer"
        else:
            # Fallback if LOCALAPPDATA not set
            return Path.home() / "AppData" / "Local" / "SLPlayer"
    else:
        # Non-Windows: Use ~/.slplayer (backward compatible)
        return Path.home() / ".slplayer"


def get_licenses_dir() -> Path:
    """Get licenses directory"""
    return get_app_data_dir() / "licenses"


def get_settings_file() -> Path:
    """Get settings file path"""
    return get_app_data_dir() / "settings.json"


def get_credentials_file() -> Path:
    """Get credentials file path"""
    return get_app_data_dir() / "credentials.json"


def get_session_file() -> Path:
    """Get session file path"""
    return get_app_data_dir() / "session.json"


def get_backup_dir() -> Path:
    """Get backup directory"""
    return get_app_data_dir() / "backups"


def get_auto_save_dir() -> Path:
    """Get auto-save directory"""
    return get_app_data_dir() / "autosave"


def ensure_app_data_dir() -> Path:
    """
    Ensure application data directory exists.
    
    Returns:
        Path to application data directory
    """
    app_data_dir = get_app_data_dir()
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir

