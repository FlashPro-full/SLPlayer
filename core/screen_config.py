from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal


_current_screen_config: Optional[Dict[str, Any]] = None
_screen_config_manager: Optional['ScreenConfigManager'] = None


class ScreenConfigManager(QObject):
    config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def set_config(self, brand: Optional[str], model: Optional[str], width: int, height: int, rotate: int = 0, controller_id: Optional[str] = None, screen_name: Optional[str] = None):
        global _current_screen_config
        if _current_screen_config is None:
            _current_screen_config = {}
        _current_screen_config.update({
            "brand": brand,
            "model": model,
            "width": width,
            "height": height,
            "rotate": rotate,
            "controller_id": controller_id
        })
        if screen_name is not None:
            _current_screen_config["screen_name"] = screen_name
        self.config_changed.emit(_current_screen_config)
    
    def set_screen_name(self, screen_name: Optional[str]):
        global _current_screen_config
        if _current_screen_config is None:
            _current_screen_config = {}
        _current_screen_config["screen_name"] = screen_name
        self.config_changed.emit(_current_screen_config)


def get_screen_config_manager() -> ScreenConfigManager:
    global _screen_config_manager
    if _screen_config_manager is None:
        _screen_config_manager = ScreenConfigManager()
    return _screen_config_manager


def set_screen_config(brand: Optional[str], model: Optional[str], width: int, height: int, rotate: int = 0, controller_id: Optional[str] = None, screen_name: Optional[str] = None):
    manager = get_screen_config_manager()
    manager.set_config(brand, model, width, height, rotate, controller_id, screen_name)

def set_screen_name(screen_name: Optional[str]):
    manager = get_screen_config_manager()
    manager.set_screen_name(screen_name)

def get_screen_name() -> Optional[str]:
    global _current_screen_config
    if not _current_screen_config:
        return None
    return _current_screen_config.get("screen_name")


def get_screen_config() -> Optional[Dict[str, Any]]:
    global _current_screen_config
    return _current_screen_config


def get_controller_display_name() -> str:
    global _current_screen_config
    if not _current_screen_config:
        return ""
    brand = _current_screen_config.get("brand", "")
    model = _current_screen_config.get("model", "")
    if brand and model:
        return f"{brand} · {model}"
    elif brand:
        return brand
    elif model:
        return model
    return ""

