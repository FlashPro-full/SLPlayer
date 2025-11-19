from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen


class LoadingSpinner(QWidget):
    
    def __init__(self, parent=None, size=32, color=None):
        super().__init__(parent)
        self.size = size
        self.color = QColor(color if color else "#2196F3")
        self._angle = 0
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)
        

        self.animation = QPropertyAnimation(self, b"angle")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)
        

        self.setVisible(False)
    
    def set_angle(self, value):
        self._angle = value
        self.update()
    
    def get_angle(self):
        return self._angle
    

    angle = pyqtProperty(int, get_angle, set_angle)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        

        pen = QPen(self.color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        

        rect = self.rect()
        margin = 4
        painter.drawArc(
            margin, margin,
            self.width() - margin * 2,
            self.height() - margin * 2,
            (self._angle * 16),
            (270 * 16)
        )
    
    def start(self):
        if not self.animation.state() == QPropertyAnimation.Running:
            self.animation.start()
        self.setVisible(True)
    
    def stop(self):
        self.animation.stop()
        self.setVisible(False)
    
    def set_color(self, color):
        self.color = QColor(color)
        self.update()


class LoadingWidget(QWidget):
    
    def __init__(self, parent=None, text="Loading...", size=32):
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
            self.text_label.setStyleSheet("color: #333333; font-size: 12px;")
            layout.addWidget(self.text_label, alignment=Qt.AlignCenter)
        

        self.setVisible(False)
    
    def start(self):
        self.spinner.start()
        self.setVisible(True)
    
    def stop(self):
        self.spinner.stop()
        self.setVisible(False)
    
    def set_text(self, text: str):
        if self.text_label:
            self.text_label.setText(text)
    
    def set_color(self, color):
        self.spinner.set_color(color)

