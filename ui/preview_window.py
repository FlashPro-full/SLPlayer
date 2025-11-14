"""
Preview window for real-time program preview
"""
from typing import Dict, Callable, Optional, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QPaintEvent, QKeyEvent
from core.program_manager import Program
from config.constants import ContentType


class PreviewWidget(QWidget):
    """Widget for displaying preview content"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program_callback: Optional[Callable] = None
        self.draw_callback: Optional[Callable] = None
    
    def set_program_callback(self, callback: Callable):
        """Set callback to get program"""
        self.program_callback = callback
    
    def set_draw_callback(self, callback: Callable[[QPainter, QRect], None]):
        """Set callback to draw content"""
        self.draw_callback = callback
    
    def paintEvent(self, event: QPaintEvent):
        """Paint preview content"""
        if self.draw_callback:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.draw_callback(painter, self.rect())


class PreviewWindow(QWidget):
    """Preview window for displaying program content"""
    
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program: Program = None
        self.playing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.setWindowTitle("Preview")
        self.setMinimumSize(640, 360)
        self.init_ui()
    
    def init_ui(self):
        """Initialize preview UI"""
        layout = QVBoxLayout(self)
        
        # Preview area (will be drawn in paintEvent)
        self.preview_widget = PreviewWidget(self)
        self.preview_widget.setMinimumSize(640, 360)
        self.preview_widget.setStyleSheet("background-color: #000000;")
        self.preview_widget.set_program_callback(lambda: self.program)
        self.preview_widget.set_draw_callback(self.draw_preview_content)
        layout.addWidget(self.preview_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("■ Stop")
        self.stop_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_btn)
        
        self.fullscreen_btn = QPushButton("⛶ Fullscreen")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        controls_layout.addWidget(self.fullscreen_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
    
    def set_program(self, program: Program):
        """Set program to preview"""
        self.program = program
        self.preview_widget.update()
    
    def toggle_playback(self):
        """Toggle playback"""
        if self.playing:
            self.pause_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start preview playback"""
        self.playing = True
        self.play_btn.setText("⏸ Pause")
        self.timer.start(33)  # ~30 FPS
    
    def pause_playback(self):
        """Pause preview playback"""
        self.playing = False
        self.play_btn.setText("▶ Play")
        self.timer.stop()
    
    def stop_playback(self):
        """Stop preview playback"""
        self.playing = False
        self.play_btn.setText("▶ Play")
        self.timer.stop()
        self.preview_widget.update()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("⛶ Fullscreen")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("⛶ Exit Fullscreen")
    
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("⛶ Fullscreen")
        else:
            super().keyPressEvent(event)
    
    def update_preview(self):
        """Update preview display"""
        self.preview_widget.update()
    
    
    def draw_element(self, painter: QPainter, element_data: Dict, offset_x: float, 
                    offset_y: float, scale: float):
        """Draw element in preview"""
        from config.constants import ContentType
        
        element_type = element_data.get("type", "")
        element_x = element_data.get("x", 0) * scale + offset_x
        element_y = element_data.get("y", 0) * scale + offset_y
        element_width = element_data.get("width", 200) * scale
        element_height = element_data.get("height", 100) * scale
        element_props = element_data.get("properties", {})
        
        try:
            content_type = ContentType(element_type)
            
            if content_type == ContentType.TEXT:
                text = element_props.get("text", "Text")
                color = QColor(element_props.get("color", "#FFFFFF"))
                painter.setPen(QPen(color))
                font = painter.font()
                font.setPixelSize(int(24 * scale))
                painter.setFont(font)
                painter.drawText(int(element_x), int(element_y), 
                               int(element_width), int(element_height),
                               Qt.AlignmentFlag.AlignCenter, text)
            
            elif content_type == ContentType.PHOTO:
                file_path = element_props.get("file_path", "")
                if file_path:
                    from PyQt6.QtGui import QPixmap
                    from pathlib import Path
                    if Path(file_path).exists():
                        pixmap = QPixmap(file_path)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(
                                int(element_width), int(element_height),
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            img_x = element_x + (element_width - scaled_pixmap.width()) / 2
                            img_y = element_y + (element_height - scaled_pixmap.height()) / 2
                            painter.drawPixmap(int(img_x), int(img_y), scaled_pixmap)
            
            elif content_type == ContentType.CLOCK:
                from datetime import datetime
                now = datetime.now()
                time_str = now.strftime("%H:%M:%S")
                color = QColor(element_props.get("color", "#FFFFFF"))
                painter.setPen(QPen(color))
                font = painter.font()
                font.setPixelSize(int(48 * scale))
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(int(element_x), int(element_y),
                               int(element_width), int(element_height),
                               Qt.AlignmentFlag.AlignCenter, time_str)
            
            elif content_type == ContentType.NEON:
                # Draw neon effect using resources
                neon_index = element_props.get("neon_index", 0)
                from core.resource_manager import resource_manager
                neon_pixmap = resource_manager.get_neon_background(neon_index)
                if neon_pixmap:
                    scaled_neon = neon_pixmap.scaled(
                        int(element_width), int(element_height),
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    painter.drawPixmap(int(element_x), int(element_y), scaled_neon)
        
        except ValueError:
            pass
    
    def closeEvent(self, event):
        """Handle window close"""
        self.closed.emit()
        super().closeEvent(event)

