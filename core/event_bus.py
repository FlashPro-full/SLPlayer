"""
Event Bus - Decoupled communication between components
"""
from typing import Callable, Dict, List, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from utils.logger import get_logger

logger = get_logger(__name__)


class EventBus(QObject):
    """
    Centralized event bus for decoupled component communication.
    Uses Qt signals for thread-safe event dispatching.
    """
    
    # Program events
    program_created = pyqtSignal(object)  # Program
    program_updated = pyqtSignal(object)  # Program
    program_deleted = pyqtSignal(str)  # program_id
    program_selected = pyqtSignal(str)  # program_id
    program_saved = pyqtSignal(object, str)  # Program, file_path
    
    # Screen events
    screen_created = pyqtSignal(str)  # screen_name
    screen_updated = pyqtSignal(str)  # screen_name
    screen_deleted = pyqtSignal(str)  # screen_name
    screen_selected = pyqtSignal(str)  # screen_name
    
    # File events
    file_loaded = pyqtSignal(str)  # file_path
    file_saved = pyqtSignal(str)  # file_path
    file_error = pyqtSignal(str, str)  # file_path, error_message
    
    # Controller events
    controller_connected = pyqtSignal(object)  # BaseController
    controller_disconnected = pyqtSignal()
    controller_discovered = pyqtSignal(list)  # List[ControllerInfo]
    controller_error = pyqtSignal(str)  # error_message
    
    # UI events
    ui_refresh_needed = pyqtSignal()
    ui_program_list_refresh = pyqtSignal()
    ui_status_update = pyqtSignal(str)  # status_message
    
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
        """
        Emit a signal after a delay, canceling previous emissions with the same key.
        Useful for search, auto-save, etc.
        
        Args:
            signal: The signal to emit
            *args: Arguments to pass to the signal
            delay_ms: Delay in milliseconds
            key: Unique key for this debounce operation (defaults to signal name)
        """
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
        """
        Emit a signal at most once per interval.
        Useful for scroll events, resize events, etc.
        
        Args:
            signal: The signal to emit
            *args: Arguments to pass to the signal
            interval_ms: Minimum interval between emissions
            key: Unique key for this throttle operation
        """
        import time
        if key is None:
            key = signal.name if hasattr(signal, 'name') else str(signal)
        
        current_time = time.time() * 1000  # Convert to milliseconds
        
        if key not in self._throttle_last_call:
            # First call, emit immediately
            signal.emit(*args)
            self._throttle_last_call[key] = current_time
            return
        
        elapsed = current_time - self._throttle_last_call[key]
        
        if elapsed >= interval_ms:
            # Enough time has passed, emit immediately
            signal.emit(*args)
            self._throttle_last_call[key] = current_time
        else:
            # Schedule emission after remaining time
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


# Global singleton instance
event_bus = EventBus()

