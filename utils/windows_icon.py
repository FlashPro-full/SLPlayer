import sys
import ctypes
from pathlib import Path

if sys.platform == "win32":
    try:
        from ctypes import wintypes
    except ImportError:
        pass


def set_taskbar_icon(window_handle, icon_path: Path):

    if sys.platform != "win32":
        return False
    
    if not icon_path.exists():
        return False
    
    try:
        user32 = ctypes.windll.user32
        
        # Constants
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1
        
        icon_path_str = str(icon_path.absolute())
        
        hicon = user32.LoadImageW(
            None,
            icon_path_str,
            IMAGE_ICON,
            0,
            0,
            LR_LOADFROMFILE | LR_DEFAULTSIZE
        )
        
        if hicon:

            user32.SendMessageW(window_handle, WM_SETICON, ICON_SMALL, hicon)
            user32.SendMessageW(window_handle, WM_SETICON, ICON_BIG, hicon)
            return True
        else:

            try:
                shell32 = ctypes.windll.shell32
                pass
            except Exception as e:
                from utils.logger import get_logger
                logger = get_logger(__name__)
                logger.debug(f"Alternative icon loading method failed: {e}")
                
    except Exception as e:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.warning(f"Error setting taskbar icon: {e}", exc_info=True)
    
    return False

