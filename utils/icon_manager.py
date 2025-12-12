import sys
from pathlib import Path
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from utils.logger import get_logger

logger = get_logger(__name__)


class IconManager:
    
    @staticmethod
    def setup_application_icon(app, base_path: Path) -> bool:
        icon_path = base_path / "resources" / "app.ico"
        if not icon_path.exists():
            icon_path = base_path / "_internal" / "resources" / "app.ico"
        if icon_path.exists():
            icon = QIcon(str(icon_path.absolute()))
            app.setWindowIcon(icon)
            logger.info(f"Application icon set: {icon_path}")
            return True
        else:
            logger.warning(f"Icon file not found: {icon_path}")
            for alt_name in ["icon.ico", "app_icon.ico", "SLPlayer.ico", "icon.png"]:
                alt_path = base_path / "resources" / alt_name
                if alt_path.exists():
                    icon = QIcon(str(alt_path.absolute()))
                    app.setWindowIcon(icon)
                    logger.info(f"Using alternative icon: {alt_path}")
                    return True
        return False
    
    @staticmethod
    def setup_taskbar_icon(window, base_path: Path) -> None:

        if sys.platform != "win32":
            return
        
        try:
            from utils.windows_icon import set_taskbar_icon
        except ImportError:
            return
        
        icon_path = base_path / "resources" / "app.ico"
        if icon_path.exists():
            def set_icon():
                try:
                    window_handle = int(window.winId())
                    if set_taskbar_icon(window_handle, icon_path):
                        logger.info(f"Taskbar icon set successfully: {icon_path}")
                    else:
                        logger.warning("Failed to set taskbar icon via Windows API")
                except Exception as e:
                    logger.warning(f"Could not set taskbar icon: {e}")
            

            QTimer.singleShot(100, set_icon)
        else:
            logger.warning(f"Taskbar icon file not found: {icon_path}")

