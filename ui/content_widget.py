from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QSize, Qt, QUrl, QTimer
from PyQt5.QtWidgets import QWidget
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    QWebEngineView = None # type: ignore
from typing import Optional, Dict, TYPE_CHECKING, Any
from core.screen_config import get_screen_config
from utils.logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from core.screen_manager import ScreenManager


class ContentWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, screen_manager: Optional['ScreenManager'] = None):
        super().__init__(parent)
        self.screen_manager = screen_manager
        self.setStyleSheet("""
            ContentWidget {
                border-left: 1px solid #555555;
            }
        """)
        self.checker_size = 10
        self.color1 = QtGui.QColor(43, 43, 43)
        self.color2 = QtGui.QColor(35, 35, 35)
        self._cached_pixmap = None
        self._cached_size = QSize()
        self.scale_factor = 1.0
        self.screen_offset_x = 0
        self.screen_offset_y = 0
        self.selected_element_id: Optional[str] = None
        self.properties_panel = None
        self.screen_list_panel = None
        self._video_captures: Dict[str, Any] = {}
        self._video_frames: Dict[str, Optional[QtGui.QPixmap]] = {}
        self._video_timers: Dict[str, QTimer] = {}
        self._video_paths: Dict[str, str] = {}
        self._html_widgets: Dict[str, QWidget] = {}
        self._html_refresh_timers: Dict[str, QTimer] = {}
        self._is_playing = False
        self._media_order: list = []
        self._photo_animations: Dict[str, Dict] = {}
        self._text_animations: Dict[str, Dict] = {}
        self._text_flow_animations: Dict[str, Dict] = {}
        self._animation_timer = QtCore.QTimer(self)
        self._animation_timer.timeout.connect(self._update_animations)
        self._animation_timer.setInterval(33)
        self._clock_timer = QtCore.QTimer(self)
        self._clock_timer.timeout.connect(self._update_clocks)
        self._clock_timer.setInterval(1000)
        self._clock_timer.start()
        self.setMouseTracking(True)
        self._drag_state = None
        self._resize_handle_size = 8
        self._hover_handle = None
    
    def set_screen_manager(self, screen_manager: Optional['ScreenManager']):
        self.screen_manager = screen_manager
    
    def set_properties_panel(self, properties_panel):
        self.properties_panel = properties_panel
        if properties_panel:
            properties_panel.property_changed.connect(self._on_property_changed)
    
    def set_screen_list_panel(self, screen_list_panel):
        self.screen_list_panel = screen_list_panel
    
    def add_content(self, program_id: str, content_type: str):
        if not self.screen_manager:
            return
        
        program = self.screen_manager.get_program_by_id(program_id)
        if not program:
            return
        
        import uuid
        from datetime import datetime
        
        screen_config = get_screen_config()
        screen_width = screen_config.get("width", 640) if screen_config else 640
        screen_height = screen_config.get("height", 480) if screen_config else 480
        
        element_id = f"element_{uuid.uuid4().hex[:12]}"
        
        existing_count = sum(1 for e in program.elements if e.get("type") == content_type)
        default_name = f"{content_type.capitalize()} {existing_count + 1}"
        
        default_width = min(1920, screen_width)
        default_height = min(1080, screen_height)
        
        element: Dict[str, Any] = {
            "id": element_id,
            "type": content_type,
            "name": default_name,
            "x": 0,
            "y": 0,
            "width": default_width,
            "height": default_height,
            "properties": {
                "x": 0,
                "y": 0,
                "width": default_width,
                "height": default_height,
            },
            "duration": 0,
            "transition_in": "",
            "transition_out": "",
            "file_path": ""
        }
        
        properties: Dict[str, Any] = element.get("properties", {})
        
        if content_type == "video":
            properties["video_list"] = []
            properties["frame"] = {
                "enabled": False,
                "border": "---",
                "effect": "---",
                "speed": "---"
            }
            properties["video_shot"] = {
                "enabled": False,
                "width": default_width,
                "height": default_height,
                "start_time": "00:00:00",
                "end_time": "00:00:30"
            }
        elif content_type == "photo":
            properties["photo_list"] = []
            properties["animation"] = {
                "entrance": "Random",
                "exit": "Random",
                "entrance_speed": "1 fast",
                "exit_speed": "1 fast",
                "hold_time": 0.0
            }
        elif content_type == "text":
            properties["text"] = {
                "content": "",
                "format": {
                    "font_family": "MS Shell Dlg 2",
                    "font_size": 16,
                    "font_color": "#ffffff",
                    "text_bg_color": "",
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "alignment": "center",
                    "outline": False
                },
                "background_color": "#55ffff",
                "edit_bg_color": 8344917,
                "trans_bg_color": 1,
                "stroke_color": 65280,
                "use_hollow": 0,
                "use_stroke": 0,
                "single_mode": 0,
                "page_count": 1,
                "head_close_to_tail": 1
            }
            element["properties"]["animation"] = {
                "entrance": "Random",
                "exit": "Random",
                "entrance_speed": "1 fast",
                "exit_speed": "1 fast",
                "hold_time": 5.0,
                "speed_time_index": 4,
                "clear_effect": 1,
                "clear_time": 4,
                "disp_effect": 1,
                "disp_time": 4
            }
            element["properties"]["alpha"] = 255
            element["properties"]["frame_speed"] = 4
            element["properties"]["frame_type"] = 0
            element["properties"]["lock_area"] = 0
            element["properties"]["motley_index"] = 0
            element["properties"]["purity_color"] = 255
            element["properties"]["purity_index"] = 0
            element["properties"]["tricolor_index"] = 0
            element["properties"]["font_size"] = 24
        elif content_type == "clock":
            element["properties"]["clock"] = {
                "type": "System",
                "timezone": "Local",
                "correction": 0,
                "system": {
                    "font_family": "Arial",
                    "font_size": 24,
                    "title_enabled": True,
                    "title_value": "LED",
                    "title_color": "#0000FF",
                    "date_enabled": True,
                    "date_format": "YYYY-MM-DD",
                    "date_color": "#0000FF",
                    "week_enabled": True,
                    "week_format": "Full Name",
                    "week_color": "#00FF00",
                    "noon_enabled": True,
                    "noon_color": "#0000FF",
                    "hour_scale_shape": "straight line",
                    "hour_scale_color": "#FF0000",
                    "minute_scale_shape": "round",
                    "minute_scale_color": "#00FF00",
                    "hour_hand_shape": "rectangle",
                    "hour_hand_color": "#FF0000",
                    "minute_hand_shape": "rectangle",
                    "minute_hand_color": "#00FF00",
                    "second_hand_shape": "rectangle",
                    "second_hand_color": "#0000FF"
                },
                "digital": {
                    "font_family": "Arial",
                    "font_size": 24,
                    "line_setting": "Single Line",
                    "title_enabled": True,
                    "title_value": "Clock",
                    "title_color": "#FF0000",
                    "date_enabled": True,
                    "date_format": "YYYY-MM-DD",
                    "date_color": "#0000FF",
                    "time_enabled": True,
                    "time_format": "HH:MM:SS",
                    "time_color": "#FF0000",
                    "week_enabled": True,
                    "week_format": "Full Name",
                    "week_color": "#00FF00"
                }
            }
            element["properties"]["animation"] = {
                "entrance": "Random",
                "exit": "Random",
                "entrance_speed": "1 fast",
                "exit_speed": "1 fast",
                "hold_time": 5.0
            }
        
        program.elements.append(element)
        program.modified = datetime.now().isoformat()
        
        if self.screen_list_panel:
            self.screen_list_panel.refresh_screens(debounce=False)
        
        self.update()
        
        if self.properties_panel:
            self.properties_panel.set_element(element, program)
    
    def add_content_to_current_program(self, content_type: str):
        if not self.screen_manager:
            return
        
        if not self.screen_manager.current_screen:
            if self.screen_manager.screens:
                self.screen_manager.current_screen = self.screen_manager.screens[0]
            else:
                return
        
        if not self.screen_manager.current_screen.programs:
            from core.screen_config import get_screen_name
            screen_name = get_screen_name()
            if screen_name:
                if self.screen_list_panel:
                    self.screen_list_panel.add_program_to_screen(screen_name)
                    if self.screen_manager.current_screen.programs:
                        program = self.screen_manager.current_screen.programs[0]
                        self.add_content(program.id, content_type)
            return
        
        program = self.screen_manager.current_screen.programs[0]
        self.add_content(program.id, content_type)
    
    def set_selected_element(self, element_id: Optional[str]):
        self.selected_element_id = element_id
        self.update()
    
    def set_playing(self, playing: bool):
        self._is_playing = playing
        
        if playing:
            if not self._animation_timer.isActive():
                self._animation_timer.start()
            if not self._clock_timer.isActive():
                self._clock_timer.start()
            self._initialize_videos_for_program()
        else:
            if self._animation_timer.isActive():
                self._animation_timer.stop()
        self.update()
    
    
    def _setup_video_player(self, element_id: str, video_path: str):
        from pathlib import Path
        video_file = Path(video_path)
        video_path_abs = str(video_file.absolute())
        
        if element_id in self._video_paths:
            if self._video_paths[element_id] == video_path_abs:
                return
            self._cleanup_video_player(element_id)
        
        if not video_path or not video_path.strip():
            return
        
        if not CV2_AVAILABLE:
            return
        
        from pathlib import Path
        video_file = Path(video_path)
        if not video_file.exists() or not video_file.is_file():
            return
        
        try:
            cap = cv2.VideoCapture(str(video_file.absolute()))
            if not cap.isOpened():
                return
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30
            
            self._video_captures[element_id] = cap
            self._video_frames[element_id] = None
            self._video_paths[element_id] = video_path_abs
            
            timer = QTimer(self)
            timer.timeout.connect(lambda eid=element_id: self._update_video_frame(eid))
            timer.start(int(1000 / fps))
            self._video_timers[element_id] = timer
            
            if ('video', element_id) not in self._media_order:
                self._media_order.append(('video', element_id))
            else:
                self._media_order.remove(('video', element_id))
                self._media_order.append(('video', element_id))
            
            self._update_video_frame(element_id)
        except Exception as e:
            logger.warning(f"Failed to setup video player for {element_id}: {e}")
            return
    
    def _update_video_frame(self, element_id: str):
        if element_id not in self._video_captures:
            return
        
        cap = self._video_captures[element_id]
        if not cap.isOpened():
            return
        
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qt_image)
            self._video_frames[element_id] = pixmap
            self.update()
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def _initialize_videos_for_program(self):
        elements = self._get_current_program_elements()
        for element in elements:
            element_type = element.get("type", "")
            if element_type == "video":
                element_id = element.get("id", "")
                element_props = element.get("properties", {})
                video_list = element_props.get("video_list", [])
                if video_list and len(video_list) > 0:
                    active_index = self._get_video_active_index(element_id, video_list)
                    if 0 <= active_index < len(video_list):
                        video_path = video_list[active_index].get("path", "")
                        if video_path:
                            from pathlib import Path
                            if Path(video_path).exists():
                                self._setup_video_player(element_id, video_path)
    
    def _start_videos_for_program(self):
        if not CV2_AVAILABLE:
            return
        elements = self._get_current_program_elements()
        for element in elements:
            element_type = element.get("type", "")
            if element_type == "video":
                element_id = element.get("id", "")
                if element_id in self._video_captures:
                    cap = self._video_captures[element_id]
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                elif element_id not in self._video_paths:
                    element_props = element.get("properties", {})
                    video_list = element_props.get("video_list", [])
                    if video_list and len(video_list) > 0:
                        active_index = self._get_video_active_index(element_id, video_list)
                        if 0 <= active_index < len(video_list):
                            video_path = video_list[active_index].get("path", "")
                            if video_path:
                                from pathlib import Path
                                if Path(video_path).exists():
                                    self._setup_video_player(element_id, video_path)
    
    
    def _cleanup_video_player(self, element_id: str):
        try:
            if element_id in self._video_captures:
                cap = self._video_captures[element_id]
                cap.release()
                del self._video_captures[element_id]
            if element_id in self._video_frames:
                del self._video_frames[element_id]
            if element_id in self._video_timers:
                self._video_timers[element_id].stop()
                del self._video_timers[element_id]
            if element_id in self._video_paths:
                del self._video_paths[element_id]
            self._media_order = [(t, eid) for t, eid in self._media_order if not (t == 'video' and eid == element_id)]
        except Exception as e:
            logger.warning(f"Error cleaning up video player {element_id}: {e}")
    
    def _cleanup_video_players(self):
        current_elements = {e.get("id") for e in self._get_current_program_elements() if e.get("type") == "video"}
        
        for element_id in list(self._video_captures.keys()):
            if element_id not in current_elements:
                self._cleanup_video_player(element_id)
    
    def _cleanup_all_video_players(self):
        for element_id in list(self._video_captures.keys()):
            try:
                if element_id in self._video_captures:
                    cap = self._video_captures[element_id]
                    cap.release()
                    del self._video_captures[element_id]
                if element_id in self._video_frames:
                    del self._video_frames[element_id]
                if element_id in self._video_timers:
                    self._video_timers[element_id].stop()
                    del self._video_timers[element_id]
                self._media_order = [(t, eid) for t, eid in self._media_order if not (t == 'video' and eid == element_id)]
            except Exception as e:
                logger.warning(f"Error cleaning up video player {element_id}: {e}")
    
    def _get_photo_active_index(self, element_id: str, photo_list: list) -> int:
        if self.properties_panel and hasattr(self.properties_panel, 'image_properties_widget'):
            image_widget = self.properties_panel.image_properties_widget
            if image_widget and hasattr(image_widget, 'photo_list'):
                if image_widget.current_element and image_widget.current_element.get("id") == element_id:
                    active_idx = image_widget.photo_list.get_active_index()
                    if 0 <= active_idx < len(photo_list):
                        return active_idx
        
        if element_id in self._photo_animations:
            anim_state = self._photo_animations[element_id]
        if element_id in self._text_animations:
            anim_state = self._text_animations[element_id]
            return anim_state.get("current_photo_index", 0)
        return 0
    
    def _get_video_active_index(self, element_id: str, video_list: list) -> int:
        if self.properties_panel and hasattr(self.properties_panel, 'video_properties_widget'):
            video_widget = self.properties_panel.video_properties_widget
            if video_widget and hasattr(video_widget, 'video_list'):
                if video_widget.current_element and video_widget.current_element.get("id") == element_id:
                    active_idx = video_widget.video_list.get_active_index()
                    if 0 <= active_idx < len(video_list):
                        return active_idx
        
        elements = self._get_current_program_elements()
        element = next((e for e in elements if e.get("id") == element_id), None)
        if element:
            element_props = element.get("properties", {})
            active_idx = element_props.get("active_video_index", 0)
            if 0 <= active_idx < len(video_list):
                return active_idx
        return 0
    
    def _draw_photo_with_animation(self, painter, pixmap, x, y, width, height, element_id, animation_props, element_rect, is_selected):
        import random
        
        entrance_anim = animation_props.get("entrance", "None")
        exit_anim = animation_props.get("exit", "None")
        
        elements = self._get_current_program_elements()
        element = next((e for e in elements if e.get("id") == element_id), None)
        element_props = element.get("properties", {}) if element else {}
        fit_mode = element_props.get("fit_mode", "Keep Aspect Ratio")
        
        if entrance_anim == "Immediate Show" and exit_anim == "Immediate Clear":
            aspect_ratio_mode = Qt.IgnoreAspectRatio if fit_mode == "Stretch" else Qt.KeepAspectRatio
            scaled_pixmap = pixmap.scaled(width, height, aspect_ratio_mode, Qt.SmoothTransformation)
            scaled_width = scaled_pixmap.width()
            scaled_height = scaled_pixmap.height()
            if fit_mode == "Stretch":
                draw_x = x
                draw_y = y
            else:
                draw_x = x + (width - scaled_width) // 2
                draw_y = y + (height - scaled_height) // 2
            painter.drawPixmap(draw_x, draw_y, scaled_pixmap)
            if is_selected:
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                painter.drawRect(element_rect)
            # Clean up animation state if it exists
            if element_id in self._photo_animations:
                del self._photo_animations[element_id]
            return
        
        if element_id not in self._photo_animations:
            self._photo_animations[element_id] = {
                "current_photo_index": 0,
                "phase": "entrance",
                "progress": 0.0,
                "start_time": QtCore.QDateTime.currentDateTime(),
                "entrance_duration": 1000.0,
                "hold_duration": 0.0,
                "exit_duration": 1000.0,
                "selected_entrance_anim": None,
                "selected_exit_anim": None
            }
            if not self._animation_timer.isActive():
                self._animation_timer.start()
            self._start_videos_for_program()
        
        anim_state = self._photo_animations[element_id]
        
        available_animations = [
            "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ]
        
        if entrance_anim == "Random":
            if anim_state["selected_entrance_anim"] is None or (anim_state["phase"] == "entrance" and anim_state["progress"] == 0.0):
                if available_animations:
                    anim_state["selected_entrance_anim"] = random.choice(available_animations)
                else:
                    anim_state["selected_entrance_anim"] = "Immediate Show"
            entrance_anim = anim_state["selected_entrance_anim"]
        
        if exit_anim == "Random":
            if anim_state["selected_exit_anim"] is None or (anim_state["phase"] == "exit" and anim_state["progress"] == 0.0):
                if available_animations:
                    anim_state["selected_exit_anim"] = random.choice(available_animations)
                else:
                    anim_state["selected_exit_anim"] = "Immediate Clear"
            exit_anim = anim_state["selected_exit_anim"]
        hold_time = animation_props.get("hold_time", 0.0)
        entrance_speed = animation_props.get("entrance_speed", "1 fast")
        exit_speed = animation_props.get("exit_speed", "1 fast")
        
        speed_multiplier = self._get_speed_multiplier(entrance_speed if anim_state["phase"] == "entrance" else exit_speed)
        
        if entrance_anim == "Immediate Show":
            anim_state["entrance_duration"] = 0.0
        else:
            anim_state["entrance_duration"] = 1000.0 / speed_multiplier
        
        if exit_anim == "Immediate Clear" or exit_anim == "None":
            anim_state["exit_duration"] = 0.0
        else:
            anim_state["exit_duration"] = 1000.0 / speed_multiplier
        
        anim_state["hold_duration"] = hold_time * 1000.0
        
        elapsed = anim_state["start_time"].msecsTo(QtCore.QDateTime.currentDateTime())
        
        if anim_state["phase"] == "entrance":
            duration = anim_state["entrance_duration"]
            if elapsed >= duration:
                anim_state["phase"] = "hold"
                anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
                elapsed = 0
            else:
                anim_state["progress"] = elapsed / duration if duration > 0 else 1.0
        elif anim_state["phase"] == "hold":
            if entrance_anim == "Immediate Show":
                anim_state["progress"] = 1.0
            else:
                duration = anim_state["hold_duration"]
                if elapsed >= duration:
                    anim_state["phase"] = "exit"
                    anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
                    elapsed = 0
                else:
                    anim_state["progress"] = 1.0
        elif anim_state["phase"] == "exit":
            if entrance_anim == "Immediate Show":
                anim_state["phase"] = "hold"
                anim_state["progress"] = 1.0
            else:
                duration = anim_state["exit_duration"]
                if elapsed >= duration:
                    anim_state["phase"] = "entrance"
                    anim_state["current_photo_index"] = (anim_state["current_photo_index"] + 1) % self._get_photo_count(element_id)
                    anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
                    elapsed = 0
                    anim_state["progress"] = 0.0
                    # Reset random selections for new cycle
                    anim_state["selected_entrance_anim"] = None
                    anim_state["selected_exit_anim"] = None
                    self._start_videos_for_program()
                else:
                    anim_state["progress"] = elapsed / duration if duration > 0 else 1.0
        
        elements = self._get_current_program_elements()
        element = next((e for e in elements if e.get("id") == element_id), None)
        element_props = element.get("properties", {}) if element else {}
        fit_mode = element_props.get("fit_mode", "Keep Aspect Ratio")
        aspect_ratio_mode = Qt.IgnoreAspectRatio if fit_mode == "Stretch" else Qt.KeepAspectRatio
        
        scaled_pixmap = pixmap.scaled(width, height, aspect_ratio_mode, Qt.SmoothTransformation)
        
        scaled_width = scaled_pixmap.width()
        scaled_height = scaled_pixmap.height()
        if fit_mode == "Stretch":
            draw_x = x
            draw_y = y
        else:
            draw_x = x + (width - scaled_width) // 2
            draw_y = y + (height - scaled_height) // 2
        
        if anim_state["phase"] == "entrance":
            self._apply_entrance_animation(painter, scaled_pixmap, draw_x, draw_y, width, height, entrance_anim, anim_state["progress"])
        elif anim_state["phase"] == "hold":
            painter.drawPixmap(draw_x, draw_y, scaled_pixmap)
        elif anim_state["phase"] == "exit":
            self._apply_exit_animation(painter, scaled_pixmap, draw_x, draw_y, width, height, exit_anim, anim_state["progress"])
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
            painter.drawRect(element_rect)
    
    def _get_speed_multiplier(self, speed_str: str) -> float:
        try:
            speed_num = int(speed_str.split()[0])
            return max(0.1, 1 - speed_num * 0.1)
        except (ValueError, IndexError, AttributeError):
            return 0.9
    
    def _get_photo_count(self, element_id: str) -> int:
        elements = self._get_current_program_elements()
        for element in elements:
            if element.get("id") == element_id:
                element_props = element.get("properties", {})
                photo_list = element_props.get("photo_list", element_props.get("image_list", []))
                return max(1, len(photo_list))
        return 1
    
    def _apply_entrance_animation(self, painter, pixmap, x, y, width, height, anim_type, progress):
        import random
        
        # Available animations (excluding Random and Immediate Show)
        available_animations = [
            "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ]
        
        if anim_type == "Random":
            anim_type = random.choice(available_animations)
        
        if anim_type == "Immediate Show" or anim_type == "None":
            painter.drawPixmap(x, y, pixmap)
            return
        
        if anim_type == "Move Left":
            offset_x = int((1.0 - progress) * width)
            painter.drawPixmap(x + offset_x, y, pixmap)
        elif anim_type == "Move Right":
            offset_x = int(-(1.0 - progress) * width)
            painter.drawPixmap(x + offset_x, y, pixmap)
        elif anim_type == "Move Up":
            offset_y = int((1.0 - progress) * height)
            painter.drawPixmap(x, y + offset_y, pixmap)
        elif anim_type == "Move Down":
            offset_y = int(-(1.0 - progress) * height)
            painter.drawPixmap(x, y + offset_y, pixmap)
        elif anim_type == "Cover Left":
            clip_width = int(progress * width)
            painter.setClipRect(x, y, clip_width, height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Cover Right":
            clip_x = int(x + (1.0 - progress) * width)
            clip_width = int(progress * width)
            painter.setClipRect(clip_x, y, clip_width, height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Cover Up":
            clip_height = int(progress * height)
            painter.setClipRect(x, y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Cover Down":
            clip_y = int(y + (1.0 - progress) * height)
            clip_height = int(progress * height)
            painter.setClipRect(x, clip_y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Top Left Cover":
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            painter.setClipRect(x, y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Top Right Cover":
            clip_x = int(x + (1.0 - progress) * width)
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            painter.setClipRect(clip_x, y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Bottom Left Cover":
            clip_width = int(progress * width)
            clip_y = int(y + (1.0 - progress) * height)
            clip_height = int(progress * height)
            painter.setClipRect(x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Bottom Right Cover":
            clip_x = int(x + (1.0 - progress) * width)
            clip_width = int(progress * width)
            clip_y = int(y + (1.0 - progress) * height)
            clip_height = int(progress * height)
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Open From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Up Down Open":
            center_y = y + height // 2
            clip_height = int(progress * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Close From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Up Down Close":
            center_y = y + height // 2
            clip_height = int((1.0 - progress) * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Gradual Change":
            painter.setOpacity(progress)
            painter.drawPixmap(x, y, pixmap)
            painter.setOpacity(1.0)
        elif anim_type == "Vertical Blinds":
            num_strips = 8
            strip_height = height / num_strips
            for i in range(num_strips):
                strip_y = y + i * strip_height
                if (i % 2 == 0 and progress > 0.5) or (i % 2 == 1 and progress <= 0.5):
                    clip_progress = min(1.0, progress * 2) if i % 2 == 0 else min(1.0, (progress - 0.5) * 2)
                    clip_height = int(clip_progress * strip_height)
                    painter.setClipRect(x, int(strip_y), width, clip_height)
                    painter.drawPixmap(x, y, pixmap)
                    painter.setClipping(False)
            painter.drawPixmap(x, y, pixmap)
        elif anim_type == "Horizontal Blinds":
            num_strips = 8
            strip_width = width / num_strips
            for i in range(num_strips):
                strip_x = x + i * strip_width
                if (i % 2 == 0 and progress > 0.5) or (i % 2 == 1 and progress <= 0.5):
                    clip_progress = min(1.0, progress * 2) if i % 2 == 0 else min(1.0, (progress - 0.5) * 2)
                    clip_width = int(clip_progress * strip_width)
                    painter.setClipRect(int(strip_x), y, clip_width, height)
                    painter.drawPixmap(x, y, pixmap)
                    painter.setClipping(False)
            painter.drawPixmap(x, y, pixmap)
        elif anim_type == "Twinkle":
            opacity = 0.5 + 0.5 * abs((progress * 4) % 2 - 1)
            painter.setOpacity(opacity)
            painter.drawPixmap(x, y, pixmap)
            painter.setOpacity(1.0)
        else:
            # Default: fade in
            painter.setOpacity(progress)
            painter.drawPixmap(x, y, pixmap)
            painter.setOpacity(1.0)
    
    def _apply_exit_animation(self, painter, pixmap, x, y, width, height, anim_type, progress):
        if anim_type == "Immediate Clear" or anim_type == "None":
            return
        
        if anim_type == "Move Left":
            offset_x = int(-progress * width)
            painter.drawPixmap(x + offset_x, y, pixmap)
        elif anim_type == "Move Right":
            offset_x = int(progress * width)
            painter.drawPixmap(x + offset_x, y, pixmap)
        elif anim_type == "Move Up":
            offset_y = int(-progress * height)
            painter.drawPixmap(x, y + offset_y, pixmap)
        elif anim_type == "Move Down":
            offset_y = int(progress * height)
            painter.drawPixmap(x, y + offset_y, pixmap)
        elif anim_type == "Cover Left":
            clip_width = int((1.0 - progress) * width)
            painter.setClipRect(x, y, clip_width, height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Cover Right":
            clip_x = int(x + progress * width)
            clip_width = int((1.0 - progress) * width)
            painter.setClipRect(clip_x, y, clip_width, height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Cover Up":
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Cover Down":
            clip_y = int(y + progress * height)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, clip_y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Top Left Cover":
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Top Right Cover":
            clip_x = int(x + progress * width)
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(clip_x, y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Bottom Left Cover":
            clip_width = int((1.0 - progress) * width)
            clip_y = int(y + progress * height)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Bottom Right Cover":
            clip_x = int(x + progress * width)
            clip_width = int((1.0 - progress) * width)
            clip_y = int(y + progress * height)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Open From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Up Down Open":
            center_y = y + height // 2
            clip_height = int((1.0 - progress) * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Close From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Up Down Close":
            center_y = y + height // 2
            clip_height = int(progress * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            painter.drawPixmap(x, y, pixmap)
            painter.setClipping(False)
        elif anim_type == "Gradual Change":
            painter.setOpacity(1.0 - progress)
            painter.drawPixmap(x, y, pixmap)
            painter.setOpacity(1.0)
        elif anim_type == "Vertical Blinds":
            num_strips = 8
            strip_height = height / num_strips
            for i in range(num_strips):
                strip_y = y + i * strip_height
                if (i % 2 == 0 and progress < 0.5) or (i % 2 == 1 and progress >= 0.5):
                    clip_progress = max(0.0, 1.0 - progress * 2) if i % 2 == 0 else max(0.0, 1.0 - (progress - 0.5) * 2)
                    clip_height = int(clip_progress * strip_height)
                    painter.setClipRect(x, int(strip_y), width, clip_height)
                    painter.drawPixmap(x, y, pixmap)
                    painter.setClipping(False)
            painter.drawPixmap(x, y, pixmap)
        elif anim_type == "Horizontal Blinds":
            num_strips = 8
            strip_width = width / num_strips
            for i in range(num_strips):
                strip_x = x + i * strip_width
                if (i % 2 == 0 and progress < 0.5) or (i % 2 == 1 and progress >= 0.5):
                    clip_progress = max(0.0, 1.0 - progress * 2) if i % 2 == 0 else max(0.0, 1.0 - (progress - 0.5) * 2)
                    clip_width = int(clip_progress * strip_width)
                    painter.setClipRect(int(strip_x), y, clip_width, height)
                    painter.drawPixmap(x, y, pixmap)
                    painter.setClipping(False)
            painter.drawPixmap(x, y, pixmap)
        elif anim_type == "Twinkle":
            opacity = 0.5 + 0.5 * abs(((1.0 - progress) * 4) % 2 - 1)
            painter.setOpacity(opacity)
            painter.drawPixmap(x, y, pixmap)
            painter.setOpacity(1.0)
        else:
            # Default: fade out
            painter.setOpacity(1.0 - progress)
            painter.drawPixmap(x, y, pixmap)
            painter.setOpacity(1.0)
    
    def _draw_text_with_animation(self, painter, text_content, text_format, element_props, x, y, width, height, element_id, animation_props, element_rect, is_selected, scale, is_singleline=False):
        import random
        
        entrance_anim = animation_props.get("entrance", "None")
        exit_anim = animation_props.get("exit", "None")
        
        # If both entrance and exit are "Immediate Show", skip animation entirely
        if entrance_anim == "Immediate Show" and exit_anim == "Immediate Clear":
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, element_rect, is_selected, scale, is_singleline)
            # Clean up animation state if it exists
            if element_id in self._text_animations:
                del self._text_animations[element_id]
            return
        
        if element_id not in self._text_animations:
            self._text_animations[element_id] = {
                "phase": "entrance",
                "progress": 0.0,
                "start_time": QtCore.QDateTime.currentDateTime(),
                "entrance_duration": 1000.0,
                "hold_duration": 0.0,
                "exit_duration": 1000.0,
                "selected_entrance_anim": None,
                "selected_exit_anim": None
            }
            if not self._animation_timer.isActive():
                self._animation_timer.start()
            self._start_videos_for_program()
        
        anim_state = self._text_animations[element_id]
        
        # Available animations (excluding Random and Immediate Show)
        available_animations = [
            "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ]
        
        # Add singleline-specific animations
        if is_singleline:
            available_animations.extend(["Continuous Move Left", "Continuous Move Right", "Don't Clear Screen"])
        
        # Handle Random: select and store a random animation for this cycle
        if entrance_anim == "Random":
            if anim_state["selected_entrance_anim"] is None or (anim_state["phase"] == "entrance" and anim_state["progress"] == 0.0):
                if available_animations:
                    anim_state["selected_entrance_anim"] = random.choice(available_animations)
                else:
                    anim_state["selected_entrance_anim"] = "Immediate Show"
            entrance_anim = anim_state["selected_entrance_anim"]
        
        if exit_anim == "Random":
            if anim_state["selected_exit_anim"] is None or (anim_state["phase"] == "exit" and anim_state["progress"] == 0.0):
                if available_animations:
                    anim_state["selected_exit_anim"] = random.choice(available_animations)
                else:
                    anim_state["selected_exit_anim"] = "Immediate Clear"
            exit_anim = anim_state["selected_exit_anim"]
        
        hold_time = animation_props.get("hold_time", 0.0)
        entrance_speed = animation_props.get("entrance_speed", "1 fast")
        exit_speed = animation_props.get("exit_speed", "1 fast")
        
        speed_multiplier = self._get_speed_multiplier(entrance_speed if anim_state["phase"] == "entrance" else exit_speed)
        
        if entrance_anim == "Immediate Show":
            anim_state["entrance_duration"] = 0.0
        else:
            anim_state["entrance_duration"] = 1000.0 / speed_multiplier
        
        if exit_anim == "Immediate Clear" or exit_anim == "None" or (is_singleline and exit_anim == "Don't Clear Screen"):
            anim_state["exit_duration"] = 0.0
        else:
            anim_state["exit_duration"] = 1000.0 / speed_multiplier
        
        anim_state["hold_duration"] = hold_time * 1000.0
        
        elapsed = anim_state["start_time"].msecsTo(QtCore.QDateTime.currentDateTime())
        
        if anim_state["phase"] == "entrance":
            duration = anim_state["entrance_duration"]
            if elapsed >= duration:
                anim_state["phase"] = "hold"
                anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
                elapsed = 0
            else:
                anim_state["progress"] = elapsed / duration if duration > 0 else 1.0
        elif anim_state["phase"] == "hold":
            if entrance_anim == "Immediate Show":
                anim_state["progress"] = 1.0
            else:
                duration = anim_state["hold_duration"]
                if elapsed >= duration:
                    anim_state["phase"] = "exit"
                    anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
                    elapsed = 0
                else:
                    anim_state["progress"] = 1.0
        elif anim_state["phase"] == "exit":
            if entrance_anim == "Immediate Show":
                anim_state["phase"] = "hold"
                anim_state["progress"] = 1.0
            else:
                duration = anim_state["exit_duration"]
                if elapsed >= duration:
                    anim_state["phase"] = "entrance"
                    anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
                    self._start_videos_for_program()
                    elapsed = 0
                    anim_state["progress"] = 0.0
                    # Reset random selections for new cycle
                    anim_state["selected_entrance_anim"] = None
                    anim_state["selected_exit_anim"] = None
                else:
                    anim_state["progress"] = elapsed / duration if duration > 0 else 1.0
        
        if anim_state["phase"] == "entrance":
            self._apply_text_entrance_animation(painter, text_content, text_format, element_props, x, y, width, height, entrance_anim, anim_state["progress"], scale, is_singleline)
        elif anim_state["phase"] == "hold":
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, element_rect, is_selected, scale, is_singleline)
        elif anim_state["phase"] == "exit":
            self._apply_text_exit_animation(painter, text_content, text_format, element_props, x, y, width, height, exit_anim, anim_state["progress"], scale, is_singleline)
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
            painter.drawRect(element_rect)
    
    def _draw_text_static(self, painter, text_content, text_format, element_props, x, y, width, height, element_rect, is_selected, scale, is_singleline=False):
        if element_rect is not None:
            element_bounds = QtCore.QRect(x, y, width, height)
            painter.setClipRect(element_bounds)
        
        font = painter.font()
        font_size = element_props.get("font_size", 24)
        if text_format.get("font_size"):
            font_size = text_format.get("font_size", font_size)
        font.setPointSize(max(8, int(font_size * scale)))
        
        if text_format.get("font_family"):
            font.setFamily(text_format.get("font_family"))
        if text_format.get("bold"):
            font.setBold(True)
        if text_format.get("italic"):
            font.setItalic(True)
        if text_format.get("underline"):
            font.setUnderline(True)
        painter.setFont(font)
        
        text_color_str = element_props.get("text_color", "#FFFFFF")
        if text_format.get("font_color"):
            text_color_str = text_format.get("font_color")
        text_color = QtGui.QColor(text_color_str)
        
        # Default alignment: center for both single-line and multi-line
        # Always use alignment from format if present, otherwise default to center
        align_str = text_format.get("alignment", "center")
        if is_singleline:
            if align_str == "left":
                alignment = Qt.AlignLeft
            elif align_str == "center":
                alignment = Qt.AlignHCenter
            elif align_str == "right":
                alignment = Qt.AlignRight
            else:
                alignment = Qt.AlignHCenter  # Default to center
        else:
            if align_str == "left":
                alignment = Qt.AlignLeft | Qt.TextWordWrap
            elif align_str == "center":
                alignment = Qt.AlignHCenter | Qt.TextWordWrap
            elif align_str == "right":
                alignment = Qt.AlignRight | Qt.TextWordWrap
            else:
                alignment = Qt.AlignHCenter | Qt.TextWordWrap  # Default to center
        
        element_bounds = QtCore.QRect(x, y, width, height)
        text_rect = QtCore.QRect(x, y, width, height)
        font_metrics = painter.fontMetrics()
        
        # Calculate actual text height using a temporary rect with very large height
        # This ensures we get the actual text height regardless of alignment
        temp_rect = QtCore.QRect(0, 0, width, 10000)
        text_bounding_rect = font_metrics.boundingRect(temp_rect, alignment, text_content)
        actual_text_height = text_bounding_rect.height()
        
        vertical_align = text_format.get("vertical_alignment", "middle")
        if vertical_align == "top":
            text_rect = QtCore.QRect(x, y, width, min(height, actual_text_height))
        elif vertical_align == "middle":
            offset_y = max(0, (height - actual_text_height) // 2)
            text_rect = QtCore.QRect(x, y + offset_y, width, min(height - offset_y, actual_text_height))
        elif vertical_align == "bottom":
            offset_y = max(0, height - actual_text_height)
            text_rect = QtCore.QRect(x, y + offset_y, width, min(height - offset_y, actual_text_height))
        
        # Ensure text_rect doesn't exceed element bounds
        text_rect = text_rect.intersected(element_bounds)
        # Only set clipping if element_rect is provided (not None) to avoid overriding animation clipping
        # When called from animation functions, element_rect is None, so we don't override the clipping set by animations
        if element_rect is not None:
            painter.setClipRect(element_bounds)
        
        text_bg_color_str = text_format.get("text_bg_color")
        if text_bg_color_str:
            text_bg_color = QtGui.QColor(text_bg_color_str)
            text_bounding_rect = font_metrics.boundingRect(
                text_rect, alignment, text_content
            )
            text_bg_rect = QtCore.QRect(
                text_bounding_rect.x(),
                text_bounding_rect.y(),
                text_bounding_rect.width(),
                text_bounding_rect.height()
            )
            painter.fillRect(text_bg_rect, text_bg_color)
        
        if text_format.get("outline"):
            outline_pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
            outline_pen.setWidth(3)
            painter.setPen(outline_pen)
            # Ensure outline text is also clipped
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_rect = QtCore.QRect(
                            text_rect.x() + dx,
                            text_rect.y() + dy,
                            text_rect.width(),
                            text_rect.height()
                        )
                        # Clip outline rect to element bounds
                        clipped_outline_rect = outline_rect.intersected(element_bounds)
                        if not clipped_outline_rect.isEmpty():
                            painter.drawText(clipped_outline_rect, alignment, text_content)
        
        painter.setPen(QtGui.QPen(text_color))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        painter.drawText(text_rect, alignment, text_content)
        # Only disable clipping if we set it (when element_rect is not None)
        if element_rect is not None:
            painter.setClipping(False)
    
    def _apply_text_entrance_animation(self, painter, text_content, text_format, element_props, x, y, width, height, anim_type, progress, scale, is_singleline=False):
        import random
        
        # Set clipping to element bounds to prevent text from displaying outside
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        # Available animations (excluding Random and Immediate Show)
        available_animations = [
            "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ]
        
        if is_singleline:
            available_animations.extend(["Continuous Move Left", "Continuous Move Right"])
        
        if anim_type == "Random":
            anim_type = random.choice(available_animations)
        
        if anim_type == "Immediate Show" or anim_type == "None":
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
            return
        
        painter.save()


        if is_singleline and anim_type == "Continuous Move Left":
            offset_x = int((1.0 - progress) * width)
            painter.translate(offset_x, 0)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        
        if is_singleline and anim_type == "Continuous Move Right":
            offset_x = int(-(1.0 - progress) * width)
            painter.translate(offset_x, 0)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        if anim_type == "Move Left":
            offset_x = int((1.0 - progress) * width)
            painter.translate(offset_x, 0)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Right":
            offset_x = int(-(1.0 - progress) * width)
            painter.translate(offset_x, 0)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Up":
            offset_y = int((1.0 - progress) * height)
            painter.translate(0, offset_y)
            painter.setClipRect(x, y - offset_y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Down":
            offset_y = int(-(1.0 - progress) * height)
            painter.translate(0, offset_y)
            painter.setClipRect(x, y - offset_y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Cover Left":
            clip_width = int(progress * width)
            painter.setClipRect(x, y, clip_width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Cover Right":
            clip_x = int(x + (1.0 - progress) * width)
            clip_width = int(progress * width)
            painter.setClipRect(clip_x, y, clip_width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Cover Up":
            clip_height = int(progress * height)
            painter.setClipRect(x, y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Cover Down":
            clip_y = int(y + (1.0 - progress) * height)
            clip_height = int(progress * height)
            painter.setClipRect(x, clip_y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Top Left Cover":
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            painter.setClipRect(x, y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Top Right Cover":
            clip_x = int(x + (1.0 - progress) * width)
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            painter.setClipRect(clip_x, y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Bottom Left Cover":
            clip_width = int(progress * width)
            clip_y = int(y + (1.0 - progress) * height)
            clip_height = int(progress * height)
            painter.setClipRect(x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Bottom Right Cover":
            clip_x = int(x + (1.0 - progress) * width)
            clip_width = int(progress * width)
            clip_y = int(y + (1.0 - progress) * height)
            clip_height = int(progress * height)
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Open From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Up Down Open":
            center_y = y + height // 2
            clip_height = int(progress * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Close From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Up Down Close":
            center_y = y + height // 2
            clip_height = int((1.0 - progress) * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Gradual Change":
            painter.setOpacity(progress)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setOpacity(1.0)
        elif anim_type == "Vertical Blinds":
            num_strips = 8
            strip_height = height / num_strips
            for i in range(num_strips):
                strip_y = y + i * strip_height
                if (i % 2 == 0 and progress > 0.5) or (i % 2 == 1 and progress <= 0.5):
                    clip_progress = min(1.0, progress * 2) if i % 2 == 0 else min(1.0, (progress - 0.5) * 2)
                    clip_height = int(clip_progress * strip_height)
                    painter.setClipRect(x, int(strip_y), width, clip_height)
                    self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
                    painter.setClipping(False)
        elif anim_type == "Horizontal Blinds":
            num_strips = 8
            strip_width = width / num_strips
            for i in range(num_strips):
                strip_x = x + i * strip_width
                if (i % 2 == 0 and progress > 0.5) or (i % 2 == 1 and progress <= 0.5):
                    clip_progress = min(1.0, progress * 2) if i % 2 == 0 else min(1.0, (progress - 0.5) * 2)
                    clip_width = int(clip_progress * strip_width)
                    painter.setClipRect(int(strip_x), y, clip_width, height)
                    self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
                    painter.setClipping(False)
        elif anim_type == "Twinkle":
            opacity = 0.5 + 0.5 * abs((progress * 4) % 2 - 1)
            painter.setOpacity(opacity)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setOpacity(1.0)
        else:
            painter.setOpacity(progress)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setOpacity(1.0)
        
        painter.restore()
        painter.setClipping(False)
    
    def _apply_text_exit_animation(self, painter, text_content, text_format, element_props, x, y, width, height, anim_type, progress, scale, is_singleline=False):
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        if anim_type == "Immediate Clear" or anim_type == "None" or (is_singleline and anim_type == "Don't Clear Screen"):
            painter.setClipping(False)
            return
        
        painter.save()
        
        if anim_type == "Move Left":
            offset_x = int(-progress * width)
            painter.translate(offset_x, 0)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Right":
            offset_x = int(progress * width)
            painter.translate(offset_x, 0)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Up":
            offset_y = int(-progress * height)
            painter.translate(0, offset_y)
            painter.setClipRect(x, y - offset_y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Down":
            offset_y = int(progress * height)
            painter.translate(0, offset_y)
            painter.setClipRect(x, y - offset_y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Cover Left":
            clip_width = int((1.0 - progress) * width)
            painter.setClipRect(x, y, clip_width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Cover Right":
            clip_x = int(x + progress * width)
            clip_width = int((1.0 - progress) * width)
            painter.setClipRect(clip_x, y, clip_width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Cover Up":
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Cover Down":
            clip_y = int(y + progress * height)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, clip_y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Top Left Cover":
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Top Right Cover":
            clip_x = int(x + progress * width)
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(clip_x, y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Bottom Left Cover":
            clip_width = int((1.0 - progress) * width)
            clip_y = int(y + progress * height)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Bottom Right Cover":
            clip_x = int(x + progress * width)
            clip_width = int((1.0 - progress) * width)
            clip_y = int(y + progress * height)
            clip_height = int((1.0 - progress) * height)
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Open From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int((1.0 - progress) * width)
            clip_height = int((1.0 - progress) * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Up Down Open":
            center_y = y + height // 2
            clip_height = int((1.0 - progress) * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Close From Middle":
            center_x = x + width // 2
            center_y = y + height // 2
            clip_width = int(progress * width)
            clip_height = int(progress * height)
            clip_x = center_x - clip_width // 2
            clip_y = center_y - clip_height // 2
            painter.setClipRect(clip_x, clip_y, clip_width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Up Down Close":
            center_y = y + height // 2
            clip_height = int(progress * height)
            clip_y = center_y - clip_height // 2
            painter.setClipRect(x, clip_y, width, clip_height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
        elif anim_type == "Gradual Change":
            painter.setOpacity(1.0 - progress)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setOpacity(1.0)
        elif anim_type == "Vertical Blinds":
            num_strips = 8
            strip_height = height / num_strips
            for i in range(num_strips):
                strip_y = y + i * strip_height
                if (i % 2 == 0 and progress > 0.5) or (i % 2 == 1 and progress <= 0.5):
                    clip_progress = min(1.0, progress * 2) if i % 2 == 0 else min(1.0, (progress - 0.5) * 2)
                    clip_height = int((1.0 - clip_progress) * strip_height)
                    painter.setClipRect(x, int(strip_y), width, clip_height)
                    self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
                    painter.setClipping(False)
        elif anim_type == "Horizontal Blinds":
            num_strips = 8
            strip_width = width / num_strips
            for i in range(num_strips):
                strip_x = x + i * strip_width
                if (i % 2 == 0 and progress > 0.5) or (i % 2 == 1 and progress <= 0.5):
                    clip_progress = min(1.0, progress * 2) if i % 2 == 0 else min(1.0, (progress - 0.5) * 2)
                    clip_width = int((1.0 - clip_progress) * strip_width)
                    painter.setClipRect(int(strip_x), y, clip_width, height)
                    self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
                    painter.setClipping(False)
        elif anim_type == "Twinkle":
            opacity = 0.5 + 0.5 * abs((progress * 4) % 2 - 1)
            painter.setOpacity(opacity)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setOpacity(1.0)
        else:
            painter.setOpacity(1.0 - progress)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setOpacity(1.0)
        
        painter.restore()
        painter.setClipping(False)
    
    def _update_animations(self):
        if self._photo_animations or self._text_animations or self._text_flow_animations:
            self.update()
    
    def _get_current_program_elements(self):
        if not self.screen_manager or not self.screen_manager.current_screen:
            return []
        
        if not self.screen_manager.current_screen.programs:
            return []
        
        program = self.screen_manager.current_screen.programs[0]
        return program.elements
    
    def _calculate_scale(self, screen_width: int, screen_height: int) -> float:
        available_width = self.width()
        available_height = self.height()
        
        if screen_width <= 0 or screen_height <= 0:
            return 1.0
        
        scale_x = available_width / screen_width
        scale_y = available_height / screen_height
        return min(scale_x, scale_y)
    
    def _draw_element(self, painter, element, screen_x, screen_y, scale):
        element_type = element.get("type", "")
        element_props = element.get("properties", {})
        
        x = element_props.get("x", element.get("x", 0))
        y = element_props.get("y", element.get("y", 0))
        width = element_props.get("width", element.get("width", 100))
        height = element_props.get("height", element.get("height", 100))
        
        scaled_x = int(screen_x + (x * scale))
        scaled_y = int(screen_y + (y * scale))
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)
        
        if scaled_width <= 0 or scaled_height <= 0:
            return
        
        element_rect = QtCore.QRect(scaled_x, scaled_y, scaled_width, scaled_height)
        element_id = element.get("id", "")
        is_selected = element_id == self.selected_element_id
        
        if element_type == "video":
            video_list = element_props.get("video_list", [])
            if video_list and len(video_list) > 0:
                active_index = self._get_video_active_index(element_id, video_list)
                if 0 <= active_index < len(video_list):
                    video_path = video_list[active_index].get("path", "")
                    if video_path:
                        self._setup_video_player(element_id, video_path)
            
            if element_id in self._video_frames and self._video_frames[element_id]:
                pixmap = self._video_frames[element_id]
                if not pixmap.isNull():
                    fit_mode = element_props.get("fit_mode", "Keep Aspect Ratio")
                    aspect_ratio_mode = Qt.IgnoreAspectRatio if fit_mode == "Stretch" else Qt.KeepAspectRatio
                    scaled_pixmap = pixmap.scaled(scaled_width, scaled_height, aspect_ratio_mode, Qt.SmoothTransformation)
                    if fit_mode == "Stretch":
                        pixmap_x = scaled_x
                        pixmap_y = scaled_y
                    else:
                        pixmap_x = scaled_x + (scaled_width - scaled_pixmap.width()) // 2
                        pixmap_y = scaled_y + (scaled_height - scaled_pixmap.height()) // 2
                    painter.drawPixmap(pixmap_x, pixmap_y, scaled_pixmap)
                    if is_selected:
                        painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                        painter.drawRect(element_rect)
                    return
            
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "VIDEO")
        elif element_type == "photo":
            if ('photo', element_id) not in self._media_order:
                self._media_order.append(('photo', element_id))
            photo_list = element_props.get("photo_list", element_props.get("image_list", []))
            if photo_list and len(photo_list) > 0:
                active_index = self._get_photo_active_index(element_id, photo_list)
                if 0 <= active_index < len(photo_list):
                    photo_path = photo_list[active_index].get("path", "")
                    if photo_path:
                        try:
                            from pathlib import Path
                            if Path(photo_path).exists():
                                pixmap = QtGui.QPixmap(photo_path)
                                if not pixmap.isNull():
                                    animation_props = element_props.get("animation", {})
                                    self._draw_photo_with_animation(
                                        painter, pixmap, scaled_x, scaled_y, scaled_width, scaled_height,
                                        element_id, animation_props, element_rect, is_selected
                                    )
                                    return
                        except Exception:
                            pass
            
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "PHOTO")
        elif element_type == "text":
            if ('text', element_id) not in self._media_order:
                self._media_order.append(('text', element_id))
            text_props = element_props.get("text", {})
            if isinstance(text_props, dict):
                text_content = text_props.get("content", "")
                # Also check for play_text (base64 encoded) and html
                if not text_content:
                    text_content = text_props.get("html", "")
                if not text_content and text_props.get("play_text"):
                    import base64
                    try:
                        text_content = base64.b64decode(text_props.get("play_text", "")).decode('utf-8')
                    except Exception:
                        pass
                text_format = text_props.get("format", {})
            else:
                text_content = str(text_props) if text_props else ""
                text_format = {}
            
            if text_content and text_content.strip():
                animation_props = element_props.get("animation", {})
                self._draw_text_with_animation(
                    painter, text_content, text_format, element_props,
                    scaled_x, scaled_y, scaled_width, scaled_height,
                    element_id, animation_props, element_rect, is_selected, scale, is_singleline=False
                )
            else:
                painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100), 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
                painter.drawRect(element_rect)
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
                painter.drawText(element_rect, Qt.AlignCenter, "TEXT")
                if is_selected:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                    painter.drawRect(element_rect)
        elif element_type == "singleline_text":
            if ('text', element_id) not in self._media_order:
                self._media_order.append(('text', element_id))
            text_props = element_props.get("text", {})
            if isinstance(text_props, dict):
                text_content = text_props.get("content", "")
                text_format = text_props.get("format", {})
            else:
                text_content = str(text_props) if text_props else ""
                text_format = {}
            
            if text_content:
                animation_props = element_props.get("animation", {})
                self._draw_text_with_animation(
                    painter, text_content, text_format, element_props,
                    scaled_x, scaled_y, scaled_width, scaled_height,
                    element_id, animation_props, element_rect, is_selected, scale, is_singleline=True
                )
            else:
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 255) if is_selected else QtGui.QColor(100, 100, 100), 2))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
                painter.drawRect(element_rect)
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
                painter.drawText(element_rect, Qt.AlignCenter, "TEXT")
                if is_selected:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                    painter.drawRect(element_rect)
        elif element_type == "animation":
            self._draw_text_animation(painter, element_props, scaled_x, scaled_y, scaled_width, scaled_height, element_rect, is_selected, element_id, scale)
        elif element_type == "clock":
            self._draw_clock(painter, element_props, scaled_x, scaled_y, scaled_width, scaled_height, element_rect, is_selected)
        elif element_type == "timing":
            self._draw_timing(painter, element_props, scaled_x, scaled_y, scaled_width, scaled_height, element_rect, is_selected, element_id, scale)
        elif element_type == "weather":
            painter.setPen(QtGui.QPen(QtGui.QColor(135, 206, 250) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "WEATHER")
        elif element_type == "sensor":
            self._draw_sensor(painter, element_props, scaled_x, scaled_y, scaled_width, scaled_height, element_rect, is_selected, scale)
        elif element_type == "html":
            self._setup_html_widget(painter, element_props, scaled_x, scaled_y, scaled_width, scaled_height, element_rect, is_selected, element_id, scale)
        elif element_type == "hdmi":
            self._setup_hdmi_widget(painter, element_props, scaled_x, scaled_y, scaled_width, scaled_height, element_rect, is_selected, element_id, scale)
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, element_type.upper() if element_type else "ELEMENT")
    
    def _draw_clock(self, painter, element_props, x, y, width, height, element_rect, is_selected):
        """Draw clock based on clock type"""
        from datetime import datetime
        import math
        
        clock_props = element_props.get("clock", {})
        clock_type = clock_props.get("type", "System")
        timezone = clock_props.get("timezone", "Local")
        correction = clock_props.get("correction", 0)
        
        # Get current time with timezone and correction
        now = datetime.now()
        if timezone != "Local":
            # Simple timezone handling (can be improved)
            if timezone.startswith("GMT+"):
                offset = int(timezone[4:])
                from datetime import timedelta
                now = now + timedelta(hours=offset)
            elif timezone.startswith("GMT-"):
                offset = int(timezone[4:])
                from datetime import timedelta
                now = now - timedelta(hours=offset)
        
        if correction != 0:
            from datetime import timedelta
            now = now + timedelta(seconds=correction)
        
        center_x = x + width // 2
        center_y = y + height // 2
        radius = min(width, height) // 2 - 10
        
        if clock_type == "System":
            self._draw_system_clock(painter, clock_props, now, center_x, center_y, radius, x, y, width, height, element_rect, is_selected)
        elif clock_type == "Analog":
            self._draw_analog_clock(painter, clock_props, now, center_x, center_y, radius, x, y, width, height, element_rect, is_selected)
        elif clock_type == "Digital":
            self._draw_digital_clock(painter, clock_props, now, x, y, width, height, element_rect, is_selected)
        else:
            # Default: draw placeholder
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 192, 203) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "CLOCK")
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
            painter.drawRect(element_rect)
    
    def _draw_system_clock(self, painter, clock_props, now, center_x, center_y, radius, x, y, width, height, element_rect, is_selected):
        import math
        
        # Set clipping to element bounds to prevent content from displaying outside
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        system_props = clock_props.get("system", {})
        font_family = system_props.get("font_family", "Arial")
        font_size = system_props.get("font_size", 24)
        
        # Draw analog clock face (no numbers, only face and hands) - transparent background
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))  # Transparent
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Draw hour scale
        hour_scale_shape = system_props.get("hour_scale_shape", "straight line")
        hour_scale_color = QtGui.QColor(system_props.get("hour_scale_color", "#FF0000"))  # Default red
        painter.setPen(QtGui.QPen(hour_scale_color, 2))
        
        for hour in range(12):
            angle = math.radians(hour * 30 - 90)
            start_x = center_x + (radius - 20) * math.cos(angle)
            start_y = center_y + (radius - 20) * math.sin(angle)
            end_x = center_x + (radius - 5) * math.cos(angle)
            end_y = center_y + (radius - 5) * math.sin(angle)
            
            if hour_scale_shape == "round":
                painter.drawEllipse(int(end_x) - 3, int(end_y) - 3, 6, 6)
            elif hour_scale_shape == "rectangle":
                painter.drawRect(int(end_x) - 3, int(end_y) - 3, 6, 6)
            elif hour_scale_shape == "all numbers":
                font = painter.font()
                font.setPointSize(12)
                painter.setFont(font)
                text_x = center_x + (radius - 30) * math.cos(angle) - 5
                text_y = center_y + (radius - 30) * math.sin(angle) + 5
                painter.drawText(int(text_x), int(text_y), str(hour + 1 if hour < 11 else 12))
            elif hour_scale_shape == "digital":
                if hour in [2, 5, 8, 11]:  # 3, 6, 9, 12
                    font = painter.font()
                    font.setPointSize(12)
                    painter.setFont(font)
                    text_x = center_x + (radius - 30) * math.cos(angle) - 5
                    text_y = center_y + (radius - 30) * math.sin(angle) + 5
                    painter.drawText(int(text_x), int(text_y), str(hour + 1 if hour < 11 else 12))
            else:  # straight line
                painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
        
        # Draw minute scale
        minute_scale_shape = system_props.get("minute_scale_shape", "round")
        minute_scale_color = QtGui.QColor(system_props.get("minute_scale_color", "#00FF00"))  # Default green
        painter.setPen(QtGui.QPen(minute_scale_color, 1))
        
        if minute_scale_shape != "air":
            for minute in range(60):
                if minute % 5 != 0:  # Skip hour marks
                    angle = math.radians(minute * 6 - 90)
                    start_x = center_x + (radius - 10) * math.cos(angle)
                    start_y = center_y + (radius - 10) * math.sin(angle)
                    end_x = center_x + (radius - 5) * math.cos(angle)
                    end_y = center_y + (radius - 5) * math.sin(angle)
                    
                    if minute_scale_shape == "round":
                        painter.drawEllipse(int(end_x) - 2, int(end_y) - 2, 4, 4)
                    elif minute_scale_shape == "rectangle":
                        painter.drawRect(int(end_x) - 2, int(end_y) - 2, 4, 4)
                    else:  # straight line
                        painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
        
        # Draw hands
        hour_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)
        minute_angle = math.radians(now.minute * 6 + now.second * 0.1 - 90)
        second_angle = math.radians(now.second * 6 - 90)
        
        # Hour hand
        hour_hand_shape = system_props.get("hour_hand_shape", "rectangle")
        hour_hand_color = QtGui.QColor(system_props.get("hour_hand_color", "#FF0000"))  # Default red
        if hour_hand_shape != "air":
            hour_length = radius * 0.5
            hour_x = center_x + hour_length * math.cos(hour_angle)
            hour_y = center_y + hour_length * math.sin(hour_angle)
            painter.setPen(QtGui.QPen(hour_hand_color, 4))
            if hour_hand_shape == "polygon":
                # Draw rhombus
                points = [
                    QtCore.QPoint(int(center_x), int(center_y)),
                    QtCore.QPoint(int(hour_x + 5 * math.cos(hour_angle + math.pi/2)), int(hour_y + 5 * math.sin(hour_angle + math.pi/2))),
                    QtCore.QPoint(int(hour_x), int(hour_y)),
                    QtCore.QPoint(int(hour_x + 5 * math.cos(hour_angle - math.pi/2)), int(hour_y + 5 * math.sin(hour_angle - math.pi/2)))
                ]
                painter.drawPolygon(points)
            else:  # rectangle
                painter.drawLine(int(center_x), int(center_y), int(hour_x), int(hour_y))
        
        # Minute hand
        minute_hand_shape = system_props.get("minute_hand_shape", "rectangle")
        minute_hand_color = QtGui.QColor(system_props.get("minute_hand_color", "#00FF00"))  # Default green
        if minute_hand_shape != "air":
            minute_length = radius * 0.7
            minute_x = center_x + minute_length * math.cos(minute_angle)
            minute_y = center_y + minute_length * math.sin(minute_angle)
            painter.setPen(QtGui.QPen(minute_hand_color, 3))
            if minute_hand_shape == "polygon":
                points = [
                    QtCore.QPoint(int(center_x), int(center_y)),
                    QtCore.QPoint(int(minute_x + 4 * math.cos(minute_angle + math.pi/2)), int(minute_y + 4 * math.sin(minute_angle + math.pi/2))),
                    QtCore.QPoint(int(minute_x), int(minute_y)),
                    QtCore.QPoint(int(minute_x + 4 * math.cos(minute_angle - math.pi/2)), int(minute_y + 4 * math.sin(minute_angle - math.pi/2)))
                ]
                painter.drawPolygon(points)
            else:  # rectangle
                painter.drawLine(int(center_x), int(center_y), int(minute_x), int(minute_y))
        
        # Second hand
        second_hand_shape = system_props.get("second_hand_shape", "rectangle")
        second_hand_color = QtGui.QColor(system_props.get("second_hand_color", "#0000FF"))  # Default blue
        if second_hand_shape != "air":
            second_length = radius * 0.8
            second_x = center_x + second_length * math.cos(second_angle)
            second_y = center_y + second_length * math.sin(second_angle)
            painter.setPen(QtGui.QPen(second_hand_color, 2))
            if second_hand_shape == "polygon":
                points = [
                    QtCore.QPoint(int(center_x), int(center_y)),
                    QtCore.QPoint(int(second_x + 3 * math.cos(second_angle + math.pi/2)), int(second_y + 3 * math.sin(second_angle + math.pi/2))),
                    QtCore.QPoint(int(second_x), int(second_y)),
                    QtCore.QPoint(int(second_x + 3 * math.cos(second_angle - math.pi/2)), int(second_y + 3 * math.sin(second_angle - math.pi/2)))
                ]
                painter.drawPolygon(points)
            else:  # rectangle
                painter.drawLine(int(center_x), int(center_y), int(second_x), int(second_y))
        
        # Draw center dot
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 255), 2))  # Blue
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 255)))  # Blue
        painter.drawEllipse(center_x - 5, center_y - 5, 10, 10)
        
        # Draw digital time below analog clock
        digital_y = center_y + radius + 30
        font = QtGui.QFont(font_family, font_size)
        painter.setFont(font)
        
        # Draw time (always enabled, 24 hour format)
        time_str = now.strftime("%H:%M:%S")
        time_color = QtGui.QColor(system_props.get("time_color", "#000000"))
        
        # Draw AM/PM if enabled
        noon_str = ""
        if system_props.get("noon_enabled", False):
            # Check if current time is before noon (AM) or afternoon/evening (PM)
            # 0-11 hours = AM, 12-23 hours = PM
            if now.hour < 12:
                noon_str = " AM"
            else:
                noon_str = " PM"
            noon_color = QtGui.QColor(system_props.get("noon_color", "#0000FF"))  # Default blue
            # Draw time with AM/PM - ensure it stays within bounds
            painter.setPen(QtGui.QPen(time_color))
            available_height = min(height - (digital_y - y), font_size + 10)
            if available_height > 0 and digital_y < y + height:
                text_rect = QtCore.QRect(x, digital_y, width, available_height)
                painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, time_str)
                # Draw AM/PM with its own color - ensure it stays within bounds
                painter.setPen(QtGui.QPen(noon_color))
                time_width = painter.fontMetrics().width(time_str)
                noon_x = x + width // 2 + time_width // 2
                if noon_x < x + width:
                    noon_rect = QtCore.QRect(noon_x, digital_y, x + width - noon_x, available_height)
                    painter.drawText(noon_rect, Qt.AlignLeft | Qt.AlignTop, noon_str)
        else:
            # Draw time without AM/PM - ensure it stays within bounds
            available_height = min(height - (digital_y - y), font_size + 10)
            if available_height > 0 and digital_y < y + height:
                painter.setPen(QtGui.QPen(time_color))
                text_rect = QtCore.QRect(x, digital_y, width, available_height)
                painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, time_str)
        
        digital_y += font_size + 5
        
        # Draw additional info if enabled - centered in the area
        info_items = []
        
        if system_props.get("title_enabled", False):
            title_value = system_props.get("title_value", "Clock")
            title_color = QtGui.QColor(system_props.get("title_color", "#0000FF"))  # Default blue
            info_items.append((title_value, title_color))
        
        if system_props.get("date_enabled", False):
            date_format = system_props.get("date_format", "YYYY-MM-DD")
            if date_format == "MM/DD/YYYY":
                date_str = now.strftime("%m/%d/%Y")
            elif date_format == "DD/MM/YYYY":
                date_str = now.strftime("%d/%m/%Y")
            elif date_format == "YYYY/MM/DD":
                date_str = now.strftime("%Y/%m/%d")
            else:  # YYYY-MM-DD
                date_str = now.strftime("%Y-%m-%d")
            date_color = QtGui.QColor(system_props.get("date_color", "#0000FF"))  # Default blue
            info_items.append((date_str, date_color))
        
        if system_props.get("week_enabled", False):
            week_format = system_props.get("week_format", "Full Name")
            weekdays_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekdays_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            weekday_num = now.weekday()
            if week_format == "Short Name":
                week_str = weekdays_short[weekday_num]
            elif week_format == "Number":
                week_str = str(weekday_num + 1)
            else:  # Full Name
                week_str = weekdays_full[weekday_num]
            week_color = QtGui.QColor(system_props.get("week_color", "#00FF00"))  # Default green
            info_items.append((week_str, week_color))
        
        # Calculate center position for title, date, week
        if info_items:
            total_info_height = len(info_items) * (font_size + 5) - 5  # Total height of all info items
            # Center vertically in the entire element area
            center_y_pos = y + height // 2
            start_y = center_y_pos - total_info_height // 2
            
            for i, (line, color) in enumerate(info_items):
                line_y = start_y + i * (font_size + 5)
                # Ensure text doesn't go outside element bounds
                if line_y >= y and line_y + font_size <= y + height:
                    painter.setPen(QtGui.QPen(color))
                    text_rect = QtCore.QRect(x, line_y, width, min(font_size + 5, y + height - line_y))
                    painter.drawText(text_rect, Qt.AlignCenter, line)
        
        painter.setClipping(False)
    
    def _draw_analog_clock(self, painter, clock_props, now, center_x, center_y, radius, x, y, width, height, element_rect, is_selected):
        """Draw analog clock using images"""
        import math
        from pathlib import Path
        
        # Set clipping to element bounds to prevent content from displaying outside
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        analog_props = clock_props.get("analog", {})
        
        # Draw dial plate
        dial_plate_path = analog_props.get("dial_plate", "")
        if dial_plate_path and Path(dial_plate_path).exists():
            dial_pixmap = QtGui.QPixmap(dial_plate_path)
            if not dial_pixmap.isNull():
                scaled_dial = dial_pixmap.scaled(radius * 2, radius * 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(center_x - scaled_dial.width() // 2, center_y - scaled_dial.height() // 2, scaled_dial)
        
        # Calculate angles
        hour_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)
        minute_angle = math.radians(now.minute * 6 + now.second * 0.1 - 90)
        second_angle = math.radians(now.second * 6 - 90)
        
        # Draw hour hand
        hour_hand_path = analog_props.get("hour_hand", "")
        if hour_hand_path and Path(hour_hand_path).exists():
            hour_pixmap = QtGui.QPixmap(hour_hand_path)
            if not hour_pixmap.isNull():
                scaled_hour = hour_pixmap.scaled(radius, radius, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.save()
                painter.translate(center_x, center_y)
                painter.rotate(math.degrees(hour_angle) + 90)
                painter.drawPixmap(-scaled_hour.width() // 2, -scaled_hour.height() // 2, scaled_hour)
                painter.restore()
        
        # Draw minute hand
        minute_hand_path = analog_props.get("minute_hand", "")
        if minute_hand_path and Path(minute_hand_path).exists():
            minute_pixmap = QtGui.QPixmap(minute_hand_path)
            if not minute_pixmap.isNull():
                scaled_minute = minute_pixmap.scaled(radius, radius, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.save()
                painter.translate(center_x, center_y)
                painter.rotate(math.degrees(minute_angle) + 90)
                painter.drawPixmap(-scaled_minute.width() // 2, -scaled_minute.height() // 2, scaled_minute)
                painter.restore()
        
        # Draw second hand
        second_hand_path = analog_props.get("second_hand", "")
        if second_hand_path and Path(second_hand_path).exists():
            second_pixmap = QtGui.QPixmap(second_hand_path)
            if not second_pixmap.isNull():
                scaled_second = second_pixmap.scaled(radius, radius, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.save()
                painter.translate(center_x, center_y)
                painter.rotate(math.degrees(second_angle) + 90)
                painter.drawPixmap(-scaled_second.width() // 2, -scaled_second.height() // 2, scaled_second)
                painter.restore()
        
        painter.setClipping(False)
    
    def _draw_digital_clock(self, painter, clock_props, now, x, y, width, height, element_rect, is_selected):
        """Draw digital clock"""
        # Set clipping to element bounds to prevent content from displaying outside
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        digital_props = clock_props.get("digital", {})
        font_family = digital_props.get("font_family", "Arial")
        font_size = digital_props.get("font_size", 24)
        line_setting = digital_props.get("line_setting", "Single Line")
        
        font = QtGui.QFont(font_family, font_size)
        painter.setFont(font)
        
        lines = []
        
        # Title first
        if digital_props.get("title_enabled", False):
            title_value = digital_props.get("title_value", "Clock")
            title_color = QtGui.QColor(digital_props.get("title_color", "#FF0000"))  # Default red
            lines.append((title_value, title_color))
        
        # Time
        if digital_props.get("time_enabled", True):
            time_format = digital_props.get("time_format", "HH:MM:SS")
            if time_format == "HH:MM":
                time_str = now.strftime("%H:%M")
            elif time_format == "12 Hour":
                time_str = now.strftime("%I:%M:%S %p")
            else:  # Default to "HH:MM:SS"
                time_str = now.strftime("%H:%M:%S")
            time_color = QtGui.QColor(digital_props.get("time_color", "#FF0000"))  # Default red
            lines.append((time_str, time_color))
        
        # Additional info
        if digital_props.get("date_enabled", False):
            date_format = digital_props.get("date_format", "YYYY-MM-DD")
            if date_format == "MM/DD/YYYY":
                date_str = now.strftime("%m/%d/%Y")
            elif date_format == "DD/MM/YYYY":
                date_str = now.strftime("%d/%m/%Y")
            elif date_format == "YYYY/MM/DD":
                date_str = now.strftime("%Y/%m/%d")
            else:  # YYYY-MM-DD
                date_str = now.strftime("%Y-%m-%d")
            date_color = QtGui.QColor(digital_props.get("date_color", "#0000FF"))  # Default blue
            lines.append((date_str, date_color))
        
        if digital_props.get("week_enabled", False):
            week_format = digital_props.get("week_format", "Full Name")
            weekdays_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekdays_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            weekday_num = now.weekday()
            if week_format == "Short Name":
                week_str = weekdays_short[weekday_num]
            elif week_format == "Number":
                week_str = str(weekday_num + 1)
            else:  # Full Name
                week_str = weekdays_full[weekday_num]
            week_color = QtGui.QColor(digital_props.get("week_color", "#00FF00"))  # Default green
            lines.append((week_str, week_color))
        
        if line_setting == "Single Line":
            # Draw each part with its own color
            if not lines:
                return
            
            # Calculate total width and positions for centering
            font_metrics = painter.fontMetrics()
            separator = " | "
            separator_width = font_metrics.width(separator)
            
            # Calculate total width
            total_width = 0
            for i, (line, color) in enumerate(lines):
                total_width += font_metrics.width(line)
                if i < len(lines) - 1:
                    total_width += separator_width
            
            # Start position (centered)
            start_x = x + (width - total_width) // 2
            current_x = start_x
            
            # Draw each part with its own color
            for i, (line, color) in enumerate(lines):
                painter.setPen(QtGui.QPen(color))
                text_rect = QtCore.QRect(current_x, y, font_metrics.width(line), height)
                painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, line)
                current_x += font_metrics.width(line)
                
                # Draw separator if not last
                if i < len(lines) - 1:
                    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))  # Black separator
                    separator_rect = QtCore.QRect(current_x, y, separator_width, height)
                    painter.drawText(separator_rect, Qt.AlignLeft | Qt.AlignVCenter, separator)
                    current_x += separator_width
        else:
            # Multi-line with individual colors
            line_height = font_size + 5
            start_y = y + (height - len(lines) * line_height) // 2
            for i, (line, color) in enumerate(lines):
                line_y = start_y + i * line_height
                # Ensure text doesn't go outside element bounds
                if line_y >= y and line_y + font_size <= y + height:
                    painter.setPen(QtGui.QPen(color))
                    text_rect = QtCore.QRect(x, line_y, width, min(line_height, y + height - line_y))
                    painter.drawText(text_rect, Qt.AlignCenter, line)
        
        painter.setClipping(False)
    
    def _draw_text_animation(self, painter, element_props, x, y, width, height, element_rect, is_selected, element_id, scale):
        """Draw animated text with gradient colors and character-by-character movement"""
        import math
        from datetime import datetime
        
        text_props = element_props.get("text", {})
        if not isinstance(text_props, dict):
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 165, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "ANIM")
            if is_selected:
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                painter.drawRect(element_rect)
            return
        
        text_content = text_props.get("content", "")
        if not text_content:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 165, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "ANIM")
            if is_selected:
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                painter.drawRect(element_rect)
            return
        
        text_format = text_props.get("format", {})
        animation_style = element_props.get("animation_style", {})
        
        if element_id not in self._text_flow_animations:
            self._text_flow_animations[element_id] = {
                "start_time": QtCore.QDateTime.currentDateTime()
            }
            if not self._animation_timer.isActive():
                self._animation_timer.start()
        
        anim_state = self._text_flow_animations[element_id]
        
        style_index = animation_style.get("style_index", 0)
        hold_time = animation_style.get("hold_time", 6.0)
        speed = animation_style.get("speed", 5)
        
        from ui.utils import animation_effects
        import math
        
        font = painter.font()
        font_size = element_props.get("font_size", 24)
        if text_format.get("font_size"):
            font_size = text_format.get("font_size", font_size)
        font.setPointSize(max(8, int(font_size * scale)))
        
        if text_format.get("font_family"):
            font.setFamily(text_format.get("font_family"))
        if text_format.get("bold"):
            font.setBold(True)
        if text_format.get("italic"):
            font.setItalic(True)
        if text_format.get("underline"):
            font.setUnderline(True)
        painter.setFont(font)
        
        char_spacing = text_format.get("char_spacing", 0)
        
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        font_metrics = painter.fontMetrics()
        current_x = x
        current_y = y + font_metrics.ascent()
        
        elapsed_ms = anim_state["start_time"].msecsTo(QtCore.QDateTime.currentDateTime())
        elapsed_sec = elapsed_ms / 1000.0
        
        text_length = len(text_content)
        char_positions = []
        current_pos_x = x
        current_pos_y = y + font_metrics.ascent()
        
        for char in text_content:
            char_width = font_metrics.width(char)
            char_positions.append((current_pos_x, current_pos_y, char_width))
            current_pos_x += char_width + char_spacing
            if current_pos_x + char_width > x + width:
                current_pos_x = x
                current_pos_y += font_metrics.height()
        
        if char_positions:
            min_x = min(pos[0] for pos in char_positions)
            max_x = max(pos[0] + pos[2] for pos in char_positions)
            min_y = min(pos[1] for pos in char_positions)
            max_y = max(pos[1] + font_metrics.height() for pos in char_positions)
            text_width = max_x - min_x
            text_height = max_y - min_y
            text_center_x = min_x + text_width / 2
            text_center_y = min_y + text_height / 2
        else:
            text_width = 0
            text_height = font_metrics.height()
            text_center_x = x + width / 2
            text_center_y = y + height / 2
        
        is_continuous_scroll = style_index in [0, 1, 2, 3]
        
        if is_continuous_scroll:
            if style_index == 0 or style_index == 1:
                vertical_align = text_format.get("vertical_alignment", "middle")
                line_height = font_metrics.height()
                ascent = font_metrics.ascent()
                descent = font_metrics.descent()
                
                if vertical_align == "top":
                    vertical_offset = 0
                elif vertical_align == "middle":
                    vertical_offset = (height - text_height) / 2
                else:
                    vertical_offset = height - text_height
                
                scroll_speed = speed * 10
                scroll_offset = (elapsed_sec * scroll_speed) % text_width
                
                num_repeats = max(3, int((width + text_width) / max(text_width, 1)) + 2)
                start_offset = -text_width
                
                for repeat_idx in range(num_repeats):
                    if style_index == 0:
                        text_offset_x = start_offset + (repeat_idx * text_width) - scroll_offset
                    else:
                        text_offset_x = start_offset + (repeat_idx * text_width) + scroll_offset
                    
                    if text_offset_x + text_width < x - text_width or text_offset_x > x + width + text_width:
                        continue
                    
                    for i, char in enumerate(text_content):
                        char_x_base, char_y_base, char_width = char_positions[i]
                        char_height = font_metrics.height()
                        
                        draw_x = int(text_offset_x + (char_x_base - min(pos[0] for pos in char_positions)))
                        draw_y = int(y + vertical_offset + (char_y_base - min(pos[1] for pos in char_positions)) + ascent)
                        
                        draw_y = max(y + ascent, min(draw_y, y + height - descent))
                        
                        if draw_x + char_width < x or draw_x > x + width:
                            continue
                        
                        color = animation_effects.get_animation_color(style_index, i, text_length, elapsed_sec)
                        
                        painter.save()
                        painter.setPen(QtGui.QPen(color))
                        painter.setOpacity(1.0)
                        
                        if text_format.get("hollow", False):
                            outline_pen = QtGui.QPen(color, 2)
                            painter.setPen(outline_pen)
                            for ddx in [-1, 0, 1]:
                                for ddy in [-1, 0, 1]:
                                    if ddx != 0 or ddy != 0:
                                        painter.drawText(draw_x + ddx, draw_y + ddy, char)
                            painter.setPen(QtGui.QPen(color))
                        painter.drawText(draw_x, draw_y, char)
                        painter.restore()
            
            if style_index == 2 or style_index == 3:
                vertical_char_width = max(font_metrics.width(char) for char in text_content) if text_content else font_metrics.width("A")
                vertical_text_height = sum(font_metrics.height() for _ in text_content) if text_content else font_metrics.height()
                
                alignment = text_format.get("alignment", "center")
                ascent = font_metrics.ascent()
                descent = font_metrics.descent()
                
                if alignment == "left":
                    horizontal_offset = 0
                elif alignment == "right":
                    horizontal_offset = width - vertical_char_width
                else:
                    horizontal_offset = (width - vertical_char_width) / 2
                
                vertical_base_x = x + horizontal_offset
                vertical_base_y = y
                
                scroll_speed = speed * 10
                scroll_offset = (elapsed_sec * scroll_speed) % max(vertical_text_height, 1)
                
                num_repeats = max(3, int((height + vertical_text_height) / max(vertical_text_height, 1)) + 2)
                start_offset = -vertical_text_height
                
                char_heights = []
                current_y = 0
                for char in text_content:
                    char_height = font_metrics.height()
                    char_heights.append((current_y, char_height))
                    current_y += char_height
                
                for repeat_idx in range(num_repeats):
                    if style_index == 2:
                        text_offset_y = start_offset + (repeat_idx * vertical_text_height) - scroll_offset
                    else:
                        text_offset_y = start_offset + (repeat_idx * vertical_text_height) + scroll_offset
                    
                    if text_offset_y + vertical_text_height < y - vertical_text_height or text_offset_y > y + height + vertical_text_height:
                        continue
                    
                    for i, char in enumerate(text_content):
                        char_y_offset, char_height = char_heights[i]
                        char_width = font_metrics.width(char)
                        
                        draw_x = int(vertical_base_x + (vertical_char_width - char_width) / 2)
                        draw_y = int(vertical_base_y + text_offset_y + char_y_offset + ascent)
                        
                        draw_y = max(y + ascent, min(draw_y, y + height - descent))
                        
                        if draw_y + char_height < y or draw_y > y + height:
                            continue
                        
                        color = animation_effects.get_animation_color(style_index, i, text_length, elapsed_sec)
                        
                        painter.save()
                        painter.setPen(QtGui.QPen(color))
                        painter.setOpacity(1.0)
                        
                        if text_format.get("hollow", False):
                            outline_pen = QtGui.QPen(color, 2)
                            painter.setPen(outline_pen)
                            for ddx in [-1, 0, 1]:
                                for ddy in [-1, 0, 1]:
                                    if ddx != 0 or ddy != 0:
                                        painter.drawText(draw_x, draw_y, char)
                            painter.setPen(QtGui.QPen(color))
                        else:
                            painter.drawText(draw_x, draw_y, char)
                        
                        painter.restore()
        else:
            for i, char in enumerate(text_content):
                char_x_base, char_y_base, char_width = char_positions[i]
                char_height = font_metrics.height()
                
                transform = animation_effects.get_animation_transform(
                    style_index, i, text_length, elapsed_sec, hold_time, speed,
                    char_x_base, char_y_base,
                    char_width, char_height, text_width, text_height,
                    text_center_x, text_center_y
                )
                
                color = animation_effects.get_animation_color(style_index, i, text_length, elapsed_sec)
                
                painter.save()
                painter.setPen(QtGui.QPen(color))
                painter.setOpacity(transform.get('opacity', 1.0))
                
                char_x = transform.get('x', char_x_base)
                char_y = transform.get('y', char_y_base)
                scale_x = transform.get('scale_x', 1.0)
                scale_y = transform.get('scale_y', 1.0)
                rotation = transform.get('rotation', 0.0)
                
                pivot_x = transform.get('pivot_x', char_x + char_width / 2)
                pivot_y = transform.get('pivot_y', char_y)
                
                dx = char_x - char_x_base
                dy = char_y - char_y_base
                
                if rotation != 0.0 or scale_x != 1.0 or scale_y != 1.0 or dx != 0.0 or dy != 0.0:
                    transform_matrix = QtGui.QTransform()
                    transform_matrix.translate(pivot_x, pivot_y)
                    transform_matrix.rotate(math.degrees(rotation))
                    transform_matrix.scale(scale_x, scale_y)
                    transform_matrix.translate(-pivot_x, -pivot_y)
                    transform_matrix.translate(dx, dy)
                    painter.setTransform(transform_matrix)
                
                if text_format.get("hollow", False):
                    outline_pen = QtGui.QPen(color, 2)
                    painter.setPen(outline_pen)
                    for ddx in [-1, 0, 1]:
                        for ddy in [-1, 0, 1]:
                            if ddx != 0 or ddy != 0:
                                painter.drawText(int(char_x_base), int(char_y_base), char)
                    painter.setPen(QtGui.QPen(color))
                else:
                    painter.drawText(int(char_x_base), int(char_y_base), char)
                
                painter.restore()
        
        painter.setClipping(False)
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
            painter.drawRect(element_rect)

    def _draw_timing(self, painter, element_props, x, y, width, height, element_rect, is_selected, element_id, scale):
        from datetime import datetime, timedelta
        from PyQt5.QtCore import QDateTime, Qt
        
        timing_props = element_props.get("timing", {})
        mode = timing_props.get("mode", "suitable_time")
        
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        top_text = timing_props.get("top_text", "To **")
        top_text_color_str = timing_props.get("top_text_color", "#cdcd00")
        top_text_color = QtGui.QColor(top_text_color_str)
        multiline = timing_props.get("multiline", True)
        top_text_space = timing_props.get("top_text_space", 5)
        
        display_style = timing_props.get("display_style", {})
        display_color_str = display_style.get("color", "#ff9900")
        display_color = QtGui.QColor(display_color_str)
        position_align = display_style.get("position_align", "center")
        
        font = painter.font()
        font.setPointSize(max(8, int(24 * scale)))
        painter.setFont(font)
        font_metrics = painter.fontMetrics()
        
        year_enabled = display_style.get("year", True)
        day_enabled = display_style.get("day", True)
        hour_enabled = display_style.get("hour", True)
        minute_enabled = display_style.get("minute", True)
        second_enabled = display_style.get("second", True)
        millisecond_enabled = display_style.get("millisecond", False)
        
        now = datetime.now()
        
        if mode == "suitable_time":
            suitable_time = timing_props.get("suitable_time", {})
            suitable_time_str = suitable_time.get("datetime", "")
            if suitable_time_str:
                target_dt = QDateTime.fromString(suitable_time_str, Qt.ISODate)
                if target_dt.isValid():
                    target_datetime = target_dt.toPyDateTime()
                    if now > target_datetime:
                        time_delta = now - target_datetime
                    else:
                        time_delta = timedelta(0)
                else:
                    time_delta = timedelta(0)
            else:
                time_delta = timedelta(0)
        elif mode == "count_down":
            count_down = timing_props.get("count_down", {})
            count_down_str = count_down.get("datetime", "")
            if count_down_str:
                target_dt = QDateTime.fromString(count_down_str, Qt.ISODate)
                if target_dt.isValid():
                    target_datetime = target_dt.toPyDateTime()
                    if target_datetime > now:
                        time_delta = target_datetime - now
                    else:
                        time_delta = timedelta(0)
                else:
                    time_delta = timedelta(0)
            else:
                time_delta = timedelta(0)
        else:
            fixed_time = timing_props.get("fixed_time", {})
            day_period = fixed_time.get("day_period", 0)
            time_str = fixed_time.get("time", "")
            if element_id:
                current_period_seconds = day_period * 86400
                if time_str:
                    time_obj = QDateTime.fromString(time_str, Qt.ISODate).time()
                    if time_obj.isValid():
                        current_period_seconds += time_obj.hour() * 3600 + time_obj.minute() * 60 + time_obj.second()
                
                if element_id not in self._text_flow_animations:
                    self._text_flow_animations[element_id] = {
                        "start_time": QtCore.QDateTime.currentDateTime(),
                        "period_seconds": current_period_seconds
                    }
                
                anim_state = self._text_flow_animations[element_id]
                stored_period = anim_state.get("period_seconds", 0)
                
                if current_period_seconds != stored_period:
                    anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
                    anim_state["period_seconds"] = current_period_seconds
                    stored_period = current_period_seconds
                
                start_dt = anim_state.get("start_time", QtCore.QDateTime.currentDateTime())
                elapsed_seconds = start_dt.secsTo(QtCore.QDateTime.currentDateTime())
                remaining_seconds = max(0, stored_period - elapsed_seconds)
                time_delta = timedelta(seconds=int(remaining_seconds))
            else:
                time_delta = timedelta(0)
        
        total_seconds = int(time_delta.total_seconds())
        milliseconds = int(time_delta.total_seconds() * 1000) % 1000
        
        years = total_seconds // 31536000
        remaining = total_seconds % 31536000
        days = remaining // 86400
        remaining = remaining % 86400
        hours = remaining // 3600
        remaining = remaining % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        
        if mode == "fixed_time":
            total_hours = total_seconds // 3600
            remaining_for_minutes = total_seconds % 3600
            total_minutes = remaining_for_minutes // 60
            total_secs = remaining_for_minutes % 60
            display_text = f"{total_hours:02d}:{total_minutes:02d}:{total_secs:02d}"
        else:
            display_parts = []
            if year_enabled:
                display_parts.append(f"{years}Y")
            if day_enabled:
                display_parts.append(f"{days}D")
            if hour_enabled:
                display_parts.append(f"{hours}H")
            if minute_enabled:
                display_parts.append(f"{minutes}M")
            if second_enabled:
                display_parts.append(f"{seconds}S")
            if millisecond_enabled:
                display_parts.append(f"{milliseconds}ms")
            
            if not display_parts:
                display_parts = ["0S"]
            
            display_text = " ".join(display_parts)
        
        line_height = font_metrics.height()
        ascent = font_metrics.ascent()
        descent = font_metrics.descent()
        
        if top_text:
            painter.setPen(QtGui.QPen(top_text_color))
            if multiline:
                top_text_lines = [line for line in top_text.split('\n') if line]
                if not top_text_lines:
                    top_text_lines = [""]
                
                total_lines = len(top_text_lines)
                total_content_height = total_lines * line_height + max(0, (total_lines - 1) * top_text_space)
                
                if position_align == "top":
                    start_y = y + ascent
                elif position_align == "center":
                    start_y = y + max(0, (height - total_content_height) / 2) + ascent
                else:
                    start_y = y + max(0, height - total_content_height) + ascent
                
                start_y = max(y + ascent, min(start_y, y + height - descent))
                
                current_line_y = start_y
                for line in top_text_lines:
                    if current_line_y < y or current_line_y + line_height > y + height:
                        break
                    
                    if line:
                        line_width = font_metrics.width(line)
                        display_width = font_metrics.width(display_text)
                        combined_width = line_width + top_text_space + display_width
                        
                        line_x = x + max(0, (width - combined_width) / 2)
                        line_x = max(x, min(line_x, x + max(0, width - min(combined_width, width))))
                        line_x = int(line_x)
                        current_line_y_int = int(current_line_y)
                        
                        painter.drawText(line_x, current_line_y_int, line)
                        display_x = line_x + line_width + top_text_space
                        painter.setPen(QtGui.QPen(display_color))
                        painter.drawText(display_x, current_line_y_int, display_text)
                        painter.setPen(QtGui.QPen(top_text_color))
                    
                    current_line_y += line_height + top_text_space
                    if current_line_y > y + height:
                        break
            else:
                single_line_text = top_text.replace('\n', ' ')
                top_text_width = font_metrics.width(single_line_text)
                display_width = font_metrics.width(display_text)
                combined_width = top_text_width + top_text_space + display_width
                
                if position_align == "top":
                    line_y = y + ascent
                elif position_align == "center":
                    line_y = y + height / 2 + ascent / 2
                else:
                    line_y = y + height - line_height
                
                line_y = max(y + ascent, min(int(line_y), y + height - descent))
                
                line_x = x + max(0, (width - combined_width) / 2)
                line_x = max(x, min(int(line_x), x + max(0, width - min(combined_width, width))))
                
                painter.drawText(line_x, line_y, single_line_text)
                display_x = line_x + top_text_width + top_text_space
                painter.setPen(QtGui.QPen(display_color))
                painter.drawText(display_x, line_y, display_text)
        else:
            display_width = font_metrics.width(display_text)
            
            if position_align == "top":
                display_y = y + ascent
            elif position_align == "center":
                display_y = y + height / 2 + ascent / 2
            else:
                display_y = y + height - line_height
            
            display_y = max(y + ascent, min(int(display_y), y + height - descent))
            
            display_x = x + max(0, (width - display_width) / 2)
            display_x = max(x, min(int(display_x), x + max(0, width - min(display_width, width))))
            
            painter.setPen(QtGui.QPen(display_color))
            painter.drawText(display_x, display_y, display_text)
        
        painter.setClipping(False)
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
            painter.drawRect(element_rect)

    def _get_sensor_unit(self, sensor_props: dict) -> str:
        unit = sensor_props.get("unit", "")
        if unit:
            return unit
        
        sensor_type = sensor_props.get("sensor_type", "temp")
        unit_map = {
            "temp": "°C",
            "Air Humidity": "%",
            "PM2.5": "",
            "PM10": "",
            "Wind power": "LV",
            "Wind Direction": "wind",
            "Noise": "dB",
            "Pressure": "kPa",
            "Light Intensity": "Lux",
            "CO2": "ppm"
        }
        return unit_map.get(sensor_type, "")
    
    def _get_sensor_value(self, sensor_props: dict, sensor_type: str) -> float:
        stored_value = sensor_props.get("value")
        if stored_value is not None:
            try:
                return float(stored_value)
            except (ValueError, TypeError):
                pass
        
        default_values = {
            "temp": 25.0,
            "Air Humidity": 60.0,
            "PM2.5": 50.0,
            "PM10": 70.0,
            "Wind power": 5.0,
            "Wind Direction": 180.0,
            "Noise": 65.0,
            "Pressure": 1013.25,
            "Light Intensity": 500.0,
            "CO2": 400.0
        }
        return default_values.get(sensor_type, 0.0)
    
    def _draw_sensor(self, painter, element_props, x, y, width, height, element_rect, is_selected, scale):
        sensor_props = element_props.get("sensor", {})
        if not isinstance(sensor_props, dict):
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 20, 147) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "SENSOR")
            if is_selected:
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                painter.drawRect(element_rect)
            return
        
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        sensor_type = sensor_props.get("sensor_type", "temp")
        fixed_text = sensor_props.get("fixed_text", f"The {sensor_type}")
        sensor_value = self._get_sensor_value(sensor_props, sensor_type)
        sensor_unit = self._get_sensor_unit(sensor_props)
        
        if sensor_type == "Wind Direction":
            value_text = f"{int(sensor_value)}"
        elif sensor_type in ["Light Intensity", "CO2"]:
            value_text = f"{int(sensor_value)}"
        else:
            value_text = f"{sensor_value}"
        
        if sensor_unit:
            display_text = f"{fixed_text} {value_text}{sensor_unit}"
        else:
            display_text = f"{fixed_text} {value_text}"
        
        font = painter.font()
        font_family = sensor_props.get("font_family", "Arial")
        font.setFamily(font_family)
        font.setPointSize(max(8, int(24 * scale)))
        painter.setFont(font)
        font_metrics = painter.fontMetrics()
        
        text_width = font_metrics.width(display_text)
        line_height = font_metrics.height()
        ascent = font_metrics.ascent()
        descent = font_metrics.descent()
        
        display_x = x + max(0, (width - text_width) / 2)
        display_x = max(x, min(int(display_x), x + max(0, width - min(text_width, width))))
        
        display_y = y + height / 2 + ascent / 2
        display_y = max(y + ascent, min(int(display_y), y + height - descent))
        
        font_color_str = sensor_props.get("font_color", "#FFFFFF")
        font_color = QtGui.QColor(font_color_str)
        painter.setPen(QtGui.QPen(font_color))
        painter.drawText(display_x, display_y, display_text)
        
        painter.setClipping(False)
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
            painter.drawRect(element_rect)

    def _setup_html_widget(self, painter, element_props, x, y, width, height, element_rect, is_selected, element_id, scale):
        html_props = element_props.get("html", {})
        url = html_props.get("url", "https://www.google.com/") if isinstance(html_props, dict) else "https://www.google.com/"
        
        if not WEBENGINE_AVAILABLE:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 191, 255) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "HTML\n(WebEngine not available)")
            if is_selected:
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                painter.drawRect(element_rect)
            return
        
        if element_id not in self._html_widgets:
            web_view = QWebEngineView(self)
            web_view.hide()
            web_view.setAttribute(Qt.WA_OpaquePaintEvent, False)
            web_view.setAutoFillBackground(False)
            self._html_widgets[element_id] = web_view
            web_view.load(QUrl(url))
        
        web_view = self._html_widgets[element_id]
        current_url = web_view.url().toString()
        if current_url != url:
            web_view.load(QUrl(url))
        
        web_view.setGeometry(int(x), int(y), int(width), int(height))
        web_view.lower()
        web_view.show()
        
        time_refresh_enabled = html_props.get("time_refresh_enabled", False) if isinstance(html_props, dict) else False
        time_refresh_value = html_props.get("time_refresh_value", 15.0) if isinstance(html_props, dict) else 15.0
        
        if time_refresh_enabled and element_id:
            if element_id not in self._html_refresh_timers:
                refresh_timer = QTimer(self)
                refresh_timer.timeout.connect(lambda: self._refresh_html_page(element_id, url))
                refresh_timer.setSingleShot(False)
                self._html_refresh_timers[element_id] = refresh_timer
                refresh_timer.start(int(time_refresh_value * 1000))
            else:
                timer = self._html_refresh_timers[element_id]
                interval = int(time_refresh_value * 1000)
                if timer.interval() != interval:
                    timer.setInterval(interval)
                if not timer.isActive():
                    timer.start()
        else:
            if element_id in self._html_refresh_timers:
                self._html_refresh_timers[element_id].stop()
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 0)))
            painter.drawRect(element_rect)
    
    def _refresh_html_page(self, element_id: str, url: str):
        if element_id in self._html_widgets:
            web_view = self._html_widgets[element_id]
            html_props = {}
            for program in self.screen_manager.current_screen.programs if self.screen_manager and self.screen_manager.current_screen else []:
                for element in program.elements:
                    if element.get("id") == element_id:
                        html_props = element.get("properties", {}).get("html", {})
                        break
                if html_props:
                    break
            
            current_url = html_props.get("url", url) if isinstance(html_props, dict) else url
            web_view.load(QUrl(current_url))
    
    def _cleanup_html_widgets(self):
        current_elements = {e.get("id") for e in self._get_current_program_elements() if e.get("type") == "html"}
        
        for element_id in list(self._html_widgets.keys()):
            if element_id not in current_elements:
                if element_id in self._html_refresh_timers:
                    self._html_refresh_timers[element_id].stop()
                    del self._html_refresh_timers[element_id]
                if element_id in self._html_widgets:
                    self._html_widgets[element_id].hide()
                    self._html_widgets[element_id].deleteLater()
                    del self._html_widgets[element_id]
    
    def _setup_hdmi_widget(self, painter, element_props, x, y, width, height, element_rect, is_selected, element_id, scale):
        hdmi_props = element_props.get("hdmi", {})
        display_mode = hdmi_props.get("display_mode", "Full Screen Zoom") if isinstance(hdmi_props, dict) else "Full Screen Zoom"
        
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        painter.setPen(QtGui.QPen(QtGui.QColor(50, 50, 50)))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        painter.drawRect(element_rect)
        
        font = painter.font()
        font.setPointSize(max(8, int(16 * scale)))
        painter.setFont(font)
        font_metrics = painter.fontMetrics()
        
        mode_text = f"HDMI: {display_mode}"
        text_width = font_metrics.width(mode_text)
        text_height = font_metrics.height()
        ascent = font_metrics.ascent()
        
        text_x = x + (width - text_width) / 2
        text_y = y + (height + ascent) / 2
        
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200)))
        painter.drawText(int(text_x), int(text_y), mode_text)
        
        if display_mode == "Full Screen Zoom":
            corner_size = min(width, height) // 8
            corner_length = corner_size
            corner_thickness = 2
            
            painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100), corner_thickness))
            
            top_left = QtCore.QPoint(x, y)
            top_right = QtCore.QPoint(x + width, y)
            bottom_left = QtCore.QPoint(x, y + height)
            bottom_right = QtCore.QPoint(x + width, y + height)
            
            painter.drawLine(top_left, QtCore.QPoint(x + corner_length, y))
            painter.drawLine(top_left, QtCore.QPoint(x, y + corner_length))
            
            painter.drawLine(top_right, QtCore.QPoint(x + width - corner_length, y))
            painter.drawLine(top_right, QtCore.QPoint(x + width, y + corner_length))
            
            painter.drawLine(bottom_left, QtCore.QPoint(x, y + height - corner_length))
            painter.drawLine(bottom_left, QtCore.QPoint(x + corner_length, y + height))
            
            painter.drawLine(bottom_right, QtCore.QPoint(x + width - corner_length, y + height))
            painter.drawLine(bottom_right, QtCore.QPoint(x + width, y + height - corner_length))
        
        painter.setClipping(False)
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 0)))
            painter.drawRect(element_rect)

    def paintEvent(self, event):
        rect = self.rect()
        current_size = rect.size()
        
        # Validate size before creating pixmap
        if current_size.width() <= 0 or current_size.height() <= 0:
            return
        
        if self._cached_pixmap is None or self._cached_size != current_size:
            self._cached_pixmap = QtGui.QPixmap(current_size)
            if self._cached_pixmap.isNull():
                return
            
            self._cached_pixmap.fill(self.color2)
            
            painter = QtGui.QPainter(self._cached_pixmap)
            if not painter.isActive():
                return
            
            painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
            
            size = self.checker_size
            for y in range(0, current_size.height(), size):
                for x in range(0, current_size.width(), size):
                    if ((x // size) + (y // size)) % 2 == 0:
                        square_rect = QtCore.QRect(x, y, size, size)
                        painter.fillRect(square_rect, self.color1)
            
            painter.end()
            self._cached_size = current_size
        
        if self._cached_pixmap is None or self._cached_pixmap.isNull():
            return
        
        painter = QtGui.QPainter(self)
        if not painter.isActive():
            return
        
        painter.drawPixmap(rect.topLeft(), self._cached_pixmap)
        
        has_screens = self.screen_manager and self.screen_manager.screens and len(self.screen_manager.screens) > 0
        has_current_screen = self.screen_manager and self.screen_manager.current_screen
        has_programs = has_current_screen and self.screen_manager.current_screen.programs and len(self.screen_manager.current_screen.programs) > 0
        
        config = get_screen_config()
        if config and has_screens and has_current_screen and has_programs:
            screen_width = config.get("width", 0)
            screen_height = config.get("height", 0)
            if screen_width > 0 and screen_height > 0:
                available_width = current_size.width()
                available_height = current_size.height()
                
                padding = 20
                available_width_with_padding = available_width - (padding * 2)
                available_height_with_padding = available_height - (padding * 2)
                
                scale_x = available_width_with_padding / screen_width
                scale_y = available_height_with_padding / screen_height
                scale = min(scale_x, scale_y)
                
                scaled_width = int(screen_width * scale)
                scaled_height = int(screen_height * scale)
                
                center_x = available_width / 2
                center_y = available_height / 2
                rect_x = int(center_x - (scaled_width / 2))
                rect_y = int(center_y - (scaled_height / 2))
                
                black_rect = QtCore.QRect(rect_x, rect_y, scaled_width, scaled_height)
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                painter.drawRect(black_rect)
                
                self.scale_factor = scale
                self.screen_offset_x = rect_x
                self.screen_offset_y = rect_y
                
                painter.setClipRect(black_rect)
                
                for widget in self._html_widgets.values():
                    widget.hide()
                
                self._cleanup_video_players()
                self._cleanup_html_widgets()
                
                current_elements = {e.get("id") for e in self._get_current_program_elements()}
                for element_id in list(self._photo_animations.keys()):
                    if element_id not in current_elements:
                        del self._photo_animations[element_id]
                for element_id in list(self._text_animations.keys()):
                    if element_id not in current_elements:
                        del self._text_animations[element_id]
                
                elements = self._get_current_program_elements()
                for element in elements:
                    self._draw_element(painter, element, rect_x, rect_y, scale)
                
                if self.selected_element_id:
                    selected_element = next((e for e in elements if e.get("id") == self.selected_element_id), None)
                    if selected_element:
                        self._draw_selection_handles(painter, selected_element)
                
                painter.setClipping(False)
        else:
            self.scale_factor = 1.0
            self.screen_offset_x = 0
            self.screen_offset_y = 0
            for widget in self._html_widgets.values():
                widget.hide()
            self._cleanup_video_players()
            self._cleanup_html_widgets()
        
        painter.end()

    def _on_property_changed(self, property_name: str, value):
        self.update()
    
    def _update_clocks(self):
        if not self.screen_manager or not self.screen_manager.current_screen:
            return
        
        has_clock = False
        has_timing = False
        for program in self.screen_manager.current_screen.programs:
            for element in program.elements:
                element_type = element.get("type", "").lower()
                if element_type == "clock":
                    has_clock = True
                elif element_type == "timing":
                    has_timing = True
            if has_clock and has_timing:
                break
        
        if has_clock or has_timing:
            self.update()
    
    def resizeEvent(self, event):
        self._cached_pixmap = None
        super().resizeEvent(event)
        self.update()
    
    def _screen_to_canvas(self, screen_x: int, screen_y: int) -> tuple:
        if self.scale_factor <= 0:
            return (0, 0)
        canvas_x = int((screen_x - self.screen_offset_x) / self.scale_factor)
        canvas_y = int((screen_y - self.screen_offset_y) / self.scale_factor)
        return (canvas_x, canvas_y)
    
    def _canvas_to_screen(self, canvas_x: int, canvas_y: int) -> tuple:
        screen_x = int(self.screen_offset_x + (canvas_x * self.scale_factor))
        screen_y = int(self.screen_offset_y + (canvas_y * self.scale_factor))
        return (screen_x, screen_y)
    
    def _get_element_at_position(self, screen_x: int, screen_y: int) -> Optional[Dict]:
        elements = self._get_current_program_elements()
        for element in reversed(elements):
            element_props = element.get("properties", {})
            x = element_props.get("x", element.get("x", 0))
            y = element_props.get("y", element.get("y", 0))
            width = element_props.get("width", element.get("width", 100))
            height = element_props.get("height", element.get("height", 100))
            
            scaled_x = int(self.screen_offset_x + (x * self.scale_factor))
            scaled_y = int(self.screen_offset_y + (y * self.scale_factor))
            scaled_width = int(width * self.scale_factor)
            scaled_height = int(height * self.scale_factor)
            
            rect = QtCore.QRect(scaled_x, scaled_y, scaled_width, scaled_height)
            if rect.contains(screen_x, screen_y):
                return element
        return None
    
    def _get_resize_handle(self, screen_x: int, screen_y: int, element: Dict) -> Optional[str]:
        if not element or element.get("id") != self.selected_element_id:
            return None
        
        element_props = element.get("properties", {})
        x = element_props.get("x", element.get("x", 0))
        y = element_props.get("y", element.get("y", 0))
        width = element_props.get("width", element.get("width", 100))
        height = element_props.get("height", element.get("height", 100))
        
        scaled_x = int(self.screen_offset_x + (x * self.scale_factor))
        scaled_y = int(self.screen_offset_y + (y * self.scale_factor))
        scaled_width = int(width * self.scale_factor)
        scaled_height = int(height * self.scale_factor)
        
        handle_size = self._resize_handle_size
        
        handles = {
            "nw": QtCore.QRect(scaled_x - handle_size//2, scaled_y - handle_size//2, handle_size, handle_size),
            "n": QtCore.QRect(scaled_x + scaled_width//2 - handle_size//2, scaled_y - handle_size//2, handle_size, handle_size),
            "ne": QtCore.QRect(scaled_x + scaled_width - handle_size//2, scaled_y - handle_size//2, handle_size, handle_size),
            "e": QtCore.QRect(scaled_x + scaled_width - handle_size//2, scaled_y + scaled_height//2 - handle_size//2, handle_size, handle_size),
            "se": QtCore.QRect(scaled_x + scaled_width - handle_size//2, scaled_y + scaled_height - handle_size//2, handle_size, handle_size),
            "s": QtCore.QRect(scaled_x + scaled_width//2 - handle_size//2, scaled_y + scaled_height - handle_size//2, handle_size, handle_size),
            "sw": QtCore.QRect(scaled_x - handle_size//2, scaled_y + scaled_height - handle_size//2, handle_size, handle_size),
            "w": QtCore.QRect(scaled_x - handle_size//2, scaled_y + scaled_height//2 - handle_size//2, handle_size, handle_size),
        }
        
        for handle_name, handle_rect in handles.items():
            if handle_rect.contains(screen_x, screen_y):
                return handle_name
        return None
    
    def _get_cursor_for_handle(self, handle: Optional[str]) -> Qt.CursorShape:
        if not handle:
            return Qt.ArrowCursor # type: ignore
        cursors = {
            "nw": Qt.SizeFDiagCursor, # type: ignore
            "n": Qt.SizeVerCursor, # type: ignore
            "ne": Qt.SizeBDiagCursor, # type: ignore
            "e": Qt.SizeHorCursor, # type: ignore
            "se": Qt.SizeFDiagCursor, # type: ignore
            "s": Qt.SizeVerCursor, # type: ignore
            "sw": Qt.SizeBDiagCursor, # type: ignore
            "w": Qt.SizeHorCursor, # type: ignore
        }
        return cursors.get(handle, Qt.ArrowCursor) # type: ignore
    
    def _update_element_position(self, element: Dict, new_x: int, new_y: int):
        if not self.screen_manager:
            return
        
        program = None
        for screen in self.screen_manager.screens:
            for p in screen.programs:
                if element in p.elements:
                    program = p
                    break
            if program:
                break
        
        if not program:
            return
        
        from datetime import datetime
        screen_width, screen_height = self._get_screen_bounds()
        element_props = element.get("properties", {})
        width = element_props.get("width", element.get("width", 100))
        height = element_props.get("height", element.get("height", 100))
        
        new_x = max(0, min(new_x, screen_width - width))
        new_y = max(0, min(new_y, screen_height - height))
        
        if "properties" not in element:
            element["properties"] = {}
        element["properties"]["x"] = new_x
        element["properties"]["y"] = new_y
        element["x"] = new_x
        element["y"] = new_y
        program.modified = datetime.now().isoformat()
        
        if self.properties_panel:
            self.properties_panel.property_changed.emit("element_position", (new_x, new_y))
            if hasattr(self.properties_panel, 'update_properties'):
                self.properties_panel.update_properties()
        
        self.update()
    
    def _update_element_size(self, element: Dict, new_width: int, new_height: int, handle: str):
        if not self.screen_manager:
            return
        
        program = None
        for screen in self.screen_manager.screens:
            for p in screen.programs:
                if element in p.elements:
                    program = p
                    break
            if program:
                break
        
        if not program:
            return
        
        from datetime import datetime
        screen_width, screen_height = self._get_screen_bounds()
        element_props = element.get("properties", {})
        x = element_props.get("x", element.get("x", 0))
        y = element_props.get("y", element.get("y", 0))
        
        min_size = 10
        new_width = max(min_size, min(new_width, screen_width - x))
        new_height = max(min_size, min(new_height, screen_height - y))
        
        if "properties" not in element:
            element["properties"] = {}
        element["properties"]["width"] = new_width
        element["properties"]["height"] = new_height
        element["width"] = new_width
        element["height"] = new_height
        program.modified = datetime.now().isoformat()
        
        if self.properties_panel:
            self.properties_panel.property_changed.emit("element_size", (new_width, new_height))
            if hasattr(self.properties_panel, 'update_properties'):
                self.properties_panel.update_properties()
        
        self.update()
    
    def _get_screen_bounds(self) -> tuple:
        from core.screen_config import get_screen_config
        config = get_screen_config()
        if config:
            width = config.get("width", 640)
            height = config.get("height", 480)
            if width > 0 and height > 0:
                return (width, height)
        return (640, 480)
    
    def _draw_selection_handles(self, painter, element: Dict):
        if not element or element.get("id") != self.selected_element_id:
            return
        
        element_props = element.get("properties", {})
        x = element_props.get("x", element.get("x", 0))
        y = element_props.get("y", element.get("y", 0))
        width = element_props.get("width", element.get("width", 100))
        height = element_props.get("height", element.get("height", 100))
        
        scaled_x = int(self.screen_offset_x + (x * self.scale_factor))
        scaled_y = int(self.screen_offset_y + (y * self.scale_factor))
        scaled_width = int(width * self.scale_factor)
        scaled_height = int(height * self.scale_factor)
        
        handle_size = self._resize_handle_size
        handle_color = QtGui.QColor(255, 255, 255)
        handle_border = QtGui.QColor(0, 0, 0)
        
        handles = [
            (scaled_x - handle_size//2, scaled_y - handle_size//2),
            (scaled_x + scaled_width//2 - handle_size//2, scaled_y - handle_size//2),
            (scaled_x + scaled_width - handle_size//2, scaled_y - handle_size//2),
            (scaled_x + scaled_width - handle_size//2, scaled_y + scaled_height//2 - handle_size//2),
            (scaled_x + scaled_width - handle_size//2, scaled_y + scaled_height - handle_size//2),
            (scaled_x + scaled_width//2 - handle_size//2, scaled_y + scaled_height - handle_size//2),
            (scaled_x - handle_size//2, scaled_y + scaled_height - handle_size//2),
            (scaled_x - handle_size//2, scaled_y + scaled_height//2 - handle_size//2),
        ]
        
        for hx, hy in handles:
            handle_rect = QtCore.QRect(hx, hy, handle_size, handle_size)
            painter.setPen(QtGui.QPen(handle_border, 1))
            painter.setBrush(QtGui.QBrush(handle_color))
            painter.drawRect(handle_rect)
    
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            super().mousePressEvent(event)
            return
        
        screen_x = event.x()
        screen_y = event.y()
        
        if not (self.screen_offset_x <= screen_x <= self.screen_offset_x + int(self.scale_factor * self._get_screen_bounds()[0]) and
                self.screen_offset_y <= screen_y <= self.screen_offset_y + int(self.scale_factor * self._get_screen_bounds()[1])):
            super().mousePressEvent(event)
            return
        
        element = self._get_element_at_position(screen_x, screen_y)
        
        if element:
            self.selected_element_id = element.get("id")
            if self.properties_panel:
                program = None
                for screen in self.screen_manager.screens if self.screen_manager else []:
                    for p in screen.programs:
                        if element in p.elements:
                            program = p
                            break
                    if program:
                        break
                if program:
                    self.properties_panel.set_element(element, program)
            
            handle = self._get_resize_handle(screen_x, screen_y, element)
            if handle:
                self._drag_state = {
                    "type": "resize",
                    "element": element,
                    "handle": handle,
                    "start_x": screen_x,
                    "start_y": screen_y,
                    "start_element_x": element.get("properties", {}).get("x", element.get("x", 0)),
                    "start_element_y": element.get("properties", {}).get("y", element.get("y", 0)),
                    "start_element_width": element.get("properties", {}).get("width", element.get("width", 100)),
                    "start_element_height": element.get("properties", {}).get("height", element.get("height", 100)),
                }
            else:
                canvas_x, canvas_y = self._screen_to_canvas(screen_x, screen_y)
                self._drag_state = {
                    "type": "drag",
                    "element": element,
                    "start_x": screen_x,
                    "start_y": screen_y,
                    "start_canvas_x": canvas_x,
                    "start_canvas_y": canvas_y,
                    "start_element_x": element.get("properties", {}).get("x", element.get("x", 0)),
                    "start_element_y": element.get("properties", {}).get("y", element.get("y", 0)),
                }
        else:
            self.selected_element_id = None
            if self.properties_panel:
                self.properties_panel.set_element(None, None)
        
        self.update()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        screen_x = event.x()
        screen_y = event.y()
        
        if self._drag_state:
            if self._drag_state["type"] == "drag":
                canvas_x, canvas_y = self._screen_to_canvas(screen_x, screen_y)
                dx = canvas_x - self._drag_state["start_canvas_x"]
                dy = canvas_y - self._drag_state["start_canvas_y"]
                new_x = self._drag_state["start_element_x"] + dx
                new_y = self._drag_state["start_element_y"] + dy
                self._update_element_position(self._drag_state["element"], new_x, new_y)
            elif self._drag_state["type"] == "resize":
                handle = self._drag_state["handle"]
                canvas_x, canvas_y = self._screen_to_canvas(screen_x, screen_y)
                start_canvas_x, start_canvas_y = self._screen_to_canvas(
                    self._drag_state["start_x"],
                    self._drag_state["start_y"]
                )
                
                dx = canvas_x - start_canvas_x
                dy = canvas_y - start_canvas_y
                
                start_x = self._drag_state["start_element_x"]
                start_y = self._drag_state["start_element_y"]
                start_width = self._drag_state["start_element_width"]
                start_height = self._drag_state["start_element_height"]
                
                new_x = start_x
                new_y = start_y
                new_width = start_width
                new_height = start_height
                
                if "n" in handle:
                    new_y = start_y + dy
                    new_height = start_height - dy
                if "s" in handle:
                    new_height = start_height + dy
                if "w" in handle:
                    new_x = start_x + dx
                    new_width = start_width - dx
                if "e" in handle:
                    new_width = start_width + dx
                
                if new_width < 10:
                    if "w" in handle:
                        new_x = start_x + start_width - 10
                    new_width = 10
                if new_height < 10:
                    if "n" in handle:
                        new_y = start_y + start_height - 10
                    new_height = 10
                
                element = self._drag_state["element"]
                element_props = element.get("properties", {})
                element_props["x"] = new_x
                element_props["y"] = new_y
                element_props["width"] = new_width
                element_props["height"] = new_height
                element["x"] = new_x
                element["y"] = new_y
                element["width"] = new_width
                element["height"] = new_height
                self.update()
        else:
            element = self._get_element_at_position(screen_x, screen_y)
            if element and element.get("id") == self.selected_element_id:
                handle = self._get_resize_handle(screen_x, screen_y, element)
                if handle != self._hover_handle:
                    self._hover_handle = handle
                    cursor = self._get_cursor_for_handle(handle)
                    self.setCursor(cursor)
                    self.update()
            else:
                if self._hover_handle:
                    self._hover_handle = None
                    self.setCursor(Qt.ArrowCursor)
                    self.update()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drag_state:
            if self._drag_state["type"] == "resize":
                element = self._drag_state["element"]
                element_props = element.get("properties", {})
                new_width = element_props.get("width", element.get("width", 100))
                new_height = element_props.get("height", element.get("height", 100))
                self._update_element_size(element, new_width, new_height, self._drag_state["handle"])
            
            if self.properties_panel and self._drag_state["element"]:
                program = None
                for screen in self.screen_manager.screens if self.screen_manager else []:
                    for p in screen.programs:
                        if self._drag_state["element"] in p.elements:
                            program = p
                            break
                    if program:
                        break
                if program:
                    self.properties_panel.set_element(self._drag_state["element"], program)
            
            self._drag_state = None
            self.update()
        
        super().mouseReleaseEvent(event)
