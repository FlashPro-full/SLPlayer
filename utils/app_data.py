import os
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    if sys.platform == "win32":
        app_data = os.getenv("LOCALAPPDATA")
        if app_data:
            return Path(app_data) / "SLPlayer"
        else:
            return Path.home() / "AppData" / "Local" / "SLPlayer"
    else:
        return Path.home() / ".slplayer"


def get_licenses_dir() -> Path:
    return get_app_data_dir() / "licenses"


def get_settings_file() -> Path:
    return get_app_data_dir() / "settings.json"


def get_credentials_file() -> Path:
    return get_app_data_dir() / "credentials.json"


def get_session_file() -> Path:
    return get_app_data_dir() / "session.json"


def get_backup_dir() -> Path:
    return get_app_data_dir() / "backups"


def get_auto_save_dir() -> Path:
    return get_app_data_dir() / "autosave"


def ensure_app_data_dir() -> Path:
    app_data_dir = get_app_data_dir()
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir

