import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush, QFont
from utils.logger import get_logger

logger = get_logger(__name__)


if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        

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
    
    def __init__(self, message: str, message_type: str = "info", duration: int = 1000, parent=None):
        super().__init__(parent)
        self.message = message
        self.message_type = message_type
        self.duration = duration
        

        self.colors = {
            'success': {'bg': '#4CAF50', 'text': '#FFFFFF', 'icon': '✓'},
            'error': {'bg': '#F44336', 'text': '#FFFFFF', 'icon': '✕'},
            'warning': {'bg': '#FF9800', 'text': '#FFFFFF', 'icon': '⚠'},
            'info': {'bg': '#2196F3', 'text': '#FFFFFF', 'icon': 'ℹ'}
        }
        
        self.init_ui()
        self.setup_animation()
        

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)
        self.hide_timer.start(self.duration)
    
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        

        color_info = self.colors.get(self.message_type, self.colors['info'])
        icon_label = QLabel(color_info['icon'])
        icon_label.setStyleSheet(f"color: {color_info['text']}; font-size: 18px; font-weight: bold;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        

        message_label = QLabel(self.message)
        message_label.setStyleSheet(f"color: {color_info['text']}; font-size: 13px; font-weight: 500;")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(message_label)
        

        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        

        self.adjustSize()
    
    def reposition(self):

        screen = QApplication.primaryScreen().availableGeometry()
        screen_full = QApplication.primaryScreen().geometry()
        

        x = screen_full.right() - self.width() - 20
        

        offset_y = 10
        

        for existing_toast in ToastManager._toasts:
            if existing_toast != self and existing_toast.isVisible():
                existing_geo = existing_toast.geometry()

                if abs(existing_geo.right() - x) < 50:
                    offset_y += existing_toast.height() + 10
        

        if sys.platform == "win32" and ctypes and APPBARDATA:
            try:

                abd = APPBARDATA()
                abd.cbSize = ctypes.sizeof(APPBARDATA)
                abd.hWnd = 0
                
                result = ctypes.windll.shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(abd))
                if result:

                    if abd.uEdge == 1:
                        y = screen.top() + offset_y
                    else:
                        y = screen_full.top() + offset_y
                else:
                    y = screen_full.top() + offset_y
            except (OSError, AttributeError, ctypes.ArgumentError):
                y = screen_full.top() + offset_y
        else:

            y = screen_full.top() + offset_y
        
        self.move(x, y)
    
    def setup_animation(self):
        self._opacity = 1.0
        

        self.fade_in_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_anim.setDuration(300)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.OutCubic)
        

        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(300)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_anim.finished.connect(self.close)
        

        self.setWindowOpacity(0.0)
        self.fade_in_anim.start()
    
    def fade_out(self):
        self.fade_out_anim.start()
    
    def paintEvent(self, event):
        color_info = self.colors.get(self.message_type, self.colors['info'])
        bg_color = QColor(color_info['bg'])
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        

        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 8, 8)
        
        super().paintEvent(event)
    
    def showEvent(self, event):
        super().showEvent(event)

        self.adjustSize()
        self.updateGeometry()
        

        self.reposition()


class ToastManager:
    
    _instance = None
    _toasts = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def show(parent, message: str, message_type: str = "info", duration: int = 1000):

        toast = ToastWidget(message, message_type, duration, parent=None)
        

        toast.adjustSize()
        toast.updateGeometry()
        

        toast.reposition()
        
        toast.show()
        

        QTimer.singleShot(10, lambda: toast.reposition())
        

        ToastManager._toasts.append(toast)
        

        def remove_from_list():
            if toast in ToastManager._toasts:
                ToastManager._toasts.remove(toast)
        
        toast.fade_out_anim.finished.connect(remove_from_list)
        
        return toast
    
    @staticmethod
    def success(parent, message: str, duration: int = 1000):
        return ToastManager.show(parent, message, "success", duration)
    
    @staticmethod
    def error(parent, message: str, duration: int = 1000):
        return ToastManager.show(parent, message, "error", duration)
    
    @staticmethod
    def warning(parent, message: str, duration: int = 1000):
        return ToastManager.show(parent, message, "warning", duration)
    
    @staticmethod
    def info(parent, message: str, duration: int = 1000):
        return ToastManager.show(parent, message, "info", duration)

