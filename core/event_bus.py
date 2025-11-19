from typing import Callable, Dict, List, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from utils.logger import get_logger

logger = get_logger(__name__)


class EventBus(QObject):
    
    program_created = pyqtSignal(object)
    program_updated = pyqtSignal(object)
    program_deleted = pyqtSignal(str)
    program_selected = pyqtSignal(str)
    program_saved = pyqtSignal(object, str)
    program_sent = pyqtSignal(object)
    program_exported_to_usb = pyqtSignal(object, str)
    
    screen_created = pyqtSignal(str)
    screen_updated = pyqtSignal(str)
    screen_deleted = pyqtSignal(str)
    screen_selected = pyqtSignal(str)
    
    file_loaded = pyqtSignal(str)
    file_saved = pyqtSignal(str)
    file_error = pyqtSignal(str, str)
    
    controller_connected = pyqtSignal(object)
    controller_disconnected = pyqtSignal()
    controller_discovered = pyqtSignal(list)
    controller_error = pyqtSignal(str)
    
    ui_refresh_needed = pyqtSignal()
    ui_program_list_refresh = pyqtSignal()
    ui_status_update = pyqtSignal(str)
    
    _instance: Optional['EventBus'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if EventBus._initialized:
            return
        super().__init__()
        EventBus._initialized = True
        self._debounce_timers: Dict[str, QTimer] = {}
        self._throttle_timers: Dict[str, QTimer] = {}
        self._throttle_last_call: Dict[str, float] = {}
    
    def emit_debounced(self, signal: pyqtSignal, *args, delay_ms: int = 300, key: str = None):
        if key is None:
            key = signal.name if hasattr(signal, 'name') else str(signal)
        
        if key in self._debounce_timers:
            self._debounce_timers[key].stop()
        
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: signal.emit(*args))
        timer.start(delay_ms)
        self._debounce_timers[key] = timer
    
    def emit_throttled(self, signal: pyqtSignal, *args, interval_ms: int = 100, key: str = None):
        import time
        if key is None:
            key = signal.name if hasattr(signal, 'name') else str(signal)
        
        current_time = time.time() * 1000
        
        if key not in self._throttle_last_call:
            signal.emit(*args)
            self._throttle_last_call[key] = current_time
            return
        
        elapsed = current_time - self._throttle_last_call[key]
        
        if elapsed >= interval_ms:
            signal.emit(*args)
            self._throttle_last_call[key] = current_time
        else:
            remaining = interval_ms - elapsed
            if key not in self._throttle_timers:
                timer = QTimer()
                timer.setSingleShot(True)
                self._throttle_timers[key] = timer
            
            timer = self._throttle_timers[key]
            timer.stop()
            timer.timeout.connect(lambda: signal.emit(*args))
            timer.start(int(remaining))
            self._throttle_last_call[key] = current_time + remaining


event_bus = EventBus()

