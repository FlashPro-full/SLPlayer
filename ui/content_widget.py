from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from typing import Optional, Dict
from core.screen_config import get_screen_config

if False:
    from core.screen_manager import ScreenManager


class ContentWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, screen_manager: Optional['ScreenManager'] = None):
        super().__init__(parent)
        self.screen_manager = screen_manager
        self.checker_size = 10
        self.color1 = QtGui.QColor(240, 240, 240)
        self.color2 = QtGui.QColor(255, 255, 255)
        self._cached_pixmap = None
        self._cached_size = QSize()
        self.scale_factor = 1.0
        self.screen_offset_x = 0
        self.screen_offset_y = 0
        self.selected_element_id: Optional[str] = None
        self.properties_panel = None
        self.screen_list_panel = None
        self._video_players: Dict[str, QMediaPlayer] = {}
        self._video_widgets: Dict[str, QVideoWidget] = {}
        self._is_playing = False
        self._photo_animations: Dict[str, Dict] = {}
        self._text_animations: Dict[str, Dict] = {}
        self._text_flow_animations: Dict[str, Dict] = {}
        self._animation_timer = QtCore.QTimer(self)
        self._animation_timer.timeout.connect(self._update_animations)
        self._animation_timer.setInterval(33)
        # Clock update timer - update every second
        self._clock_timer = QtCore.QTimer(self)
        self._clock_timer.timeout.connect(self._update_clocks)
        self._clock_timer.setInterval(1000)
        # Start clock timer immediately to update clocks in preview mode
        self._clock_timer.start()
    
    def set_screen_manager(self, screen_manager: Optional['ScreenManager']):
        self.screen_manager = screen_manager
    
    def set_properties_panel(self, properties_panel):
        self.properties_panel = properties_panel
        if properties_panel:
            # Connect property_changed signal to update content widget
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
        
        element = {
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
        
        if content_type == "video":
            element["properties"]["video_list"] = []
            element["properties"]["frame"] = {
                "enabled": False,
                "border": "---",
                "effect": "---",
                "speed": "---"
            }
            element["properties"]["video_shot"] = {
                "width": default_width,
                "height": default_height,
                "start_time": "00:00:00",
                "end_time": "00:00:30"
            }
        elif content_type == "photo":
            element["properties"]["photo_list"] = []
            element["properties"]["animation"] = {
                "entrance": "Random",
                "exit": "Random",
                "entrance_speed": "1 fast",
                "exit_speed": "1 fast",
                "hold_time": 0.0
            }
        elif content_type == "text":
            element["properties"]["text"] = {
                "content": "Text Content",
                "format": {
                    "font_family": "MS Shell Dlg 2",
                    "font_size": 16,
                    "font_color": "#ffffff",
                    "text_bg_color": "",
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "alignment": "left",
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
                    "title_enabled": True,  # Default enabled
                    "title_value": "LED",  # Default title "LED"
                    "title_color": "#0000FF",
                    "date_enabled": True,  # Default enabled
                    "date_format": "YYYY-MM-DD",
                    "date_color": "#0000FF",
                    "week_enabled": True,  # Default enabled
                    "week_format": "Full Name",
                    "week_color": "#00FF00",
                    "noon_enabled": True,  # Default enabled
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
                    "title_enabled": True,  # Default enabled
                    "title_value": "Clock",
                    "title_color": "#FF0000",
                    "date_enabled": True,  # Default enabled
                    "date_format": "YYYY-MM-DD",
                    "date_color": "#0000FF",
                    "time_enabled": True,  # Default enabled
                    "time_format": "HH:MM:SS",
                    "time_color": "#FF0000",
                    "week_enabled": True,  # Default enabled
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
        for player in self._video_players.values():
            if playing:
                if player.state() != QMediaPlayer.PlayingState:
                    player.play()
            else:
                if player.state() == QMediaPlayer.PlayingState:
                    player.pause()
        
        if playing:
            if not self._animation_timer.isActive():
                self._animation_timer.start()
            # Clock timer runs continuously (both in preview and playback)
            if not self._clock_timer.isActive():
                self._clock_timer.start()
        else:
            if self._animation_timer.isActive():
                self._animation_timer.stop()
            # Keep clock timer running even when not playing (for preview)
            # Clock timer continues to run
        self.update()
    
    def _setup_video_player(self, element_id: str, video_path: str):
        if element_id in self._video_players:
            return
        
        player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_widget = QVideoWidget(self)
        video_widget.setAttribute(Qt.WA_OpaquePaintEvent, False)
        video_widget.setAutoFillBackground(False)
        video_widget.setStyleSheet("background-color: transparent;")
        video_widget.hide()
        
        player.setVideoOutput(video_widget)
        player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        
        self._video_players[element_id] = player
        self._video_widgets[element_id] = video_widget
    
    def _update_video_widget_position(self, element_id: str, x: int, y: int, width: int, height: int):
        if element_id in self._video_widgets:
            video_widget = self._video_widgets[element_id]
            
            # Get video dimensions to calculate aspect ratio and center it
            video_width = width
            video_height = height
            video_x = x
            video_y = y
            
            # Try to get actual video dimensions from the player
            if element_id in self._video_players:
                player = self._video_players[element_id]
                # Get video size from media metadata or use cv2
                try:
                    video_url = player.media().canonicalUrl()
                    if video_url.isLocalFile():
                        video_path = video_url.toLocalFile()
                        try:
                            import cv2
                            video_file = cv2.VideoCapture(video_path)
                            if video_file.isOpened():
                                actual_width = int(video_file.get(cv2.CAP_PROP_FRAME_WIDTH))
                                actual_height = int(video_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                video_file.release()
                                
                                if actual_width > 0 and actual_height > 0:
                                    # Calculate aspect ratio and center the video
                                    video_aspect = actual_width / actual_height
                                    element_aspect = width / height
                                    
                                    if video_aspect > element_aspect:
                                        # Video is wider - fit to width
                                        video_width = width
                                        video_height = int(width / video_aspect)
                                        video_x = x
                                        video_y = y + (height - video_height) // 2
                                    else:
                                        # Video is taller - fit to height
                                        video_width = int(height * video_aspect)
                                        video_height = height
                                        video_x = x + (width - video_width) // 2
                                        video_y = y
                        except ImportError:
                            # cv2 not available, use full area
                            pass
                        except Exception:
                            # Error reading video, use full area
                            pass
                except Exception:
                    # If we can't get video dimensions, use full area
                    pass
            
            video_widget.setGeometry(video_x, video_y, video_width, video_height)
            # Ensure video widget is behind other elements (lower z-order)
            video_widget.lower()
            video_widget.show()
            
            if self._is_playing and element_id in self._video_players:
                player = self._video_players[element_id]
                if player.state() != QMediaPlayer.PlayingState:
                    player.play()
    
    def _cleanup_video_players(self):
        current_elements = {e.get("id") for e in self._get_current_program_elements() if e.get("type") == "video"}
        
        for element_id in list(self._video_players.keys()):
            if element_id not in current_elements:
                if element_id in self._video_players:
                    self._video_players[element_id].stop()
                    self._video_players[element_id].setMedia(QMediaContent())
                    del self._video_players[element_id]
                if element_id in self._video_widgets:
                    self._video_widgets[element_id].hide()
                    self._video_widgets[element_id].deleteLater()
                    del self._video_widgets[element_id]
    
    def _cleanup_all_video_players(self):
        for element_id in list(self._video_players.keys()):
            if element_id in self._video_players:
                self._video_players[element_id].stop()
                self._video_players[element_id].setMedia(QMediaContent())
                del self._video_players[element_id]
            if element_id in self._video_widgets:
                self._video_widgets[element_id].hide()
                self._video_widgets[element_id].deleteLater()
                del self._video_widgets[element_id]
    
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
    
    def _draw_photo_with_animation(self, painter, pixmap, x, y, width, height, element_id, animation_props, element_rect, is_selected):
        import random
        
        entrance_anim = animation_props.get("entrance", "None")
        exit_anim = animation_props.get("exit", "None")
        
        # If both entrance and exit are "Immediate Show", skip animation entirely
        if entrance_anim == "Immediate Show" and exit_anim == "Immediate Show":
            scaled_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Center the pixmap
            scaled_width = scaled_pixmap.width()
            scaled_height = scaled_pixmap.height()
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
        
        anim_state = self._photo_animations[element_id]
        
        # Available animations (excluding Random and Immediate Show)
        available_animations = [
            "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ]
        
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
                    anim_state["selected_exit_anim"] = "Immediate Show"
            exit_anim = anim_state["selected_exit_anim"]
        hold_time = animation_props.get("hold_time", 0.0)
        entrance_speed = animation_props.get("entrance_speed", "1 fast")
        exit_speed = animation_props.get("exit_speed", "1 fast")
        
        speed_multiplier = self._get_speed_multiplier(entrance_speed if anim_state["phase"] == "entrance" else exit_speed)
        
        # If Immediate Show, set entrance duration to 0 to skip animation
        if entrance_anim == "Immediate Show":
            anim_state["entrance_duration"] = 0.0
        else:
            anim_state["entrance_duration"] = 1000.0 / speed_multiplier
        
        # If exit is Immediate Show or None, set exit duration to 0
        if exit_anim == "Immediate Show" or exit_anim == "None":
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
            # If entrance is "Immediate Show", stay in hold phase indefinitely (no exit animation)
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
            # If entrance is "Immediate Show", we should never reach exit phase, but handle it just in case
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
                else:
                    anim_state["progress"] = elapsed / duration if duration > 0 else 1.0
        
        scaled_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Calculate centered position
        scaled_width = scaled_pixmap.width()
        scaled_height = scaled_pixmap.height()
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
        
        # Handle Random: select a random animation
        if anim_type == "Random":
            anim_type = random.choice(available_animations)
        
        # Handle Immediate Show: show immediately without animation
        if anim_type == "Immediate Show" or anim_type == "None":
            painter.drawPixmap(x, y, pixmap)
            return
        
        # Apply specific animations
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
        # Handle Immediate Show or None: don't show exit animation
        if anim_type == "Immediate Show" or anim_type == "None":
            return
        
        # Apply specific exit animations (reversed from entrance)
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
        if entrance_anim == "Immediate Show" and exit_anim == "Immediate Show":
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
                    anim_state["selected_exit_anim"] = "Immediate Show"
            exit_anim = anim_state["selected_exit_anim"]
        
        hold_time = animation_props.get("hold_time", 0.0)
        entrance_speed = animation_props.get("entrance_speed", "1 fast")
        exit_speed = animation_props.get("exit_speed", "1 fast")
        
        speed_multiplier = self._get_speed_multiplier(entrance_speed if anim_state["phase"] == "entrance" else exit_speed)
        
        # If Immediate Show, set entrance duration to 0 to skip animation
        if entrance_anim == "Immediate Show":
            anim_state["entrance_duration"] = 0.0
        else:
            anim_state["entrance_duration"] = 1000.0 / speed_multiplier
        
        # If exit is Immediate Show or None, set exit duration to 0
        if exit_anim == "Immediate Show" or exit_anim == "None" or (is_singleline and exit_anim == "Don't Clear Screen"):
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
            # If entrance is "Immediate Show", stay in hold phase indefinitely (no exit animation)
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
            # If entrance is "Immediate Show", we should never reach exit phase, but handle it just in case
            if entrance_anim == "Immediate Show":
                anim_state["phase"] = "hold"
                anim_state["progress"] = 1.0
            else:
                duration = anim_state["exit_duration"]
                if elapsed >= duration:
                    anim_state["phase"] = "entrance"
                    anim_state["start_time"] = QtCore.QDateTime.currentDateTime()
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
        """Draw text without animation effects"""
        # Only set clipping if element_rect is provided (not None) to avoid overriding animation clipping
        # When called from animation functions, element_rect is None, so we don't override the clipping set by animations
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
        
        # Default alignment: left for both single-line and multi-line
        if is_singleline:
            alignment = Qt.AlignLeft
        else:
            alignment = Qt.AlignLeft | Qt.TextWordWrap
        
        if text_format.get("alignment"):
            align_str = text_format.get("alignment")
            if is_singleline:
                if align_str == "left":
                    alignment = Qt.AlignLeft
                elif align_str == "center":
                    alignment = Qt.AlignHCenter
                elif align_str == "right":
                    alignment = Qt.AlignRight
            else:
                if align_str == "left":
                    alignment = Qt.AlignLeft | Qt.TextWordWrap
                elif align_str == "center":
                    alignment = Qt.AlignHCenter | Qt.TextWordWrap
                elif align_str == "right":
                    alignment = Qt.AlignRight | Qt.TextWordWrap
        
        element_bounds = QtCore.QRect(x, y, width, height)
        text_rect = QtCore.QRect(x, y, width, height)
        font_metrics = painter.fontMetrics()
        
        # Calculate actual text height using a temporary rect with very large height
        # This ensures we get the actual text height regardless of alignment
        temp_rect = QtCore.QRect(0, 0, width, 10000)
        text_bounding_rect = font_metrics.boundingRect(temp_rect, alignment, text_content)
        actual_text_height = text_bounding_rect.height()
        
        vertical_align = text_format.get("vertical_alignment", "top")
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
        
        # Handle Random: select a random animation
        if anim_type == "Random":
            anim_type = random.choice(available_animations)
        
        # Handle Immediate Show: show immediately without animation
        if anim_type == "Immediate Show" or anim_type == "None":
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setClipping(False)
            return
        
        # Save painter state
        painter.save()
        
        # Apply specific animations
        if anim_type == "Move Left" or (is_singleline and anim_type == "Continuous Move Left"):
            offset_x = int((1.0 - progress) * width)
            painter.translate(offset_x, 0)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x - offset_x, y, width, height)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Right" or (is_singleline and anim_type == "Continuous Move Right"):
            offset_x = int(-(1.0 - progress) * width)
            painter.translate(offset_x, 0)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x - offset_x, y, width, height)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Up":
            offset_y = int((1.0 - progress) * height)
            painter.translate(0, offset_y)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x, y - offset_y, width, height)
            painter.setClipRect(x, y - offset_y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Down":
            offset_y = int(-(1.0 - progress) * height)
            painter.translate(0, offset_y)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x, y - offset_y, width, height)
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
            # Default: fade in
            painter.setOpacity(progress)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
            painter.setOpacity(1.0)
        
        painter.restore()
        # Ensure clipping is disabled after animation
        painter.setClipping(False)
    
    def _apply_text_exit_animation(self, painter, text_content, text_format, element_props, x, y, width, height, anim_type, progress, scale, is_singleline=False):
        # Set clipping to element bounds to prevent text from displaying outside
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        # Handle Immediate Show or None: don't show exit animation
        if anim_type == "Immediate Show" or anim_type == "None" or (is_singleline and anim_type == "Don't Clear Screen"):
            painter.setClipping(False)
            return
        
        # Save painter state
        painter.save()
        
        # Apply specific exit animations (reversed from entrance)
        if anim_type == "Move Left" or (is_singleline and anim_type == "Continuous Move Left"):
            offset_x = int(-progress * width)
            painter.translate(offset_x, 0)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x - offset_x, y, width, height)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Right" or (is_singleline and anim_type == "Continuous Move Right"):
            offset_x = int(progress * width)
            painter.translate(offset_x, 0)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x - offset_x, y, width, height)
            painter.setClipRect(x - offset_x, y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Up":
            offset_y = int(-progress * height)
            painter.translate(0, offset_y)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x, y - offset_y, width, height)
            painter.setClipRect(x, y - offset_y, width, height)
            self._draw_text_static(painter, text_content, text_format, element_props, x, y, width, height, None, False, scale, is_singleline)
        elif anim_type == "Move Down":
            offset_y = int(progress * height)
            painter.translate(0, offset_y)
            # After translation, adjust clipping rectangle to account for translation
            # In translated coordinate space, original bounds become (x, y - offset_y, width, height)
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
            # Default: fade out
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
                video_path = video_list[0].get("path", "")
                if video_path:
                    self._setup_video_player(element_id, video_path)
                    self._update_video_widget_position(element_id, scaled_x, scaled_y, scaled_width, scaled_height)
                    return
            
            if element_id not in self._video_widgets or not self._video_widgets[element_id].isVisible():
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 50, 50)))
                painter.drawRect(element_rect)
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
                painter.drawText(element_rect, Qt.AlignCenter, "VIDEO")
        elif element_type == "photo":
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
            painter.setBrush(QtGui.QBrush(QtGui.QColor(80, 80, 80)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "PHOTO")
        elif element_type == "text":
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
                painter.setBrush(QtGui.QBrush(QtGui.QColor(120, 120, 120)))
                painter.drawRect(element_rect)
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
                painter.drawText(element_rect, Qt.AlignCenter, "TEXT")
                if is_selected:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
                    painter.drawRect(element_rect)
        elif element_type == "singleline_text":
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
                painter.setBrush(QtGui.QBrush(QtGui.QColor(100, 120, 120)))
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
            painter.setPen(QtGui.QPen(QtGui.QColor(128, 0, 128) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(100, 80, 100)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "TIME")
        elif element_type == "weather":
            painter.setPen(QtGui.QPen(QtGui.QColor(135, 206, 250) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(80, 100, 120)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "WEATHER")
        elif element_type == "sensor":
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 20, 147) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(120, 80, 100)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "SENSOR")
        elif element_type == "html":
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 191, 255) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(80, 120, 140)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "HTML")
        elif element_type == "hdmi":
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 140, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(140, 100, 60)))
            painter.drawRect(element_rect)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawText(element_rect, Qt.AlignCenter, "HDMI")
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 0) if is_selected else QtGui.QColor(100, 100, 100), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(100, 100, 100)))
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
            painter.setBrush(QtGui.QBrush(QtGui.QColor(120, 100, 100)))
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
            painter.setBrush(QtGui.QBrush(QtGui.QColor(120, 100, 80)))
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
            painter.setBrush(QtGui.QBrush(QtGui.QColor(120, 100, 80)))
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
        
        # Initialize animation state
        if element_id not in self._text_flow_animations:
            self._text_flow_animations[element_id] = {
                "start_time": QtCore.QDateTime.currentDateTime(),
                "char_index": 0
            }
            if not self._animation_timer.isActive():
                self._animation_timer.start()
        
        anim_state = self._text_flow_animations[element_id]
        
        # Get animation properties
        gradient_colors = animation_style.get("gradient_colors", ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"])
        writing_direction = animation_style.get("writing_direction", "Horizontal Line Writing")
        character_movement = animation_style.get("character_movement", True)
        speed = animation_style.get("speed", 10)
        
        # Calculate elapsed time and character position
        elapsed_ms = anim_state["start_time"].msecsTo(QtCore.QDateTime.currentDateTime())
        elapsed_sec = elapsed_ms / 1000.0
        
        if character_movement:
            chars_to_show = int(elapsed_sec * speed)
            chars_to_show = min(chars_to_show, len(text_content))
        else:
            chars_to_show = len(text_content)
        
        # Setup font
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
        
        # Get character spacing
        char_spacing = text_format.get("char_spacing", 0)
        
        # Set clipping
        element_bounds = QtCore.QRect(x, y, width, height)
        painter.setClipRect(element_bounds)
        
        # Draw text with gradient colors
        font_metrics = painter.fontMetrics()
        current_x = x
        current_y = y + font_metrics.ascent()
        
        displayed_text = text_content[:chars_to_show] if character_movement else text_content
        
        for i, char in enumerate(displayed_text):
            # Calculate gradient color index (cycling through 7 colors)
            color_index = i % len(gradient_colors)
            color = QtGui.QColor(gradient_colors[color_index])
            
            # Apply gradient flow effect (shift colors based on time)
            if len(gradient_colors) == 7:
                time_offset = int(elapsed_sec * 2) % 7
                color_index = (i + time_offset) % 7
                color = QtGui.QColor(gradient_colors[color_index])
            
            painter.setPen(QtGui.QPen(color))
            
            # Check for hollow text
            if text_format.get("hollow", False):
                # Draw outline for hollow effect
                outline_pen = QtGui.QPen(color, 2)
                painter.setPen(outline_pen)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            painter.drawText(current_x + dx, current_y + dy, char)
                painter.setPen(QtGui.QPen(color))
            else:
                painter.drawText(current_x, current_y, char)
            
            # Move to next character position
            char_width = font_metrics.width(char)
            if writing_direction == "Horizontal Line Writing":
                current_x += char_width + char_spacing
                # Check if we need to wrap to next line
                if current_x + char_width > x + width and i < len(displayed_text) - 1:
                    current_x = x
                    current_y += font_metrics.height()
            else:  # Vertical Line Writing
                current_y += font_metrics.height()
                # Check if we need to wrap to next column
                if current_y > y + height and i < len(displayed_text) - 1:
                    current_y = y + font_metrics.ascent()
                    current_x += font_metrics.maxWidth() + char_spacing
        
        painter.setClipping(False)
        
        if is_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
            painter.drawRect(element_rect)

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
                
                for widget in self._video_widgets.values():
                    widget.hide()
                
                self._cleanup_video_players()
                
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
                
                painter.setClipping(False)
        
        painter.end()

    def _on_property_changed(self, property_name: str, value):
        """Handle property changes from properties panel"""
        # Update content widget when any property changes
        self.update()
    
    def _update_clocks(self):
        """Update clock displays - called every second"""
        # Check if there are any clock elements
        if not self.screen_manager or not self.screen_manager.current_screen:
            return
        
        has_clock = False
        for program in self.screen_manager.current_screen.programs:
            for element in program.elements:
                if element.get("type", "").lower() == "clock":
                    has_clock = True
                    break
            if has_clock:
                break
        
        if has_clock:
            self.update()
    
    def resizeEvent(self, event):
        self._cached_pixmap = None
        super().resizeEvent(event)
        self.update()
