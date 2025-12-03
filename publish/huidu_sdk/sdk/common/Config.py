import os
from pathlib import Path
from typing import Optional


class Config:
    host: Optional[str] = None
    sdk_key: Optional[str] = None
    sdk_secret: Optional[str] = None

    @classmethod
    def init_sdk(cls, host: Optional[str] = None,
                 sdk_key: Optional[str] = None,
                 sdk_secret: Optional[str] = None):
        if host:
            cls.host = host
        if sdk_key:
            cls.sdk_key = sdk_key
        if sdk_secret:
            cls.sdk_secret = sdk_secret

        # If not all parameters provided, try loading from file
        if not all([cls.host, cls.sdk_key, cls.sdk_secret]):
            cls._init_from_file()

    @classmethod
    def _init_from_file(cls):
        # Default file path
        file_path = Path("huidusdk/src/main/resources/application.properties")

        # Try alternative paths if default doesn't exist
        if not file_path.exists():
            # Try in current directory
            file_path = Path("application.properties")
            if not file_path.exists():
                # Try in config directory
                file_path = Path("config/application.properties")

        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()

                                if key == "host":
                                    cls.host = value
                                elif key == "sdkKey":
                                    cls.sdk_key = value
                                elif key == "sdkSecret":
                                    cls.sdk_secret = value
            except Exception:
                # Silently ignore errors like the Java version
                pass


# Initialize configuration when module is imported
Config.init_sdk()