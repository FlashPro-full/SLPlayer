from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QSize, Qt
from core.screen_config import get_screen_config


class ContentWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checker_size = 10
        self.color1 = QtGui.QColor(240, 240, 240)
        self.color2 = QtGui.QColor(255, 255, 255)
        self._cached_pixmap = None
        self._cached_size = QSize()
    
    def paintEvent(self, event):
        rect = self.rect()
        current_size = rect.size()
        
        if self._cached_pixmap is None or self._cached_size != current_size:
            self._cached_pixmap = QtGui.QPixmap(current_size)
            self._cached_pixmap.fill(self.color2)
            
            painter = QtGui.QPainter(self._cached_pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
            
            size = self.checker_size
            for y in range(0, current_size.height(), size):
                for x in range(0, current_size.width(), size):
                    if ((x // size) + (y // size)) % 2 == 0:
                        square_rect = QtCore.QRect(x, y, size, size)
                        painter.fillRect(square_rect, self.color1)
            
            painter.end()
            self._cached_size = current_size
        
        painter = QtGui.QPainter(self)
        painter.drawPixmap(rect.topLeft(), self._cached_pixmap)
        
        config = get_screen_config()
        if config:
            width = config.get("width", 0)
            height = config.get("height", 0)
            if width > 0 and height > 0:
                center_x = current_size.width() / 2
                center_y = current_size.height() / 2
                rect_x = center_x - (width / 2)
                rect_y = center_y - (height / 2)
                rect_x = max(0, min(rect_x, current_size.width() - width))
                rect_y = max(0, min(rect_y, current_size.height() - height))
                black_rect = QtCore.QRect(int(rect_x), int(rect_y), width, height)
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                painter.drawRect(black_rect)
        
        painter.end()
    
    def resizeEvent(self, event):
        self._cached_pixmap = None
        super().resizeEvent(event)
        self.update()

