"""
Media player panel with chessboard background and black rectangle working area
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QTimer, QUrl
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QImage, QFont
from pathlib import Path
from typing import Optional, Dict
from core.program_manager import Program
from media.animation_engine import AnimationEngine, AnimationType
from media.transition_engine import TransitionEngine, TransitionType
from datetime import datetime

# Try to import multimedia components, fallback if not available
try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False
    # Create dummy classes for type hints
    class QMediaPlayer:
        PlayingState = 1
        def __init__(self, *args, **kwargs):
            pass
        def setMedia(self, *args, **kwargs):
            pass
        def setVolume(self, *args, **kwargs):
            pass
        def setVideoOutput(self, *args, **kwargs):
            pass
        def play(self, *args, **kwargs):
            pass
        def stop(self, *args, **kwargs):
            pass
        def state(self):
            return 0
    
    class QMediaContent:
        def __init__(self, *args, **kwargs):
            pass
    
    class QUrl:
        def __init__(self, *args, **kwargs):
            pass
        @staticmethod
        def fromLocalFile(path):
            # Return a dummy QUrl instance
            obj = object.__new__(QUrl)
            return obj
    
    class QVideoWidget(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        def setGeometry(self, *args, **kwargs):
            pass
        def setVisible(self, *args, **kwargs):
            pass
        def setParent(self, *args, **kwargs):
            pass
        def deleteLater(self, *args, **kwargs):
            pass


class MediaPlayerPanel(QWidget):
    """Media player panel with chessboard background and content area"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.current_element_id: Optional[str] = None
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #FFFFFF;")
        
        # Media players for videos (one per element)
        self.media_players: Dict[str, QMediaPlayer] = {}
        self.video_widgets: Dict[str, QVideoWidget] = {}
        
        # Cached images
        self.image_cache: Dict[str, QPixmap] = {}
        
        # Animation and transition engines
        self.animation_engine = AnimationEngine()
        self.transition_engine = TransitionEngine()
        
        # Update timer for animations and dynamic content
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(33)  # ~30 FPS
        
        # Timer to update video positions when properties change
        self._position_update_timer = QTimer(self)
        self._position_update_timer.setSingleShot(True)
        self._position_update_timer.timeout.connect(self._update_video_widget_positions)
    
    def set_program(self, program: Optional[Program]):
        """Set the current program"""
        # Stop all media players when program changes
        self._stop_all_media()
        self.current_program = program
        
        # Setup animations and transitions for elements
        self._setup_animations_and_transitions()
        
        # Setup media players after a short delay to ensure widget is sized
        QTimer.singleShot(100, self._setup_media_players)
        self.update()
    
    def _setup_animations_and_transitions(self):
        """Setup animations and transitions for all elements"""
        if not self.current_program or not self.current_program.elements:
            return
        
        current_time = datetime.now().timestamp()
        
        for element in self.current_program.elements:
            element_id = element.get("id", "")
            element_props = element.get("properties", {})
            
            # Setup animations
            animation_type = element_props.get("animation", {}).get("type")
            if animation_type:
                try:
                    anim_type = AnimationType(animation_type)
                    duration = element_props.get("animation", {}).get("duration", 5.0)
                    speed = element_props.get("animation", {}).get("speed", 1.0)
                    self.animation_engine.add_animation(element_id, anim_type, duration, speed)
                except (ValueError, KeyError):
                    pass
            
            # Setup transitions
            transition_in = element_props.get("display", {}).get("mode", "Immediate Show")
            transition_out = element_props.get("clear", {}).get("mode", "Immediate Clear")
            duration_in = element_props.get("display", {}).get("time", 5) / 1000.0  # Convert ms to seconds
            duration_out = element_props.get("clear", {}).get("time", 5) / 1000.0
            
            if transition_in != "Immediate Show" or transition_out != "Immediate Clear":
                self.transition_engine.add_transition(
                    element_id, transition_in, transition_out, duration_in, duration_out
                )
                # Start transition in
                self.transition_engine.start_transition_in(element_id, current_time)
    
    def set_current_element(self, element_id: Optional[str]):
        """Set the currently selected element ID"""
        self.current_element_id = element_id
        self.update()
    
    def refresh_media(self):
        """Refresh media positions and content - call when properties change"""
        self._position_update_timer.start(50)  # Debounce updates
        self.update()
    
    def resizeEvent(self, event):
        """Handle resize to update video widget positions"""
        super().resizeEvent(event)
        self._update_video_widget_positions()
    
    def _update_video_widget_positions(self):
        """Update positions of all video widgets"""
        from core.screen_params import ScreenParams
        
        screen_width, screen_height = ScreenParams.get_screen_dimensions(self.current_program)
        if not screen_width or not screen_height:
            return
        
        panel_width = self.width()
        panel_height = self.height()
        scale_x = panel_width / max(screen_width, 1)
        scale_y = panel_height / max(screen_height, 1)
        scale = min(scale_x, scale_y) * 0.9
        
        rect_width = int(screen_width * scale)
        rect_height = int(screen_height * scale)
        rect_x = (panel_width - rect_width) // 2
        rect_y = (panel_height - rect_height) // 2
        
        for element in self.current_program.elements:
            element_id = element.get("id", "")
            if element_id in self.video_widgets:
                element_props = element.get("properties", {})
                x = element_props.get("x", element.get("x", 0))
                y = element_props.get("y", element.get("y", 0))
                default_width = screen_width if screen_width else 100
                default_height = screen_height if screen_height else 100
                width = element_props.get("width", element.get("width", default_width))
                height = element_props.get("height", element.get("height", default_height))
                
                # Constrain to screen
                x = max(0, min(x, screen_width - width))
                y = max(0, min(y, screen_height - height))
                width = min(width, screen_width - x)
                height = min(height, screen_height - y)
                
                # Scale to preview coordinates
                elem_x = int(x * scale) + rect_x
                elem_y = int(y * scale) + rect_y
                elem_width = int(width * scale)
                elem_height = int(height * scale)
                
                video_widget = self.video_widgets[element_id]
                video_widget.setGeometry(elem_x, elem_y, elem_width, elem_height)
    
    def _stop_all_media(self):
        """Stop all media players"""
        if not MULTIMEDIA_AVAILABLE:
            self.media_players.clear()
            self.video_widgets.clear()
            return
        
        for player in self.media_players.values():
            try:
                if player.state() == QMediaPlayer.PlayingState:
                    player.stop()
            except Exception:
                pass
        self.media_players.clear()
        for widget in self.video_widgets.values():
            try:
                widget.setParent(None)
                widget.deleteLater()
            except Exception:
                pass
        self.video_widgets.clear()
    
    def _setup_media_players(self):
        """Setup media players for video elements"""
        if not MULTIMEDIA_AVAILABLE:
            return  # Multimedia not available, skip video setup
        
        if not self.current_program or not self.current_program.elements:
            return
        
        # Calculate screen transform for positioning video widgets
        from core.screen_params import ScreenParams
        
        screen_width, screen_height = ScreenParams.get_screen_dimensions(self.current_program)
        if not screen_width or not screen_height:
            return
        
        panel_width = self.width()
        panel_height = self.height()
        scale_x = panel_width / max(screen_width, 1)
        scale_y = panel_height / max(screen_height, 1)
        scale = min(scale_x, scale_y) * 0.9
        
        rect_width = int(screen_width * scale)
        rect_height = int(screen_height * scale)
        rect_x = (panel_width - rect_width) // 2
        rect_y = (panel_height - rect_height) // 2
        
        for element in self.current_program.elements:
            element_type = element.get("type", "").lower()
            element_id = element.get("id", "")
            
            if element_type == "video":
                element_props = element.get("properties", {})
                video_list = element_props.get("video_list", [])
                
                if video_list and len(video_list) > 0:
                    video_path = video_list[0].get("path", "")
                    if video_path and Path(video_path).exists():
                        try:
                            player = QMediaPlayer(self)
                            
                            # Connect error signal to handle playback errors
                            # Use a closure to properly capture element_id
                            def make_error_handler(eid):
                                def error_handler(error):
                                    self._on_media_error(eid, error)
                                return error_handler
                            
                            def make_status_handler(eid):
                                def status_handler(status):
                                    self._on_media_status_changed(eid, status)
                                return status_handler
                            
                            try:
                                if hasattr(player, 'mediaStatusChanged'):
                                    player.mediaStatusChanged.connect(make_status_handler(element_id))
                                if hasattr(player, 'error'):
                                    player.error.connect(make_error_handler(element_id))
                            except Exception as sig_err:
                                print(f"Failed to connect error signals: {sig_err}")
                                pass  # Error signal connection failed, continue anyway
                            
                            # Get element position and size first
                            # Use screen dimensions as defaults
                            x = element_props.get("x", element.get("x", 0))
                            y = element_props.get("y", element.get("y", 0))
                            default_width = screen_width if screen_width else 100
                            default_height = screen_height if screen_height else 100
                            width = element_props.get("width", element.get("width", default_width))
                            height = element_props.get("height", element.get("height", default_height))
                            
                            # Constrain to screen
                            x = max(0, min(x, screen_width - width))
                            y = max(0, min(y, screen_height - height))
                            width = min(width, screen_width - x)
                            height = min(height, screen_height - y)
                            
                            # Scale to preview coordinates
                            elem_x = int(x * scale) + rect_x
                            elem_y = int(y * scale) + rect_y
                            elem_width = int(width * scale)
                            elem_height = int(height * scale)
                            
                            # Create video widget positioned correctly
                            video_widget = QVideoWidget(self)
                            video_widget.setGeometry(elem_x, elem_y, elem_width, elem_height)
                            video_widget.setVisible(True)
                            
                            # Set video output BEFORE setting media
                            player.setVideoOutput(video_widget)
                            
                            # Create QUrl from local file path (matching C++ pattern)
                            media_url = QUrl.fromLocalFile(video_path)
                            media_content = QMediaContent(media_url)
                            player.setMedia(media_content)
                            player.setVolume(100)
                            
                            self.media_players[element_id] = player
                            self.video_widgets[element_id] = video_widget
                            
                            # Store video path for fallback rendering
                            element_props["_video_path"] = video_path
                            
                            # Start playing - errors will be caught by error signal
                            player.play()
                        except Exception as e:
                            # If video playback fails, we'll render a placeholder in paintEvent
                            print(f"Video playback error for {element_id}: {e}")
                            element_props["_video_error"] = True
                            element_props["_video_path"] = video_path
    
    def _load_image(self, image_path: str) -> Optional[QPixmap]:
        """Load and cache an image"""
        if not image_path or not Path(image_path).exists():
            return None
        
        if image_path in self.image_cache:
            return self.image_cache[image_path]
        
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.image_cache[image_path] = pixmap
                return pixmap
        except Exception:
            pass
        
        return None
    
    def _on_media_error(self, element_id: str, error):
        """Handle media player errors"""
        # Mark element as having playback error for fallback rendering
        if self.current_program:
            for element in self.current_program.elements:
                if element.get("id") == element_id:
                    element_props = element.get("properties", {})
                    element_props["_video_error"] = True
                    # Stop and remove the player
                    if element_id in self.media_players:
                        try:
                            self.media_players[element_id].stop()
                        except:
                            pass
                        del self.media_players[element_id]
                    if element_id in self.video_widgets:
                        try:
                            self.video_widgets[element_id].setVisible(False)
                            self.video_widgets[element_id].deleteLater()
                        except:
                            pass
                        del self.video_widgets[element_id]
                    break
        print(f"Media playback error for element {element_id}: {error}")
        self.update()  # Refresh display to show fallback
    
    def _on_media_status_changed(self, element_id: str, status):
        """Handle media status changes - detect invalid media"""
        # QMediaPlayer.InvalidMedia = 1, QMediaPlayer.NoMedia = 0
        if status == 1:  # InvalidMedia
            if self.current_program:
                for element in self.current_program.elements:
                    if element.get("id") == element_id:
                        element_props = element.get("properties", {})
                        element_props["_video_error"] = True
                        break
            print(f"Media status: Invalid media for element {element_id}")
            self.update()  # Refresh display to show fallback
    
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
        
        # Check if screen properties exist - they must be set from screen/controller settings
        from core.screen_params import ScreenParams
        
        screen_width, screen_height = ScreenParams.get_screen_dimensions(self.current_program)
        rotate = ScreenParams.get_screen_rotation(self.current_program)
        
        # Only render if screen dimensions are set (from screen/controller settings)
        if screen_width and screen_height and screen_width > 0 and screen_height > 0:
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
            
            # Draw colorful borders for content items
            if self.current_program and self.current_program.elements:
                for element in self.current_program.elements:
                    element_type = element.get("type", "").lower()
                    element_props = element.get("properties", {})
                    
                    # Get position and size from properties or element directly
                    # Use screen dimensions as defaults
                    x = element_props.get("x", element.get("x", 0))
                    y = element_props.get("y", element.get("y", 0))
                    default_width = screen_width if screen_width else 100
                    default_height = screen_height if screen_height else 100
                    width = element_props.get("width", element.get("width", default_width))
                    height = element_props.get("height", element.get("height", default_height))
                    
                    # Constrain to screen bounds
                    x = max(0, min(x, screen_width - width))
                    y = max(0, min(y, screen_height - height))
                    width = min(width, screen_width - x)
                    height = min(height, screen_height - y)
                    
                    # Scale coordinates to preview size
                    # Elements are positioned relative to the screen (black rectangle)
                    elem_x = int(x * scale)
                    elem_y = int(y * scale)
                    elem_width = int(width * scale)
                    elem_height = int(height * scale)
                    
                    # Choose color based on content type
                    color_map = {
                        "video": QColor(255, 0, 0),      # Red
                        "image": QColor(0, 255, 0),      # Green
                        "picture": QColor(0, 255, 0),     # Green
                        "photo": QColor(0, 255, 0),       # Green
                        "text": QColor(0, 0, 255),       # Blue
                        "singleline_text": QColor(0, 150, 255),  # Light Blue
                        "animation": QColor(255, 165, 0),  # Orange
                        "3d_text": QColor(128, 0, 128),   # Purple
                        "clock": QColor(255, 192, 203),   # Pink
                        "calendar": QColor(0, 255, 255),  # Cyan
                        "timing": QColor(255, 255, 0),   # Yellow
                        "weather": QColor(135, 206, 250), # Sky Blue
                        "neon": QColor(255, 20, 147),    # Deep Pink
                        "wps": QColor(50, 205, 50),      # Lime Green
                        "table": QColor(255, 140, 0),    # Dark Orange
                        "office": QColor(70, 130, 180),  # Steel Blue
                        "digital_watch": QColor(255, 215, 0),  # Gold
                        "html": QColor(34, 139, 34),     # Forest Green
                        "livestream": QColor(220, 20, 60),  # Crimson
                        "qrcode": QColor(75, 0, 130)     # Indigo
                    }
                    
                    border_color = color_map.get(element_type, QColor(255, 255, 255))  # Default white
                    
                    # Make border thicker if this is the selected element
                    element_id = element.get("id", "")
                    is_selected = (element_id == self.current_element_id)
                    border_width = 2 if is_selected else 1
                    
                    # Get animation and transition states
                    current_time = datetime.now().timestamp()
                    anim_state = self.animation_engine.update_animation(element_id, current_time)
                    trans_state = self.transition_engine.get_transition_state(element_id, current_time)
                    
                    # Apply transition transformations (opacity, offset, scale, rotation)
                    opacity = trans_state.get("opacity", 1.0) * (anim_state.get("opacity", 1.0))
                    offset_x = trans_state.get("offset_x", 0) + anim_state.get("offset_x", 0)
                    offset_y = trans_state.get("offset_y", 0) + anim_state.get("offset_y", 0)
                    scale = trans_state.get("scale", 1.0)
                    rotation = trans_state.get("rotation", 0.0)
                    
                    # Calculate transformed position and size
                    scaled_width = int(elem_width * scale)
                    scaled_height = int(elem_height * scale)
                    center_x = elem_x + elem_width // 2
                    center_y = elem_y + elem_height // 2
                    transformed_x = center_x - scaled_width // 2 + int(offset_x * scale)
                    transformed_y = center_y - scaled_height // 2 + int(offset_y * scale)
                    
                    # Draw media content with transformations
                    painter.save()
                    
                    # Apply opacity
                    painter.setOpacity(opacity)
                    
                    # Apply rotation and scaling
                    if rotation != 0.0 or scale != 1.0:
                        painter.translate(center_x, center_y)
                        painter.rotate(rotation)
                        painter.scale(scale, scale)
                        painter.translate(-center_x, -center_y)
                    
                    # Adjusted rectangle for transformed content
                    elem_rect = QRect(transformed_x, transformed_y, scaled_width, scaled_height)
                    
                    # Video rendering
                    if element_type == "video":
                        # Check if video has playback error - render fallback
                        if element_props.get("_video_error", False):
                            # Render error placeholder or try to load as image
                            video_path = element_props.get("_video_path", "")
                            if video_path:
                                # Try to load as image (for formats that can be loaded as image)
                                pixmap = self._load_image(video_path)
                                if pixmap:
                                    scaled_pixmap = pixmap.scaled(
                                        scaled_width, scaled_height,
                                        Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation
                                    )
                                    pix_x = transformed_x + (scaled_width - scaled_pixmap.width()) // 2
                                    pix_y = transformed_y + (scaled_height - scaled_pixmap.height()) // 2
                                    painter.drawPixmap(pix_x, pix_y, scaled_pixmap)
                                else:
                                    # Draw placeholder rectangle
                                    painter.setPen(QPen(QColor(100, 100, 100), 1))
                                    painter.setBrush(QBrush(QColor(50, 50, 50)))
                                    painter.drawRect(elem_rect)
                                    painter.setPen(QPen(QColor(200, 200, 200)))
                                    painter.drawText(elem_rect, Qt.AlignCenter, "Video\nUnsupported Format")
                        # Otherwise video is rendered via QVideoWidget positioned as child widget
                    elif element_type in ["image", "picture", "photo"]:
                        # Render image
                        image_path = element_props.get("path", element.get("path", ""))
                        if image_path:
                            pixmap = self._load_image(image_path)
                            if pixmap:
                                scaled_pixmap = pixmap.scaled(
                                    scaled_width, scaled_height,
                                    Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation
                                )
                                # Center the image in the area
                                pix_x = transformed_x + (scaled_width - scaled_pixmap.width()) // 2
                                pix_y = transformed_y + (scaled_height - scaled_pixmap.height()) // 2
                                painter.drawPixmap(pix_x, pix_y, scaled_pixmap)
                    elif element_type in ["text", "singleline_text"]:
                        # Render text with animation support
                        text_content = element_props.get("text", element.get("text", element.get("name", "")))
                        if text_content:
                            # Apply typewriter effect if active
                            if "typewriter_progress" in anim_state:
                                chars_to_show = int(len(text_content) * anim_state["typewriter_progress"])
                                text_content = text_content[:chars_to_show]
                            
                            # Set text color
                            text_color = element_props.get("color", QColor(255, 255, 255))
                            if isinstance(text_color, str):
                                text_color = QColor(text_color)
                            elif isinstance(text_color, (list, tuple)) and len(text_color) >= 3:
                                text_color = QColor(text_color[0], text_color[1], text_color[2])
                            painter.setPen(QPen(text_color))
                            
                            # Set font
                            font_size = max(12, int(scaled_height * 0.3))
                            font = QFont("Arial", font_size)
                            painter.setFont(font)
                            
                            # Draw text
                            painter.drawText(elem_rect, Qt.AlignCenter | Qt.TextWordWrap, text_content)
                    elif element_type == "animation":
                        # Render animation (GIF or animated content)
                        anim_path = element_props.get("path", element.get("path", ""))
                        if anim_path:
                            # For GIFs, load first frame or use image loading
                            pixmap = self._load_image(anim_path)
                            if pixmap:
                                scaled_pixmap = pixmap.scaled(
                                    scaled_width, scaled_height,
                                    Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation
                                )
                                pix_x = transformed_x + (scaled_width - scaled_pixmap.width()) // 2
                                pix_y = transformed_y + (scaled_height - scaled_pixmap.height()) // 2
                                painter.drawPixmap(pix_x, pix_y, scaled_pixmap)
                    elif element_type == "clock":
                        # Render clock
                        now = datetime.now()
                        time_str = now.strftime("%H:%M:%S")
                        painter.setPen(QPen(QColor(255, 255, 255)))
                        font_size = max(20, int(scaled_height * 0.4))
                        font = QFont("Arial", font_size, QFont.Bold)
                        painter.setFont(font)
                        painter.drawText(elem_rect, Qt.AlignCenter, time_str)
                    elif element_type == "calendar":
                        # Render calendar
                        now = datetime.now()
                        date_str = now.strftime("%Y-%m-%d")
                        painter.setPen(QPen(QColor(255, 255, 255)))
                        font_size = max(16, int(scaled_height * 0.3))
                        font = QFont("Arial", font_size)
                        painter.setFont(font)
                        painter.drawText(elem_rect, Qt.AlignCenter, date_str)
                    
                    painter.restore()
                    
                    # Draw border on top of content
                    painter.setPen(QPen(border_color, border_width))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(elem_x, elem_y, elem_width, elem_height)
            
            painter.restore()

