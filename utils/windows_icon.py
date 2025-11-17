"""
Windows-specific icon handling for taskbar
"""
import sys
import ctypes
from pathlib import Path

if sys.platform == "win32":
    try:
        from ctypes import wintypes
    except ImportError:
        pass


def set_taskbar_icon(window_handle, icon_path: Path):
    """
    Set the taskbar icon for a window using Windows API
    This ensures the icon appears correctly in the taskbar even when running as Python script
    """
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
        
        # Load icon from file using LoadImage
        # LoadImageW signature: HANDLE LoadImageW(HINSTANCE, LPCWSTR, UINT, int, int, UINT)
        icon_path_str = str(icon_path.absolute())
        
        # Load the icon (returns HICON handle)
        hicon = user32.LoadImageW(
            None,  # hInst - NULL means load from file
            icon_path_str,
            IMAGE_ICON,
            0,  # cx - 0 means use default size
            0,  # cy - 0 means use default size
            LR_LOADFROMFILE | LR_DEFAULTSIZE
        )
        
        if hicon:
            # Send WM_SETICON message to set both small and big icons
            user32.SendMessageW(window_handle, WM_SETICON, ICON_SMALL, hicon)
            user32.SendMessageW(window_handle, WM_SETICON, ICON_BIG, hicon)
            return True
        else:
            # Try alternative: use ExtractIcon or Shell32
            try:
                shell32 = ctypes.windll.shell32
                # ExtractIconEx can also be used, but LoadImage is simpler
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

