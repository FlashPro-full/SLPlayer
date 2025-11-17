"""
Media player panel with chessboard background and black rectangle working area
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from typing import Optional
from core.program_manager import Program


class MediaPlayerPanel(QWidget):
    """Media player panel with chessboard background and content area"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #FFFFFF;")
    
    def set_program(self, program: Optional[Program]):
        """Set the current program"""
        self.current_program = program
        self.update()
    
    def paintEvent(self, event):
        """Paint the chessboard background and black rectangle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        checker_size = 20
        checker_color1 = QColor(240, 240, 240)
        checker_color2 = QColor(255, 255, 255)
        
        for y in range(0, height, checker_size):
            for x in range(0, width, checker_size):
                is_dark = ((x // checker_size) + (y // checker_size)) % 2 == 0
                color = checker_color1 if is_dark else checker_color2
                painter.fillRect(x, y, checker_size, checker_size, color)
        
        if self.current_program and "screen" in self.current_program.properties:
            screen_props = self.current_program.properties["screen"]
            screen_width = screen_props.get("width", self.current_program.width)
            screen_height = screen_props.get("height", self.current_program.height)
            rotate = screen_props.get("rotate", 0)
            
            if screen_width > 0 and screen_height > 0:
                scale_x = width / max(screen_width, 1)
                scale_y = height / max(screen_height, 1)
                scale = min(scale_x, scale_y) * 0.9
                
                rect_width = int(screen_width * scale)
                rect_height = int(screen_height * scale)
                
                rect_x = (width - rect_width) // 2
                rect_y = (height - rect_height) // 2
                
                painter.save()
                painter.translate(rect_x + rect_width // 2, rect_y + rect_height // 2)
                painter.rotate(rotate)
                painter.translate(-rect_width // 2, -rect_height // 2)
                
                black_rect = QRect(0, 0, rect_width, rect_height)
                
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.setBrush(QBrush(QColor(0, 0, 0)))
                painter.drawRect(black_rect)
                
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(black_rect)
                
                painter.restore()

