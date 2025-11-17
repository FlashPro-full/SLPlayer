"""
Toast notification widget for showing temporary messages
"""
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush, QFont
from utils.logger import get_logger

logger = get_logger(__name__)

# Windows-specific system tray positioning
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        
        # Windows API constants
        ABM_GETTASKBARPOS = 0x00000005
        
        class APPBARDATA(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_uint),
                ("hWnd", wintypes.HWND),
                ("uCallbackMessage", ctypes.c_uint),
                ("uEdge", ctypes.c_uint),
                ("rc", wintypes.RECT),
                ("lParam", ctypes.POINTER(ctypes.c_long)),
            ]
    except ImportError:
        APPBARDATA = None
        ctypes = None
else:
    APPBARDATA = None
    ctypes = None


class ToastWidget(QWidget):
    """Toast notification widget that appears temporarily"""
    
    def __init__(self, message: str, message_type: str = "info", duration: int = 1000, parent=None):
        """
        Initialize toast widget.
        
        Args:
            message: Message to display
            message_type: Type of message ('success', 'error', 'warning', 'info')
            duration: Duration in milliseconds (default: 1000ms - reduced from 3000ms)
            parent: Parent widget
        """
        super().__init__(parent)
        self.message = message
        self.message_type = message_type
        self.duration = duration
        
        # Colors for different message types
        self.colors = {
            'success': {'bg': '#4CAF50', 'text': '#FFFFFF', 'icon': '✓'},
            'error': {'bg': '#F44336', 'text': '#FFFFFF', 'icon': '✗'},
            'warning': {'bg': '#FF9800', 'text': '#FFFFFF', 'icon': '⚠'},
            'info': {'bg': '#2196F3', 'text': '#FFFFFF', 'icon': 'ℹ'}
        }
        
        self.init_ui()
        self.setup_animation()
        
        # Start hide timer (reduced duration)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)
        self.hide_timer.start(self.duration)
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        
        # Icon label
        color_info = self.colors.get(self.message_type, self.colors['info'])
        icon_label = QLabel(color_info['icon'])
        icon_label.setStyleSheet(f"color: {color_info['text']}; font-size: 18px; font-weight: bold;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Message label
        message_label = QLabel(self.message)
        message_label.setStyleSheet(f"color: {color_info['text']}; font-size: 13px; font-weight: 500;")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(message_label)
        
        # Set minimum width
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
        # Adjust size
        self.adjustSize()
    
    def reposition(self):
        """Reposition toast to top-right of Windows system area (taskbar area)"""
        # Position at top-right of screen, accounting for taskbar
        screen = QApplication.primaryScreen().availableGeometry()  # Excludes taskbar
        screen_full = QApplication.primaryScreen().geometry()  # Full screen
        
        # Calculate position at top-right
        x = screen_full.right() - self.width() - 20
        
        # Calculate vertical offset for stacking multiple toasts
        offset_y = 10
        
        # Stack existing toasts
        for existing_toast in ToastManager._toasts:
            if existing_toast != self and existing_toast.isVisible():
                existing_geo = existing_toast.geometry()
                # Check if toast is in the same column (similar x position)
                if abs(existing_geo.right() - x) < 50:  # Within 50 pixels
                    offset_y += existing_toast.height() + 10
        
        # If taskbar is at top, use available geometry; otherwise use full screen
        if sys.platform == "win32" and ctypes and APPBARDATA:
            try:
                # Get taskbar position using Windows API
                abd = APPBARDATA()
                abd.cbSize = ctypes.sizeof(APPBARDATA)
                abd.hWnd = 0
                
                result = ctypes.windll.shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(abd))
                if result:
                    # Taskbar edge: 0=left, 1=top, 2=right, 3=bottom
                    if abd.uEdge == 1:  # Top
                        y = screen.top() + offset_y
                    else:  # Bottom, left, or right
                        y = screen_full.top() + offset_y
                else:
                    y = screen_full.top() + offset_y
            except:
                y = screen_full.top() + offset_y
        else:
            # Non-Windows or API unavailable - use top of full screen
            y = screen_full.top() + offset_y
        
        self.move(x, y)
    
    def setup_animation(self):
        """Setup fade in/out animations"""
        self._opacity = 1.0
        
        # Fade in animation
        self.fade_in_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_anim.setDuration(300)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade out animation
        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(300)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_anim.finished.connect(self.close)
        
        # Start fade in
        self.setWindowOpacity(0.0)
        self.fade_in_anim.start()
    
    def fade_out(self):
        """Start fade out animation"""
        self.fade_out_anim.start()
    
    def paintEvent(self, event):
        """Custom paint event for rounded corners and background"""
        color_info = self.colors.get(self.message_type, self.colors['info'])
        bg_color = QColor(color_info['bg'])
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rectangle background
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 8, 8)
        
        super().paintEvent(event)
    
    def showEvent(self, event):
        """Position toast when shown - at top-right of Windows system area"""
        super().showEvent(event)
        # Adjust size first to get correct dimensions
        self.adjustSize()
        self.updateGeometry()
        
        # Always position at top-right of screen (system area)
        self.reposition()


class ToastManager:
    """Manager for showing toast notifications"""
    
    _instance = None
    _toasts = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def show(parent, message: str, message_type: str = "info", duration: int = 1000):
        """
        Show a toast notification.
        
        Args:
            parent: Parent widget (ignored - positioned at screen system area)
            message: Message to display
            message_type: Type of message ('success', 'error', 'warning', 'info')
            duration: Duration in milliseconds (default: 1000ms - reduced)
        """
        # Create toast without parent for screen positioning
        toast = ToastWidget(message, message_type, duration, parent=None)
        
        # Adjust size first to get correct dimensions
        toast.adjustSize()
        toast.updateGeometry()
        
        # Position toast at top-right of Windows system area
        toast.reposition()
        
        toast.show()
        
        # Reposition after showing to ensure correct placement
        QTimer.singleShot(10, lambda: toast.reposition())
        
        # Add to list
        ToastManager._toasts.append(toast)
        
        # Remove from list when closed
        def remove_from_list():
            if toast in ToastManager._toasts:
                ToastManager._toasts.remove(toast)
        
        toast.fade_out_anim.finished.connect(remove_from_list)
        
        return toast
    
    @staticmethod
    def success(parent, message: str, duration: int = 1000):
        """Show success toast (reduced duration ~3s from 3000ms)"""
        return ToastManager.show(parent, message, "success", duration)
    
    @staticmethod
    def error(parent, message: str, duration: int = 1000):
        """Show error toast (reduced duration ~3s from 4000ms)"""
        return ToastManager.show(parent, message, "error", duration)
    
    @staticmethod
    def warning(parent, message: str, duration: int = 1000):
        """Show warning toast (reduced duration ~3s from 3500ms)"""
        return ToastManager.show(parent, message, "warning", duration)
    
    @staticmethod
    def info(parent, message: str, duration: int = 1000):
        """Show info toast (reduced duration ~3s from 3000ms)"""
        return ToastManager.show(parent, message, "info", duration)

