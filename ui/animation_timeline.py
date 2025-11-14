"""
Animation timeline widget for editing animations and keyframes
"""
from typing import Dict, List, Optional, Callable
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame, QSlider, QSpinBox,
                             QComboBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent, QWheelEvent
from utils.logger import get_logger

logger = get_logger(__name__)


class TimelineRuler(QWidget):
    """Ruler showing time markers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration = 10.0  # seconds
        self.zoom = 1.0
        self.pixels_per_second = 50.0
        self.setFixedHeight(30)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # Draw time markers
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        
        seconds_per_marker = max(0.1, 1.0 / self.zoom)
        start_time = 0.0
        
        while start_time <= self.duration:
            x = int(start_time * self.pixels_per_second * self.zoom)
            if x > self.width():
                break
            
            # Major marker every second
            if int(start_time) == start_time:
                painter.drawLine(x, 0, x, self.height())
                painter.drawText(x + 2, self.height() - 5, f"{int(start_time)}s")
            else:
                # Minor marker
                painter.drawLine(x, self.height() - 10, x, self.height())
            
            start_time += seconds_per_marker


class TimelineTrack(QWidget):
    """Single animation track in the timeline"""
    
    element_selected = pyqtSignal(str)
    
    def __init__(self, element_id: str, element_name: str, parent=None):
        super().__init__(parent)
        self.element_id = element_id
        self.element_name = element_name
        self.duration = 10.0
        self.zoom = 1.0
        self.pixels_per_second = 50.0
        self.keyframes: List[Dict] = []
        self.selected_keyframe: Optional[int] = None
        self.setFixedHeight(40)
        self.setMinimumWidth(500)
    
    def add_keyframe(self, time: float, properties: Dict):
        """Add a keyframe at specified time"""
        keyframe = {
            "time": time,
            "properties": properties.copy()
        }
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k["time"])
        self.update()
    
    def remove_keyframe(self, index: int):
        """Remove keyframe at index"""
        if 0 <= index < len(self.keyframes):
            self.keyframes.pop(index)
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        
        # Draw element name
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawText(5, 20, self.element_name)
        
        # Draw keyframes
        for i, keyframe in enumerate(self.keyframes):
            x = int(keyframe["time"] * self.pixels_per_second * self.zoom)
            
            if x < 0 or x > self.width():
                continue
            
            # Draw keyframe marker
            is_selected = i == self.selected_keyframe
            color = QColor(255, 100, 100) if is_selected else QColor(100, 150, 255)
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(x - 5, self.height() // 2 - 5, 10, 10)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse clicks on keyframes"""
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()
            
            # Check if clicking on a keyframe
            for i, keyframe in enumerate(self.keyframes):
                keyframe_x = int(keyframe["time"] * self.pixels_per_second * self.zoom)
                if abs(x - keyframe_x) < 10:
                    self.selected_keyframe = i
                    self.update()
                    return
            
            # If not clicking on keyframe, select element
            self.element_selected.emit(self.element_id)
    
    def get_keyframe_at_time(self, time: float, tolerance: float = 0.1) -> Optional[int]:
        """Get keyframe index at or near specified time"""
        for i, keyframe in enumerate(self.keyframes):
            if abs(keyframe["time"] - time) < tolerance:
                return i
        return None


class AnimationTimeline(QWidget):
    """Main animation timeline widget"""
    
    keyframe_changed = pyqtSignal(str, float, dict)  # element_id, time, properties
    time_changed = pyqtSignal(float)  # current time
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration = 10.0  # seconds
        self.current_time = 0.0
        self.zoom = 1.0
        self.pixels_per_second = 50.0
        self.tracks: List[TimelineTrack] = []
        self.playback_enabled = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize timeline UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(30, 30)
        self.play_btn.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("■")
        self.stop_btn.setFixedSize(30, 30)
        self.stop_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addWidget(QLabel("Time:"))
        self.time_spin = QDoubleSpinBox()
        self.time_spin.setMinimum(0.0)
        self.time_spin.setMaximum(self.duration)
        self.time_spin.setSingleStep(0.1)
        self.time_spin.setValue(0.0)
        self.time_spin.valueChanged.connect(self.on_time_changed)
        controls_layout.addWidget(self.time_spin)
        
        controls_layout.addWidget(QLabel("Duration:"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setMinimum(1.0)
        self.duration_spin.setMaximum(3600.0)
        self.duration_spin.setValue(self.duration)
        self.duration_spin.valueChanged.connect(self.on_duration_changed)
        controls_layout.addWidget(self.duration_spin)
        
        controls_layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.setValue(1)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        controls_layout.addWidget(self.zoom_slider)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Ruler
        self.ruler = TimelineRuler(self)
        self.ruler.duration = self.duration
        self.ruler.zoom = self.zoom
        layout.addWidget(self.ruler)
        
        # Tracks area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        self.tracks_widget = QWidget()
        self.tracks_layout = QVBoxLayout(self.tracks_widget)
        self.tracks_layout.setContentsMargins(0, 0, 0, 0)
        self.tracks_layout.setSpacing(0)
        self.tracks_layout.addStretch()
        
        scroll_area.setWidget(self.tracks_widget)
        layout.addWidget(scroll_area)
        
        # Playback timer
        from PyQt6.QtCore import QTimer
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.update_playback)
        self.playback_timer.setInterval(33)  # ~30 FPS
    
    def add_track(self, element_id: str, element_name: str) -> TimelineTrack:
        """Add a new animation track"""
        track = TimelineTrack(element_id, element_name, self)
        track.duration = self.duration
        track.zoom = self.zoom
        track.element_selected.connect(self.on_element_selected)
        
        # Insert before stretch
        self.tracks_layout.insertWidget(self.tracks_layout.count() - 1, track)
        self.tracks.append(track)
        
        return track
    
    def remove_track(self, element_id: str):
        """Remove a track by element ID"""
        track = next((t for t in self.tracks if t.element_id == element_id), None)
        if track:
            self.tracks.remove(track)
            track.deleteLater()
    
    def get_track(self, element_id: str) -> Optional[TimelineTrack]:
        """Get track by element ID"""
        return next((t for t in self.tracks if t.element_id == element_id), None)
    
    def toggle_playback(self):
        """Toggle playback"""
        if self.playback_enabled:
            self.stop_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start playback"""
        self.playback_enabled = True
        self.play_btn.setText("⏸")
        self.playback_timer.start()
    
    def stop_playback(self):
        """Stop playback"""
        self.playback_enabled = False
        self.play_btn.setText("▶")
        self.playback_timer.stop()
        self.current_time = 0.0
        self.time_spin.setValue(0.0)
        self.time_changed.emit(0.0)
    
    def update_playback(self):
        """Update playback time"""
        self.current_time += 0.033  # ~30 FPS
        if self.current_time >= self.duration:
            self.current_time = 0.0
        
        self.time_spin.setValue(self.current_time)
        self.time_changed.emit(self.current_time)
        self.update()
    
    def on_time_changed(self, time: float):
        """Handle time change"""
        self.current_time = time
        self.time_changed.emit(time)
        self.update()
    
    def on_duration_changed(self, duration: float):
        """Handle duration change"""
        self.duration = duration
        self.ruler.duration = duration
        for track in self.tracks:
            track.duration = duration
        self.update()
    
    def on_zoom_changed(self, zoom_value: int):
        """Handle zoom change"""
        self.zoom = zoom_value
        self.ruler.zoom = self.zoom
        for track in self.tracks:
            track.zoom = self.zoom
        self.update()
    
    def on_element_selected(self, element_id: str):
        """Handle element selection"""
        # Emit signal for parent to handle
        pass

