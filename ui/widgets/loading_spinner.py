"""
Loading spinner widget for indicating async operations
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen


class LoadingSpinner(QWidget):
    """Animated loading spinner widget"""
    
    def __init__(self, parent=None, size=32, color=None):
        """
        Initialize loading spinner
        
        Args:
            parent: Parent widget
            size: Size of spinner in pixels
            color: Color of spinner (default: #2196F3)
        """
        super().__init__(parent)
        self.size = size
        self.color = QColor(color if color else "#2196F3")
        self._angle = 0
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Animation
        self.animation = QPropertyAnimation(self, b"angle")
        self.animation.setDuration(1000)  # 1 second per rotation
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)  # Infinite loop
        
        # Hide by default (don't start animation)
        self.setVisible(False)
    
    def set_angle(self, value):
        """Set rotation angle"""
        self._angle = value
        self.update()
    
    def get_angle(self):
        """Get rotation angle"""
        return self._angle
    
    # Property for animation (must be defined as class attribute)
    angle = pyqtProperty(int, get_angle, set_angle)
    
    def paintEvent(self, event):
        """Paint the spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw spinning circle
        pen = QPen(self.color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Draw arc (incomplete circle)
        rect = self.rect()
        margin = 4
        painter.drawArc(
            margin, margin,
            self.width() - margin * 2,
            self.height() - margin * 2,
            (self._angle * 16),  # Start angle (Qt uses 1/16th of a degree)
            (270 * 16)  # Span angle (270 degrees for 3/4 circle)
        )
    
    def start(self):
        """Start the animation"""
        if not self.animation.state() == QPropertyAnimation.Running:
            self.animation.start()
        self.setVisible(True)
    
    def stop(self):
        """Stop the animation"""
        self.animation.stop()
        self.setVisible(False)
    
    def set_color(self, color):
        """Set spinner color"""
        self.color = QColor(color)
        self.update()


class LoadingWidget(QWidget):
    """Loading widget with spinner and optional text"""
    
    def __init__(self, parent=None, text="Loading...", size=32):
        """
        Initialize loading widget
        
        Args:
            parent: Parent widget
            text: Optional text to display below spinner
            size: Size of spinner in pixels
        """
        super().__init__(parent)
        self.spinner = LoadingSpinner(self, size=size)
        self.text_label = QLabel(text) if text else None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        if self.text_label:
            self.text_label.setAlignment(Qt.AlignCenter)
            self.text_label.setStyleSheet("color: #666; font-size: 11pt;")
            layout.addWidget(self.text_label, alignment=Qt.AlignCenter)
        
        # Hide by default
        self.setVisible(False)
    
    def start(self):
        """Start loading animation"""
        self.spinner.start()
        self.setVisible(True)
    
    def stop(self):
        """Stop loading animation"""
        self.spinner.stop()
        self.setVisible(False)
    
    def set_text(self, text: str):
        """Set loading text"""
        if self.text_label:
            self.text_label.setText(text)
    
    def set_color(self, color):
        """Set spinner color"""
        self.spinner.set_color(color)

