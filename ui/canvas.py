"""
Main canvas/preview area with checkered background
"""
from typing import TYPE_CHECKING, Optional, Dict, Tuple, Any
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer, QUrl
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QMouseEvent, QPixmap, QImage
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from config.constants import CANVAS_CHECKER_SIZE
from core.program_manager import Program
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from config.constants import ContentType


class CanvasWidget(QWidget):
    """Inner canvas widget that draws the checkered background and content"""
    
    element_selected = pyqtSignal(str)  # Emits element ID when selected
    element_moved = pyqtSignal(str, int, int)  # Emits element ID, new x, new y
    element_changed = pyqtSignal(str)  # Emits element ID when element properties change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program: Program = None
        self.zoom_level = 100  # Percentage
        self.selected_element_id: Optional[str] = None
        self.selected_element_ids: set = set()  # Multi-selection support
        self.dragging = False
        self.resizing = False
        self.resize_handle: Optional[int] = None  # 0=TL, 1=TR, 2=BL, 3=BR
        self.drag_start_pos: Optional[QPoint] = None
        self.drag_element_start_pos: Optional[Tuple[int, int]] = None
        self.drag_element_start_size: Optional[Tuple[int, int]] = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Animation engine
        from media.animation_engine import AnimationEngine
        self.animation_engine = AnimationEngine()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(33)  # ~30 FPS
        
        # Video players for each video element
        self.video_players: Dict[str, QMediaPlayer] = {}
        self.video_widgets: Dict[str, QVideoWidget] = {}
        
        # Timer widgets for timing elements
        self.timer_widgets: Dict[str, Any] = {}
        # Weather widgets for weather elements
        self.weather_widgets: Dict[str, Any] = {}
        # Transition engine for element transitions
        from media.transition_engine import TransitionEngine
        self.transition_engine = TransitionEngine()
    
    def setup_video_player(self, element_id: str, file_path: str, x: int, y: int, width: int, height: int, properties: dict = None):
        """Setup video player for an element"""
        try:
            # Clean up existing player if any
            if element_id in self.video_players:
                self.video_players[element_id].stop()
                self.video_players[element_id].deleteLater()
            if element_id in self.video_widgets:
                self.video_widgets[element_id].deleteLater()
            
            # Create video widget
            video_widget = QVideoWidget(self)
            video_widget.setGeometry(0, 0, 0, 0)  # Will be positioned in paintEvent
            video_widget.hide()  # Hide initially, will show when positioned
            
            # Create media player
            audio_output = QAudioOutput()
            player = QMediaPlayer(self)
            player.setAudioOutput(audio_output)
            player.setVideoOutput(video_widget)
            player.setSource(QUrl.fromLocalFile(file_path))
            
            # Set loop if needed
            loop = properties.get("loop", False) if properties else False
            if loop:
                player.mediaStatusChanged.connect(
                    lambda status, p=player: p.play() if status == QMediaPlayer.MediaStatus.EndOfMedia else None
                )
            
            # Store element info for positioning
            video_widget.element_id = element_id
            video_widget.element_x = x
            video_widget.element_y = y
            video_widget.element_width = width
            video_widget.element_height = height
            
            self.video_players[element_id] = player
            self.video_widgets[element_id] = video_widget
            
            # Start playback
            player.play()
            
            # Update to show video widget
            self.update_video_widget_positions()
        except Exception as e:
            logger.exception(f"Error setting up video player for element {element_id}: {e}")
    
    def update_video_widget_positions(self):
        """Update positions of video widgets based on element positions and zoom"""
        if not self.program:
            return
        
        for element_id, video_widget in self.video_widgets.items():
            # Find element data
            element_data = None
            for elem in self.program.elements:
                if elem.get("id") == element_id:
                    element_data = elem
                    break
            
            if not element_data:
                video_widget.hide()
                continue
            
            # Get element position and size
            element_x = element_data.get("x", 0)
            element_y = element_data.get("y", 0)
            element_width = element_data.get("width", 640)
            element_height = element_data.get("height", 360)
            
            # Convert screen coordinates to canvas coordinates
            canvas_x, canvas_y = self.screen_to_canvas_coords(element_x, element_y)
            scale_x, scale_y, _, _ = self.get_screen_to_canvas_transform()
            
            canvas_width = element_width * scale_x
            canvas_height = element_height * scale_y
            
            # Position and show video widget
            video_widget.setGeometry(
                int(canvas_x), int(canvas_y),
                int(canvas_width), int(canvas_height)
            )
            video_widget.show()
            video_widget.raise_()
    
    def set_program(self, program: Program):
        """Set the current program"""
        # Clear existing animations
        self.animation_engine.clear_all()
        
        self.program = program
        self.selected_element_id = None
        # Setup video players for existing video elements
        if program:
            for element_data in program.elements:
                element_type = element_data.get("type", "")
                element_id = element_data.get("id", "")
                element_props = element_data.get("properties", {})
                
                # Setup video players
                if element_type == "video":
                    file_path = element_props.get("file_path", "")
                    if file_path:
                        element_x = element_data.get("x", 0)
                        element_y = element_data.get("y", 0)
                        element_width = element_data.get("width", 640)
                        element_height = element_data.get("height", 360)
                        self.setup_video_player(
                            element_id, file_path, element_x, element_y,
                            element_width, element_height, element_props
                        )
                
                # Setup animations for text elements
                if element_type in ["text", "single_line_text"]:
                    animation_type = element_props.get("animation", "None")
                    if animation_type and animation_type != "None":
                        from media.animation_engine import AnimationType
                        try:
                            anim_type_enum = AnimationType(animation_type.lower().replace(" ", "_"))
                            animation_speed = element_props.get("animation_speed", 1.0)
                            self.animation_engine.add_animation(
                                element_id, anim_type_enum,
                                duration=5.0, speed=animation_speed
                            )
                        except (ValueError, AttributeError):
                            pass
                    
                    # Setup scrolling for single line text
                    if element_type == "single_line_text":
                        direction = element_props.get("direction", "left")
                        speed = element_props.get("speed", 5)
                        from media.animation_engine import AnimationType
                        anim_type_map = {
                            "left": AnimationType.SCROLL_LEFT,
                            "right": AnimationType.SCROLL_RIGHT,
                            "up": AnimationType.SCROLL_UP,
                            "down": AnimationType.SCROLL_DOWN
                        }
                        anim_type = anim_type_map.get(direction, AnimationType.SCROLL_LEFT)
                        self.animation_engine.add_animation(
                            element_id, anim_type,
                            duration=10.0, speed=speed / 5.0
                        )
                
                # Setup timer widgets
                if element_type == "timing":
                    from core.timer_widget import TimerWidget
                    if element_id not in self.timer_widgets:
                        timer_widget = TimerWidget(element_props)
                        if element_props.get("auto_start", True):
                            timer_widget.start()
                        self.timer_widgets[element_id] = timer_widget
                
                # Setup transitions
                transition_in = element_props.get("transition_in", "none")
                transition_out = element_props.get("transition_out", "none")
                if transition_in != "none" or transition_out != "none":
                    self.transition_engine.add_transition(
                        element_id,
                        transition_in,
                        transition_out,
                        element_props.get("transition_duration_in", 1.0),
                        element_props.get("transition_duration_out", 1.0)
                    )
        self.update()
    
    def update_animations(self):
        """Update all animations and trigger canvas redraw"""
        if not self.program:
            return
        
        from datetime import datetime
        current_time = datetime.now().timestamp()
        
        # Update animations for all elements with animation properties
        for element_data in self.program.elements:
            element_id = element_data.get("id", "")
            element_props = element_data.get("properties", {})
            animation_type = element_props.get("animation", "None")
            
            if animation_type and animation_type != "None":
                # Setup animation if not already set
                from media.animation_engine import AnimationType, AnimationEngine
                try:
                    anim_type_enum = AnimationType(animation_type.lower().replace(" ", "_"))
                    animation_speed = element_props.get("animation_speed", 1.0)
                    
                    # Add animation if not already present
                    if element_id not in self.animation_engine.animations:
                        self.animation_engine.add_animation(
                            element_id, anim_type_enum,
                            duration=5.0, speed=animation_speed
                        )
                except (ValueError, AttributeError):
                    pass
        
        # Trigger canvas update for smooth animation
        self.update()
    
    def set_zoom(self, zoom_level: int):
        """Set zoom level"""
        self.zoom_level = zoom_level
        self.update()
    
    def set_selected_element(self, element_id: Optional[str]):
        """Set the selected element"""
        self.selected_element_id = element_id
        if element_id:
            self.selected_element_ids = {element_id}
        else:
            self.selected_element_ids.clear()
        self.update()
    
    def get_screen_to_canvas_transform(self) -> Tuple[float, float, float, float]:
        """Get transformation from screen coordinates to canvas coordinates"""
        rect = self.rect()
        screen_width = self.program.width if self.program else 1920
        screen_height = self.program.height if self.program else 1080
        
        canvas_width = rect.width() - 40
        canvas_height = rect.height() - 40
        
        screen_aspect = screen_width / screen_height
        canvas_aspect = canvas_width / canvas_height
        
        if screen_aspect > canvas_aspect:
            base_width = canvas_width
            base_height = canvas_width / screen_aspect
        else:
            base_height = canvas_height
            base_width = canvas_height * screen_aspect
        
        zoom_factor = self.zoom_level / 100.0
        scaled_width = base_width * zoom_factor
        scaled_height = base_height * zoom_factor
        
        scale_x = scaled_width / screen_width
        scale_y = scaled_height / screen_height
        
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        offset_x = center_x - scaled_width // 2
        offset_y = center_y - scaled_height // 2
        
        return scale_x, scale_y, offset_x, offset_y
    
    def canvas_to_screen_coords(self, canvas_x: int, canvas_y: int) -> Tuple[int, int]:
        """Convert canvas pixel coordinates to screen resolution coordinates"""
        scale_x, scale_y, offset_x, offset_y = self.get_screen_to_canvas_transform()
        
        screen_x = int((canvas_x - offset_x) / scale_x)
        screen_y = int((canvas_y - offset_y) / scale_y)
        
        return screen_x, screen_y
    
    def screen_to_canvas_coords(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen resolution coordinates to canvas pixel coordinates"""
        scale_x, scale_y, offset_x, offset_y = self.get_screen_to_canvas_transform()
        
        canvas_x = offset_x + (screen_x * scale_x)
        canvas_y = offset_y + (screen_y * scale_y)
        
        return canvas_x, canvas_y
    
    def get_element_at_position(self, x: int, y: int) -> Optional[Dict]:
        """Get element at canvas position"""
        if not self.program or not self.program.elements:
            return None
        
        scale_x, scale_y, offset_x, offset_y = self.get_screen_to_canvas_transform()
        
        # Convert canvas coordinates to screen coordinates
        screen_x, screen_y = self.canvas_to_screen_coords(x, y)
        
        # Check elements in reverse order (top to bottom)
        for element_data in reversed(self.program.elements):
            element_x = element_data.get("x", 0)
            element_y = element_data.get("y", 0)
            element_width = element_data.get("width", 200)
            element_height = element_data.get("height", 100)
            
            if (element_x <= screen_x <= element_x + element_width and
                element_y <= screen_y <= element_y + element_height):
                return element_data
        
        return None
    
    def get_resize_handle_at_position(self, x: int, y: int, element_data: Dict) -> Optional[int]:
        """Get resize handle at position (0=TL, 1=TR, 2=BL, 3=BR)"""
        if not element_data:
            return None
        
        scale_x, scale_y, offset_x, offset_y = self.get_screen_to_canvas_transform()
        element_x = element_data.get("x", 0)
        element_y = element_data.get("y", 0)
        element_width = element_data.get("width", 200)
        element_height = element_data.get("height", 100)
        
        # Convert element corners to canvas coordinates
        corners = [
            (offset_x + element_x * scale_x, offset_y + element_y * scale_y),  # TL
            (offset_x + (element_x + element_width) * scale_x, offset_y + element_y * scale_y),  # TR
            (offset_x + element_x * scale_x, offset_y + (element_y + element_height) * scale_y),  # BL
            (offset_x + (element_x + element_width) * scale_x, offset_y + (element_y + element_height) * scale_y),  # BR
        ]
        
        handle_size = 8
        for i, (cx, cy) in enumerate(corners):
            if abs(x - cx) <= handle_size and abs(y - cy) <= handle_size:
                return i
        
        return None
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for element selection and dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on resize handle first
            if self.selected_element_id:
                for elem in self.program.elements if self.program else []:
                    if elem.get("id") == self.selected_element_id:
                        handle = self.get_resize_handle_at_position(event.x(), event.y(), elem)
                        if handle is not None:
                            self.resizing = True
                            self.resize_handle = handle
                            self.drag_start_pos = event.pos()
                            self.drag_element_start_pos = (elem.get("x", 0), elem.get("y", 0))
                            self.drag_element_start_size = (elem.get("width", 200), elem.get("height", 100))
                            return
            
            element = self.get_element_at_position(event.x(), event.y())
            
            if element:
                element_id = element.get("id")
                # Multi-selection with Ctrl
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    if element_id in self.selected_element_ids:
                        self.selected_element_ids.remove(element_id)
                        if self.selected_element_id == element_id:
                            self.selected_element_id = list(self.selected_element_ids)[0] if self.selected_element_ids else None
                    else:
                        self.selected_element_ids.add(element_id)
                        self.selected_element_id = element_id
                else:
                    self.selected_element_id = element_id
                    self.selected_element_ids = {element_id}
                
                self.dragging = True
                self.drag_start_pos = event.pos()
                element_x = element.get("x", 0)
                element_y = element.get("y", 0)
                self.drag_element_start_pos = (element_x, element_y)
                self.element_selected.emit(self.selected_element_id)
            else:
                if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    self.selected_element_id = None
                    self.selected_element_ids.clear()
                    self.element_selected.emit("")
            
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            # Context menu
            element = self.get_element_at_position(event.x(), event.y())
            if element:
                self.show_element_context_menu(event.globalPos(), element)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging elements and resizing"""
        if self.resizing and self.selected_element_id and self.drag_start_pos and self.resize_handle is not None:
            if not self.program or not self.program.elements:
                return
            
            scale_x, scale_y, _, _ = self.get_screen_to_canvas_transform()
            delta_x = (event.x() - self.drag_start_pos.x()) / scale_x
            delta_y = (event.y() - self.drag_start_pos.y()) / scale_y
            
            for element_data in self.program.elements:
                if element_data.get("id") == self.selected_element_id:
                    start_x, start_y = self.drag_element_start_pos
                    start_w, start_h = self.drag_element_start_size
                    
                    # Handle resize based on corner
                    if self.resize_handle == 0:  # Top-left
                        new_x = start_x + delta_x
                        new_y = start_y + delta_y
                        new_w = start_w - delta_x
                        new_h = start_h - delta_y
                    elif self.resize_handle == 1:  # Top-right
                        new_x = start_x
                        new_y = start_y + delta_y
                        new_w = start_w + delta_x
                        new_h = start_h - delta_y
                    elif self.resize_handle == 2:  # Bottom-left
                        new_x = start_x + delta_x
                        new_y = start_y
                        new_w = start_w - delta_x
                        new_h = start_h + delta_y
                    else:  # Bottom-right
                        new_x = start_x
                        new_y = start_y
                        new_w = start_w + delta_x
                        new_h = start_h + delta_y
                    
                    # Ensure minimum size
                    new_w = max(10, new_w)
                    new_h = max(10, new_h)
                    
                    # Snap to grid if enabled
                    if settings.get("canvas.snap_to_grid", False):
                        grid_size = settings.get("canvas.grid_size", 10)
                        new_x = round(new_x / grid_size) * grid_size
                        new_y = round(new_y / grid_size) * grid_size
                        new_w = round(new_w / grid_size) * grid_size
                        new_h = round(new_h / grid_size) * grid_size
                    
                    element_data["x"] = max(0, new_x)
                    element_data["y"] = max(0, new_y)
                    element_data["width"] = new_w
                    element_data["height"] = new_h
                    
                    self.update()
                    break
        elif self.dragging and self.selected_element_id and self.drag_start_pos:
            if not self.program or not self.program.elements:
                return
            
            # Calculate drag delta in screen coordinates
            delta_x = event.x() - self.drag_start_pos.x()
            delta_y = event.y() - self.drag_start_pos.y()
            
            scale_x, scale_y, _, _ = self.get_screen_to_canvas_transform()
            
            # Convert canvas delta to screen delta
            screen_delta_x = int(delta_x / scale_x)
            screen_delta_y = int(delta_y / scale_y)
            
            # Move all selected elements
            for element_data in self.program.elements:
                if element_data.get("id") in self.selected_element_ids:
                    # Get original position for this element
                    if element_data.get("id") == self.selected_element_id:
                        orig_x = self.drag_element_start_pos[0]
                        orig_y = self.drag_element_start_pos[1]
                    else:
                        # For multi-selection, calculate relative offset
                        orig_x = element_data.get("x", 0)
                        orig_y = element_data.get("y", 0)
                    
                    new_x = orig_x + screen_delta_x
                    new_y = orig_y + screen_delta_y
                    
                    # Snap to grid if enabled
                    if settings.get("canvas.snap_to_grid", False):
                        grid_size = settings.get("canvas.grid_size", 10)
                        new_x = round(new_x / grid_size) * grid_size
                        new_y = round(new_y / grid_size) * grid_size
                    
                    element_data["x"] = max(0, new_x)
                    element_data["y"] = max(0, new_y)
            
            if self.selected_element_id:
                for elem in self.program.elements:
                    if elem.get("id") == self.selected_element_id:
                        self.element_moved.emit(self.selected_element_id, elem["x"], elem["y"])
                        break
            
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Emit element_changed signal if we were resizing
            if self.resizing and self.selected_element_id:
                self.element_changed.emit(self.selected_element_id)
            
            self.dragging = False
            self.resizing = False
            self.resize_handle = None
            self.drag_start_pos = None
            self.drag_element_start_pos = None
            self.drag_element_start_size = None
    
    def show_element_context_menu(self, pos, element_data: Dict):
        """Show context menu for element"""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(lambda: self.copy_element(element_data))
        
        duplicate_action = menu.addAction("Duplicate")
        duplicate_action.triggered.connect(lambda: self.duplicate_element(element_data))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_element(element_data))
        
        menu.addSeparator()
        
        bring_to_front_action = menu.addAction("Bring to Front")
        bring_to_front_action.triggered.connect(lambda: self.bring_to_front(element_data))
        
        send_to_back_action = menu.addAction("Send to Back")
        send_to_back_action.triggered.connect(lambda: self.send_to_back(element_data))
        
        menu.exec(pos)
    
    def copy_element(self, element_data: Dict):
        """Copy element to clipboard"""
        # Emit signal to main window
        self.parent().parent().copy_selected_element() if hasattr(self.parent().parent(), 'copy_selected_element') else None
    
    def duplicate_element(self, element_data: Dict):
        """Duplicate element"""
        if not self.program:
            return
        
        from copy import deepcopy
        from datetime import datetime
        new_element = deepcopy(element_data)
        new_element["id"] = f"element_{datetime.now().timestamp()}_{id(new_element)}"
        new_element["x"] = new_element.get("x", 0) + 20
        new_element["y"] = new_element.get("y", 0) + 20
        
        self.program.elements.append(new_element)
        self.selected_element_id = new_element["id"]
        self.selected_element_ids = {new_element["id"]}
        self.element_selected.emit(new_element["id"])
        self.update()
    
    def delete_element(self, element_data: Dict):
        """Delete element"""
        if not self.program:
            return
        
        element_id = element_data.get("id")
        self.program.elements = [e for e in self.program.elements if e.get("id") != element_id]
        if element_id in self.selected_element_ids:
            self.selected_element_ids.remove(element_id)
        if self.selected_element_id == element_id:
            self.selected_element_id = list(self.selected_element_ids)[0] if self.selected_element_ids else None
        self.element_selected.emit(self.selected_element_id or "")
        self.update()
    
    def bring_to_front(self, element_data: Dict):
        """Bring element to front"""
        if not self.program:
            return
        
        element_id = element_data.get("id")
        elements = self.program.elements
        for i, elem in enumerate(elements):
            if elem.get("id") == element_id:
                elements.append(elements.pop(i))
                self.update()
                break
    
    def send_to_back(self, element_data: Dict):
        """Send element to back"""
        if not self.program:
            return
        
        element_id = element_data.get("id")
        elements = self.program.elements
        for i, elem in enumerate(elements):
            if elem.get("id") == element_id:
                elements.insert(0, elements.pop(i))
                self.update()
                break
    
    def paintEvent(self, event):
        """Paint the canvas with checkered background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Update video widget positions before drawing
        self.update_video_widget_positions()
        
        # Draw checkered background
        self.draw_checkered_background(painter)
        
        # Draw program content if available
        self.draw_program_content(painter)
    
    def draw_checkered_background(self, painter: QPainter):
        """Draw checkered pattern background"""
        rect = self.rect()
        
        # Light gray and white squares
        light_gray = QColor(240, 240, 240)
        white = QColor(255, 255, 255)
        
        size = CANVAS_CHECKER_SIZE
        for y in range(0, rect.height(), size):
            for x in range(0, rect.width(), size):
                color = light_gray if ((x // size) + (y // size)) % 2 == 0 else white
                painter.fillRect(x, y, size, size, QBrush(color))
        
        # Draw grid if enabled
        if settings.get("canvas.grid_enabled", False):
            self.draw_grid(painter, rect)
    
    def draw_grid(self, painter: QPainter, rect):
        """Draw grid overlay"""
        grid_size = settings.get("canvas.grid_size", 10)
        grid_color = QColor(200, 200, 200, 100)  # Semi-transparent gray
        pen = QPen(grid_color, 1)
        painter.setPen(pen)
        
        # Draw vertical lines
        for x in range(0, rect.width(), grid_size):
            painter.drawLine(x, 0, x, rect.height())
        
        # Draw horizontal lines
        for y in range(0, rect.height(), grid_size):
            painter.drawLine(0, y, rect.width(), y)
    
    def draw_program_content(self, painter: QPainter):
        """Draw program content"""
        rect = self.rect()
        
        # Get screen resolution from program (default to 1920x1080 if not set)
        screen_width = self.program.width if self.program else 1920
        screen_height = self.program.height if self.program else 1080
        
        # Calculate scaling factor to fit screen resolution to canvas
        canvas_width = rect.width() - 40
        canvas_height = rect.height() - 40
        
        # Calculate aspect ratios
        screen_aspect = screen_width / screen_height
        canvas_aspect = canvas_width / canvas_height
        
        # Calculate scale to fit canvas while maintaining aspect ratio
        if screen_aspect > canvas_aspect:
            # Screen is wider - fit to width
            base_width = canvas_width
            base_height = canvas_width / screen_aspect
        else:
            # Screen is taller - fit to height
            base_height = canvas_height
            base_width = canvas_height * screen_aspect
        
        # Apply zoom transformation
        zoom_factor = self.zoom_level / 100.0
        scaled_width = base_width * zoom_factor
        scaled_height = base_height * zoom_factor
        
        # Calculate scale factor for element positions
        scale_x = scaled_width / screen_width
        scale_y = scaled_height / screen_height
        
        # Calculate offset to center the screen rectangle
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        offset_x = center_x - scaled_width // 2
        offset_y = center_y - scaled_height // 2
        
        # Draw frame if enabled
        if self.program and self.program.properties.get("frame", {}).get("enabled", False):
            self.draw_frame(painter, offset_x, offset_y, scaled_width, scaled_height)
        else:
            # Draw screen boundary rectangle
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
            painter.drawRect(int(offset_x), int(offset_y), int(scaled_width), int(scaled_height))
        
        # Draw program elements if they exist
        if self.program and self.program.elements:
            from config.constants import ContentType
            
            # Calculate scale factors for elements
            scale_x = scaled_width / screen_width
            scale_y = scaled_height / screen_height
            
            for element_data in self.program.elements:
                element_id = element_data.get("id", "")
                element_type = element_data.get("type", "")
                element_x = element_data.get("x", 0)
                element_y = element_data.get("y", 0)
                element_width = element_data.get("width", 200)
                element_height = element_data.get("height", 100)
                element_props = element_data.get("properties", {})
                
                # Scale and translate element position
                scaled_x = offset_x + (element_x * scale_x)
                scaled_y = offset_y + (element_y * scale_y)
                scaled_w = element_width * scale_x
                scaled_h = element_height * scale_y
                
                # Draw element based on type
                try:
                    content_type = ContentType(element_type)
                    # Add element ID to properties for animation/video
                    element_props_with_id = element_props.copy()
                    element_props_with_id["id"] = element_id
                    self.draw_element(painter, content_type, scaled_x, scaled_y, 
                                     scaled_w, scaled_h, element_props_with_id)
                    
                    # Draw selection highlight if selected
                    if element_id in self.selected_element_ids:
                        # Draw selection border
                        border_color = QColor(33, 150, 243) if element_id == self.selected_element_id else QColor(100, 150, 243)
                        painter.setPen(QPen(border_color, 2, Qt.PenStyle.DashLine))
                        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent
                        painter.drawRect(int(scaled_x) - 1, int(scaled_y) - 1, 
                                        int(scaled_w) + 2, int(scaled_h) + 2)
                        
                        # Draw resize handles only for primary selected element
                        if element_id == self.selected_element_id:
                            handle_size = 8
                            handle_color = QColor(33, 150, 243)
                            painter.setPen(QPen(handle_color, 1))
                            painter.setBrush(QBrush(handle_color))
                            
                            # Corner handles
                            corners = [
                                (scaled_x, scaled_y),  # Top-left
                                (scaled_x + scaled_w, scaled_y),  # Top-right
                                (scaled_x, scaled_y + scaled_h),  # Bottom-left
                                (scaled_x + scaled_w, scaled_y + scaled_h),  # Bottom-right
                            ]
                            
                            for corner_x, corner_y in corners:
                                painter.drawRect(int(corner_x - handle_size/2), 
                                               int(corner_y - handle_size/2),
                                               handle_size, handle_size)
                        
                except ValueError:
                    # Unknown type, draw as rectangle
                    painter.setPen(QPen(QColor(100, 100, 100), 1))
                    painter.setBrush(QBrush(QColor(200, 200, 200, 100)))
                    painter.drawRect(int(scaled_x), int(scaled_y), int(scaled_w), int(scaled_h))
        else:
            # Draw placeholder if no content
            pass
    
    def draw_frame(self, painter: QPainter, x: float, y: float, width: float, height: float):
        """Draw frame border using resources"""
        if not self.program:
            return
        
        frame_id = self.program.properties.get("frame", {}).get("id", 0)
        from core.resource_manager import resource_manager
        frame_pixmap = resource_manager.get_frame_image(frame_id)
        if frame_pixmap:
            # Scale and draw frame
            scaled_frame = frame_pixmap.scaled(
                int(width), int(height),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(int(x), int(y), scaled_frame)
        else:
            # Fallback to simple border
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
            painter.drawRect(int(x), int(y), int(width), int(height))
    
    def draw_element(self, painter: QPainter, content_type: 'ContentType', 
                    x: float, y: float, width: float, height: float, 
                    properties: dict):
        """Draw a specific content element"""
        from config.constants import ContentType
        
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        
        if content_type == ContentType.TEXT:
            # Draw text element with animations
            element_id = properties.get("id", "")
            text = properties.get("text", "Text")
            font_size = properties.get("font_size", 24)
            color = QColor(properties.get("color", "#000000"))
            animation_type = properties.get("animation", "None")
            
            # Get animation state if applicable
            opacity = 1.0
            offset_x = 0
            offset_y = 0
            
            if animation_type and animation_type != "None" and element_id:
                from datetime import datetime
                current_time = datetime.now().timestamp()
                anim_state = self.animation_engine.update_animation(element_id, current_time)
                
                opacity = anim_state.get("opacity", 1.0)
                offset_x = anim_state.get("offset_x", 0)
                offset_y = anim_state.get("offset_y", 0)
                
                # Handle typewriter effect
                if "typewriter_progress" in anim_state:
                    chars_to_show = int(len(text) * anim_state["typewriter_progress"])
                    text = text[:chars_to_show]
            
            # Text effects
            has_shadow = properties.get("text_shadow", False)
            shadow_color = QColor(properties.get("shadow_color", "#000000"))
            shadow_offset_x = properties.get("shadow_offset_x", 2)
            shadow_offset_y = properties.get("shadow_offset_y", 2)
            shadow_blur = properties.get("shadow_blur", 0)
            
            has_outline = properties.get("text_outline", False)
            outline_color = QColor(properties.get("outline_color", "#000000"))
            outline_width = properties.get("outline_width", 2)
            
            has_gradient = properties.get("text_gradient", False)
            gradient_color1 = QColor(properties.get("gradient_color1", "#000000"))
            gradient_color2 = QColor(properties.get("gradient_color2", "#FFFFFF"))
            gradient_direction = properties.get("gradient_direction", "horizontal")
            
            # Apply opacity
            color.setAlphaF(opacity)
            shadow_color.setAlphaF(opacity * 0.7)
            outline_color.setAlphaF(opacity)
            gradient_color1.setAlphaF(opacity)
            gradient_color2.setAlphaF(opacity)
            
            font = painter.font()
            font.setPixelSize(int(font_size * (width / 200)))
            painter.setFont(font)
            
            # Calculate text bounding rect
            text_rect = painter.fontMetrics().boundingRect(
                int(x), int(y), int(width), int(height),
                Qt.AlignmentFlag.AlignCenter, text
            )
            
            # Draw text with effects
            def draw_text_with_effects(painter, text, rect, base_x, base_y):
                """Helper to draw text with all effects"""
                # Draw shadow first (if enabled)
                if has_shadow:
                    shadow_rect = rect.translated(shadow_offset_x, shadow_offset_y)
                    painter.setPen(QPen(shadow_color, 1))
                    if shadow_blur > 0:
                        for i in range(shadow_blur):
                            offset = i * 0.5
                            painter.drawText(
                                shadow_rect.adjusted(int(offset), int(offset), int(offset), int(offset)),
                                Qt.AlignmentFlag.AlignCenter, text
                            )
                    else:
                        painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignCenter, text)
                
                # Draw outline (if enabled)
                if has_outline:
                    painter.setPen(QPen(outline_color, outline_width))
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                outline_rect = rect.translated(dx * outline_width, dy * outline_width)
                                painter.drawText(outline_rect, Qt.AlignmentFlag.AlignCenter, text)
                
                # Draw main text with gradient or solid color
                if has_gradient:
                    from PyQt6.QtGui import QLinearGradient
                    if gradient_direction == "horizontal":
                        gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
                    else:
                        gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
                    gradient.setColorAt(0, gradient_color1)
                    gradient.setColorAt(1, gradient_color2)
                    painter.setPen(QPen(gradient, 1))
                else:
                    painter.setPen(QPen(color, 1))
                
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            
            # For scrolling text, handle clipping
            if offset_x != 0 or offset_y != 0:
                painter.save()
                painter.setClipRect(int(x), int(y), int(width), int(height))
                adjusted_rect = text_rect.translated(int(offset_x), int(offset_y))
                draw_text_with_effects(painter, text, adjusted_rect, int(x + offset_x), int(y + offset_y))
                painter.restore()
            else:
                draw_text_with_effects(painter, text, text_rect, int(x), int(y))
        
        elif content_type == ContentType.SINGLE_LINE_TEXT:
            # Draw single line text with scrolling animation
            element_id = properties.get("id", "")
            text = properties.get("text", "Scrolling Text")
            color = QColor(properties.get("color", "#000000"))
            direction = properties.get("direction", "left")
            speed = properties.get("speed", 5)
            
            # Setup scrolling animation based on direction
            if element_id:
                from datetime import datetime
                from media.animation_engine import AnimationType
                current_time = datetime.now().timestamp()
                
                # Map direction to animation type
                anim_type_map = {
                    "left": AnimationType.SCROLL_LEFT,
                    "right": AnimationType.SCROLL_RIGHT,
                    "up": AnimationType.SCROLL_UP,
                    "down": AnimationType.SCROLL_DOWN
                }
                
                anim_type = anim_type_map.get(direction, AnimationType.SCROLL_LEFT)
                
                # Setup animation if not already set
                if element_id not in self.animation_engine.animations:
                    self.animation_engine.add_animation(
                        element_id, anim_type,
                        duration=10.0, speed=speed / 5.0  # Normalize speed
                    )
                
                # Get animation state
                anim_state = self.animation_engine.update_animation(element_id, current_time)
                offset_x = anim_state.get("offset_x", 0)
                offset_y = anim_state.get("offset_y", 0)
            else:
                offset_x = 0
                offset_y = 0
            
            painter.setPen(QPen(color, 1))
            font = painter.font()
            font.setPixelSize(int(24 * (width / 200)))
            painter.setFont(font)
            
            # Draw scrolling text with clipping
            painter.save()
            painter.setClipRect(int(x), int(y), int(width), int(height))
            # For scrolling, we need to draw text multiple times to create seamless loop
            text_width = painter.fontMetrics().horizontalAdvance(text)
            if text_width > 0:
                # Calculate how many times to repeat text for seamless scrolling
                repeats = max(2, int((width + abs(offset_x)) / text_width) + 1) if offset_x != 0 else 1
                for i in range(repeats):
                    text_x = int(x + offset_x + (i * text_width))
                    if text_x + text_width >= x and text_x <= x + width:
                        painter.drawText(text_x, int(y), int(width), int(height),
                                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            else:
                painter.drawText(int(x + offset_x), int(y + offset_y), int(width), int(height),
                               Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            painter.restore()
        
        elif content_type == ContentType.VIDEO:
            # Check if video player exists for this element
            element_id = properties.get("id", "")
            file_path = properties.get("file_path", "")
            
            if element_id in self.video_widgets and file_path:
                # Video widget will be positioned by update_video_widget_positions
                # Just draw a border to show the video area
                painter.setPen(QPen(QColor(100, 100, 100), 1))
                painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent
                painter.drawRect(int(x), int(y), int(width), int(height))
            else:
                # Draw video placeholder
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                painter.drawRect(int(x), int(y), int(width), int(height))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                # Draw play icon
                center_x = x + width / 2
                center_y = y + height / 2
                icon_size = min(width, height) / 4
                painter.drawText(int(center_x - icon_size/2), int(center_y - icon_size/2),
                               int(icon_size), int(icon_size),
                               Qt.AlignmentFlag.AlignCenter, "▶")
        
        elif content_type == ContentType.PHOTO:
            # Draw photo - load and display image if file path exists
            file_path = properties.get("file_path", "")
            if file_path:
                try:
                    from pathlib import Path
                    if Path(file_path).exists():
                        pixmap = QPixmap(file_path)
                        if not pixmap.isNull():
                            # Apply image effects
                            brightness = properties.get("brightness", 0)
                            contrast = properties.get("contrast", 0)
                            saturation = properties.get("saturation", 0)
                            filter_type = properties.get("filter", "none")
                            
                            if brightness != 0 or contrast != 0 or saturation != 0 or filter_type != "none":
                                from core.image_effects import ImageEffects
                                if brightness != 0 or contrast != 0:
                                    pixmap = ImageEffects.apply_brightness_contrast(pixmap, brightness, contrast)
                                if saturation != 0:
                                    pixmap = ImageEffects.apply_saturation(pixmap, saturation)
                                if filter_type != "none":
                                    pixmap = ImageEffects.apply_filter(pixmap, filter_type)
                            
                            # Scale pixmap to fit element size while maintaining aspect ratio
                            scaled_pixmap = pixmap.scaled(
                                int(width), int(height),
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            # Center the image
                            img_x = x + (width - scaled_pixmap.width()) / 2
                            img_y = y + (height - scaled_pixmap.height()) / 2
                            painter.drawPixmap(int(img_x), int(img_y), scaled_pixmap)
                        else:
                            # Invalid image file
                            self.draw_photo_placeholder(painter, x, y, width, height)
                    else:
                        # File not found
                        self.draw_photo_placeholder(painter, x, y, width, height)
                except Exception as e:
                    # Error loading image
                    self.draw_photo_placeholder(painter, x, y, width, height)
            else:
                # No file path
                self.draw_photo_placeholder(painter, x, y, width, height)
    
    def draw_photo_placeholder(self, painter: QPainter, x: float, y: float, width: float, height: float):
        """Draw photo placeholder"""
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawRect(int(x), int(y), int(width), int(height))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawText(int(x), int(y), int(width), int(height),
                       Qt.AlignmentFlag.AlignCenter, "📷")
    
    def draw_element(self, painter: QPainter, content_type: 'ContentType', 
                    x: float, y: float, width: float, height: float, 
                    properties: dict):
        """Draw a specific content element"""
        from config.constants import ContentType
        
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        
        if content_type == ContentType.TEXT:
            # Draw text element with animations
            element_id = properties.get("id", "")
            text = properties.get("text", "Text")
            font_size = properties.get("font_size", 24)
            color = QColor(properties.get("color", "#000000"))
            animation_type = properties.get("animation", "None")
            
            # Get animation state if applicable
            opacity = 1.0
            offset_x = 0
            offset_y = 0
            
            if animation_type and animation_type != "None" and element_id:
                from datetime import datetime
                current_time = datetime.now().timestamp()
                anim_state = self.animation_engine.update_animation(element_id, current_time)
                
                opacity = anim_state.get("opacity", 1.0)
                offset_x = anim_state.get("offset_x", 0)
                offset_y = anim_state.get("offset_y", 0)
                
                # Handle typewriter effect
                if "typewriter_progress" in anim_state:
                    chars_to_show = int(len(text) * anim_state["typewriter_progress"])
                    text = text[:chars_to_show]
            
            # Text effects
            has_shadow = properties.get("text_shadow", False)
            shadow_color = QColor(properties.get("shadow_color", "#000000"))
            shadow_offset_x = properties.get("shadow_offset_x", 2)
            shadow_offset_y = properties.get("shadow_offset_y", 2)
            shadow_blur = properties.get("shadow_blur", 0)
            
            has_outline = properties.get("text_outline", False)
            outline_color = QColor(properties.get("outline_color", "#000000"))
            outline_width = properties.get("outline_width", 2)
            
            has_gradient = properties.get("text_gradient", False)
            gradient_color1 = QColor(properties.get("gradient_color1", "#000000"))
            gradient_color2 = QColor(properties.get("gradient_color2", "#FFFFFF"))
            gradient_direction = properties.get("gradient_direction", "horizontal")
            
            # Apply opacity
            color.setAlphaF(opacity)
            shadow_color.setAlphaF(opacity * 0.7)
            outline_color.setAlphaF(opacity)
            gradient_color1.setAlphaF(opacity)
            gradient_color2.setAlphaF(opacity)
            
            font = painter.font()
            font.setPixelSize(int(font_size * (width / 200)))
            painter.setFont(font)
            
            # Calculate text bounding rect
            text_rect = painter.fontMetrics().boundingRect(
                int(x), int(y), int(width), int(height),
                Qt.AlignmentFlag.AlignCenter, text
            )
            
            # Draw text with effects
            def draw_text_with_effects(painter, text, rect, base_x, base_y):
                """Helper to draw text with all effects"""
                # Draw shadow first (if enabled)
                if has_shadow:
                    shadow_rect = rect.translated(shadow_offset_x, shadow_offset_y)
                    painter.setPen(QPen(shadow_color, 1))
                    if shadow_blur > 0:
                        for i in range(shadow_blur):
                            offset = i * 0.5
                            painter.drawText(
                                shadow_rect.adjusted(int(offset), int(offset), int(offset), int(offset)),
                                Qt.AlignmentFlag.AlignCenter, text
                            )
                    else:
                        painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignCenter, text)
                
                # Draw outline (if enabled)
                if has_outline:
                    painter.setPen(QPen(outline_color, outline_width))
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                outline_rect = rect.translated(dx * outline_width, dy * outline_width)
                                painter.drawText(outline_rect, Qt.AlignmentFlag.AlignCenter, text)
                
                # Draw main text with gradient or solid color
                if has_gradient:
                    from PyQt6.QtGui import QLinearGradient
                    if gradient_direction == "horizontal":
                        gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
                    else:
                        gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
                    gradient.setColorAt(0, gradient_color1)
                    gradient.setColorAt(1, gradient_color2)
                    painter.setPen(QPen(gradient, 1))
                else:
                    painter.setPen(QPen(color, 1))
                
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            
            # For scrolling text, handle clipping
            if offset_x != 0 or offset_y != 0:
                painter.save()
                painter.setClipRect(int(x), int(y), int(width), int(height))
                adjusted_rect = text_rect.translated(int(offset_x), int(offset_y))
                draw_text_with_effects(painter, text, adjusted_rect, int(x + offset_x), int(y + offset_y))
                painter.restore()
            else:
                draw_text_with_effects(painter, text, text_rect, int(x), int(y))
        
        elif content_type == ContentType.SINGLE_LINE_TEXT:
            # Draw single line text with scrolling animation
            element_id = properties.get("id", "")
            text = properties.get("text", "Scrolling Text")
            color = QColor(properties.get("color", "#000000"))
            direction = properties.get("direction", "left")
            speed = properties.get("speed", 5)
            
            # Setup scrolling animation based on direction
            if element_id:
                from datetime import datetime
                from media.animation_engine import AnimationType
                current_time = datetime.now().timestamp()
                
                # Map direction to animation type
                anim_type_map = {
                    "left": AnimationType.SCROLL_LEFT,
                    "right": AnimationType.SCROLL_RIGHT,
                    "up": AnimationType.SCROLL_UP,
                    "down": AnimationType.SCROLL_DOWN
                }
                
                anim_type = anim_type_map.get(direction, AnimationType.SCROLL_LEFT)
                
                # Setup animation if not already set
                if element_id not in self.animation_engine.animations:
                    self.animation_engine.add_animation(
                        element_id, anim_type,
                        duration=10.0, speed=speed / 5.0  # Normalize speed
                    )
                
                # Get animation state
                anim_state = self.animation_engine.update_animation(element_id, current_time)
                offset_x = anim_state.get("offset_x", 0)
                offset_y = anim_state.get("offset_y", 0)
            else:
                offset_x = 0
                offset_y = 0
            
            painter.setPen(QPen(color, 1))
            font = painter.font()
            font.setPixelSize(int(24 * (width / 200)))
            painter.setFont(font)
            
            # Draw scrolling text with clipping
            painter.save()
            painter.setClipRect(int(x), int(y), int(width), int(height))
            # For scrolling, we need to draw text multiple times to create seamless loop
            text_width = painter.fontMetrics().horizontalAdvance(text)
            if text_width > 0:
                # Calculate how many times to repeat text for seamless scrolling
                repeats = max(2, int((width + abs(offset_x)) / text_width) + 1) if offset_x != 0 else 1
                for i in range(repeats):
                    text_x = int(x + offset_x + (i * text_width))
                    if text_x + text_width >= x and text_x <= x + width:
                        painter.drawText(text_x, int(y), int(width), int(height),
                                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            else:
                painter.drawText(int(x + offset_x), int(y + offset_y), int(width), int(height),
                               Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            painter.restore()
        
        elif content_type == ContentType.VIDEO:
            # Check if video player exists for this element
            element_id = properties.get("id", "")
            file_path = properties.get("file_path", "")
            
            if element_id in self.video_widgets and file_path:
                # Video widget will be positioned by update_video_widget_positions
                # Just draw a border to show the video area
                painter.setPen(QPen(QColor(100, 100, 100), 1))
                painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent
                painter.drawRect(int(x), int(y), int(width), int(height))
            else:
                # Draw video placeholder
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                painter.drawRect(int(x), int(y), int(width), int(height))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                # Draw play icon
                center_x = x + width / 2
                center_y = y + height / 2
                icon_size = min(width, height) / 4
                painter.drawText(int(center_x - icon_size/2), int(center_y - icon_size/2),
                               int(icon_size), int(icon_size),
                               Qt.AlignmentFlag.AlignCenter, "▶")
        
        elif content_type == ContentType.PHOTO:
            # Draw photo - load and display image if file path exists
            file_path = properties.get("file_path", "")
            if file_path:
                try:
                    from pathlib import Path
                    if Path(file_path).exists():
                        pixmap = QPixmap(file_path)
                        if not pixmap.isNull():
                            # Apply image effects
                            brightness = properties.get("brightness", 0)
                            contrast = properties.get("contrast", 0)
                            saturation = properties.get("saturation", 0)
                            filter_type = properties.get("filter", "none")
                            
                            if brightness != 0 or contrast != 0 or saturation != 0 or filter_type != "none":
                                from core.image_effects import ImageEffects
                                if brightness != 0 or contrast != 0:
                                    pixmap = ImageEffects.apply_brightness_contrast(pixmap, brightness, contrast)
                                if saturation != 0:
                                    pixmap = ImageEffects.apply_saturation(pixmap, saturation)
                                if filter_type != "none":
                                    pixmap = ImageEffects.apply_filter(pixmap, filter_type)
                            
                            # Scale pixmap to fit element size while maintaining aspect ratio
                            scaled_pixmap = pixmap.scaled(
                                int(width), int(height),
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            # Center the image
                            img_x = x + (width - scaled_pixmap.width()) / 2
                            img_y = y + (height - scaled_pixmap.height()) / 2
                            painter.drawPixmap(int(img_x), int(img_y), scaled_pixmap)
                        else:
                            # Invalid image file
                            self.draw_photo_placeholder(painter, x, y, width, height)
                    else:
                        # File not found
                        self.draw_photo_placeholder(painter, x, y, width, height)
                except Exception as e:
                    # Error loading image
                    self.draw_photo_placeholder(painter, x, y, width, height)
            else:
                # No file path
                self.draw_photo_placeholder(painter, x, y, width, height)
        
        elif content_type == ContentType.CLOCK:
            # Draw clock
            from datetime import datetime
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            color = QColor(properties.get("color", "#000000"))
            
            painter.setPen(QPen(color, 1))
            font = painter.font()
            font.setPixelSize(int(48 * (width / 200)))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(int(x), int(y), int(width), int(height),
                           Qt.AlignmentFlag.AlignCenter, time_str)
        
        elif content_type == ContentType.CALENDAR:
            # Draw calendar placeholder
            painter.setBrush(QBrush(QColor(240, 240, 240)))
            painter.drawRect(int(x), int(y), int(width), int(height))
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawText(int(x), int(y), int(width), int(height),
                           Qt.AlignmentFlag.AlignCenter, "📅")
        
        elif content_type == ContentType.TIMING:
            # Draw timer/countdown widget
            from core.timer_widget import TimerWidget
            element_id = properties.get("id", "")
            
            # Get or create timer widget
            if element_id not in self.timer_widgets:
                timer_widget = TimerWidget(properties)
                if properties.get("auto_start", True):
                    timer_widget.start()
                self.timer_widgets[element_id] = timer_widget
            else:
                timer_widget = self.timer_widgets[element_id]
                # Update properties if changed
                timer_widget.properties = properties
                timer_widget.is_countdown = properties.get("mode", "countdown") == "countdown"
                timer_widget.duration_seconds = properties.get("duration", 60)
            
            # Display timer text
            timer_text = timer_widget.get_display_text()
            color = QColor(properties.get("color", "#000000"))
            font_size = properties.get("font_size", 48)
            painter.setPen(QPen(color, 1))
            font = painter.font()
            font.setPixelSize(int(font_size * (width / 200)))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(int(x), int(y), int(width), int(height),
                           Qt.AlignmentFlag.AlignCenter, timer_text)
        
        elif content_type == ContentType.WEATHER:
            # Draw weather widget
            from core.weather_widget import WeatherWidget
            element_id = properties.get("id", "")
            
            # Get or create weather widget
            if not hasattr(self, 'weather_widgets'):
                self.weather_widgets: Dict[str, WeatherWidget] = {}
            
            if element_id not in self.weather_widgets:
                weather_widget = WeatherWidget(properties)
                self.weather_widgets[element_id] = weather_widget
            else:
                weather_widget = self.weather_widgets[element_id]
                # Update properties if changed
                weather_widget.properties = properties
                weather_widget.api_key = properties.get("api_key", "")
                weather_widget.city = properties.get("city", "London")
                weather_widget.units = properties.get("units", "metric")
                weather_widget.update_interval = properties.get("update_interval", 3600)
            
            # Display weather text
            format_string = properties.get("format", "{city}: {temperature}°C, {description}")
            weather_text = weather_widget.get_display_text(format_string)
            color = QColor(properties.get("color", "#000000"))
            font_size = properties.get("font_size", 24)
            
            painter.setPen(QPen(color, 1))
            font = painter.font()
            font.setPixelSize(int(font_size * (width / 200)))
            painter.setFont(font)
            painter.drawText(int(x), int(y), int(width), int(height),
                           Qt.AlignmentFlag.AlignCenter, weather_text)
        
        elif content_type == ContentType.TEXT_3D:
            # Draw 3D text (fallback to 2D if OpenGL not available)
            element_id = properties.get("id", "")
            text = properties.get("text", "3D Text")
            font_size = properties.get("font_size", 48)
            color = QColor(properties.get("color", "#000000"))
            
            # Try to use 3D renderer if available
            try:
                from core.text_3d_renderer import Text3DRenderer
                if not hasattr(self, '_text_3d_renderer'):
                    self._text_3d_renderer = Text3DRenderer()
                    self._text_3d_renderer.initialize()
                
                # For now, render as 2D text with shadow to simulate 3D
                # Full 3D rendering would require OpenGL widget
                shadow_offset = properties.get("depth", 10.0) / 10.0
                
                # Draw shadow (simulates depth)
                shadow_color = QColor(color)
                shadow_color.setAlpha(100)
                painter.setPen(QPen(shadow_color, 1))
                font = painter.font()
                font.setPixelSize(int(font_size * (width / 200)))
                font.setBold(True)
                painter.setFont(font)
                
                # Draw multiple shadows for 3D effect
                for i in range(3):
                    offset = shadow_offset * (i + 1)
                    painter.drawText(
                        int(x + offset), int(y + offset), 
                        int(width), int(height),
                        Qt.AlignmentFlag.AlignCenter, text
                    )
                
                # Draw main text
                painter.setPen(QPen(color, 1))
                painter.drawText(int(x), int(y), int(width), int(height),
                               Qt.AlignmentFlag.AlignCenter, text)
            except Exception as e:
                # Fallback to regular text
                from utils.logger import get_logger
                logger = get_logger(__name__)
                logger.warning(f"3D text rendering failed, using 2D fallback: {e}")
                painter.setPen(QPen(color, 1))
                font = painter.font()
                font.setPixelSize(int(font_size * (width / 200)))
                painter.setFont(font)
                painter.drawText(int(x), int(y), int(width), int(height),
                               Qt.AlignmentFlag.AlignCenter, text)
        
        else:
            # Default: draw as colored rectangle with type label
            colors = {
                ContentType.ANIMATION: QColor(255, 192, 203),
                ContentType.TEXT_3D: QColor(255, 165, 0),
                ContentType.SENSOR: QColor(144, 238, 144),
                ContentType.WPS: QColor(255, 20, 147),
                ContentType.TABLE: QColor(176, 196, 222),
                ContentType.OFFICE: QColor(255, 228, 181),
                ContentType.DIGITAL_WATCH: QColor(221, 160, 221),
                ContentType.HTML: QColor(152, 251, 152),
                ContentType.LIVESTREAM: QColor(255, 99, 71),
                ContentType.QR_CODE: QColor(255, 255, 224),
                ContentType.HDMI: QColor(135, 206, 250),
                ContentType.NEON: QColor(255, 0, 0),
                ContentType.DIGITAL_WATCH: QColor(255, 140, 0),
                ContentType.HTML: QColor(100, 149, 237),
                ContentType.LIVESTREAM: QColor(50, 50, 50),
                ContentType.QR_CODE: QColor(0, 0, 0),
                ContentType.HDMI: QColor(50, 50, 50),
            }
            # Check for neon type specifically
            if content_type == ContentType.NEON:
                # Draw neon effect using resources
                neon_index = properties.get("neon_index", 0)
                from core.resource_manager import resource_manager
                neon_pixmap = resource_manager.get_neon_background(neon_index)
                if neon_pixmap:
                    # Scale and draw neon background
                    scaled_neon = neon_pixmap.scaled(
                        int(width), int(height),
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    painter.drawPixmap(int(x), int(y), scaled_neon)
                else:
                    # Fallback to colored rectangle
                    painter.setBrush(QBrush(QColor(255, 0, 0)))
                    painter.drawRect(int(x), int(y), int(width), int(height))
                    painter.setPen(QPen(QColor(255, 255, 255), 1))
                    painter.drawText(int(x), int(y), int(width), int(height),
                                   Qt.AlignmentFlag.AlignCenter, "💡")
            else:
                color = colors.get(content_type, QColor(200, 200, 200))
                painter.setBrush(QBrush(color))
                painter.drawRect(int(x), int(y), int(width), int(height))
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                font = painter.font()
                font.setPixelSize(int(12 * (width / 200)))
                painter.setFont(font)
                type_label = content_type.value.replace("_", " ").title()
                painter.drawText(int(x), int(y), int(width), int(height),
                               Qt.AlignmentFlag.AlignCenter, type_label)


class Canvas(QWidget):
    """Main canvas for displaying and editing program content"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program: Program = None
        self.zoom_level = 100  # Percentage
        # Enable keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        # Set black border for canvas
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #000000;
            }
        """)
        
        # Main layout - use a container widget for overlay positioning
        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Canvas widget (will be drawn in paintEvent)
        self.canvas_widget = CanvasWidget(self)
        self.canvas_widget.setMinimumSize(800, 600)
        container_layout.addWidget(self.canvas_widget, stretch=1)
        
        # Main layout for this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(container)
        
        # Zoom controls (bottom-right corner overlay)
        self.zoom_container = QWidget(self)
        self.zoom_container.setStyleSheet("background-color: transparent; border: none;")
        zoom_layout = QHBoxLayout(self.zoom_container)
        zoom_layout.setContentsMargins(2, 2, 2, 2)
        zoom_layout.setSpacing(2)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(25, 25)
        self.zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                border: 1px solid #212121;
                border-radius: 2px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #212121;
            }
        """)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedSize(40, 25)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setStyleSheet("""
            QLabel {
                background-color: #424242;
                border: 1px solid #212121;
                border-radius: 2px;
                color: #FFFFFF;
                padding: 2px;
                font-size: 11px;
            }
        """)
        zoom_layout.addWidget(self.zoom_label)
        
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setFixedSize(25, 25)
        self.zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                border: 1px solid #212121;
                border-radius: 2px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #212121;
            }
        """)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        self.zoom_container.setFixedSize(100, 35)
        self.zoom_container.raise_()  # Ensure it's on top
        # Position will be set in resizeEvent
    
    def resizeEvent(self, event):
        """Handle resize event to position zoom controls"""
        super().resizeEvent(event)
        # Position zoom controls in bottom-right corner
        if hasattr(self, 'zoom_container') and self.zoom_container:
            x = self.width() - self.zoom_container.width() - 5
            y = self.height() - self.zoom_container.height() - 5
            self.zoom_container.move(x, y)
            self.zoom_container.show()
            self.zoom_container.raise_()
    
    def showEvent(self, event):
        """Handle show event to position zoom controls"""
        super().showEvent(event)
        # Position zoom controls when widget is shown
        if hasattr(self, 'zoom_container') and self.zoom_container:
            x = self.width() - self.zoom_container.width() - 5
            y = self.height() - self.zoom_container.height() - 5
            self.zoom_container.move(x, y)
            self.zoom_container.show()
            self.zoom_container.raise_()
    
    def set_program(self, program: Program):
        """Set the current program"""
        self.program = program
        self.canvas_widget.set_program(program)
        # Update zoom in canvas widget to match current zoom level
        self.canvas_widget.set_zoom(self.zoom_level)
        if program:
            # Update canvas size based on program dimensions
            self.canvas_widget.setMinimumSize(program.width // 2, program.height // 2)
        self.update()
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(200, self.zoom_level + 10)
        self.update_zoom()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(25, self.zoom_level - 10)
        self.update_zoom()
    
    def update_zoom(self):
        """Update zoom display and canvas"""
        self.zoom_label.setText(f"{self.zoom_level}%")
        # Apply zoom transformation to canvas widget
        self.canvas_widget.set_zoom(self.zoom_level)
        self.canvas_widget.update()

