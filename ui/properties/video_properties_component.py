from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QSpinBox, QPushButton, QFileDialog, QLineEdit,
                             QGroupBox, QFormLayout, QTimeEdit, QCheckBox)
from PyQt5.QtCore import Qt, QTime
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent
from ui.widgets.video_icon_view import VideoIconView


class VideoPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        area_group = QGroupBox("Area Attribute")
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(6, 6, 6, 6)
        area_layout.setSpacing(4)
        
        layout_section = QVBoxLayout()
        layout_section.setSpacing(4)
        layout_section.setAlignment(Qt.AlignTop)
        
        coords_layout = QHBoxLayout()
        coords_layout.setSpacing(2)
        coords_label = QLabel("📍")
        self.video_coords_x = QLineEdit()
        self.video_coords_x.setPlaceholderText("0")
        self.video_coords_x.setMinimumWidth(60)
        self.video_coords_x.setText("0")
        coords_comma = QLabel(",")
        self.video_coords_y = QLineEdit()
        self.video_coords_y.setPlaceholderText("0")
        self.video_coords_y.setMinimumWidth(60)
        self.video_coords_y.setText("0")
        coords_layout.addWidget(coords_label)
        coords_layout.addWidget(self.video_coords_x)
        coords_layout.addWidget(coords_comma)
        coords_layout.addWidget(self.video_coords_y)
        coords_layout.addStretch()
        layout_section.addLayout(coords_layout)
        
        dims_layout = QHBoxLayout()
        dims_layout.setSpacing(2)
        dims_label = QLabel("📐")
        self.video_dims_width = QLineEdit()
        self.video_dims_width.setPlaceholderText("1920")
        self.video_dims_width.setMinimumWidth(60)
        self.video_dims_width.setText("1920")
        dims_comma = QLabel(",")
        self.video_dims_height = QLineEdit()
        self.video_dims_height.setPlaceholderText("1080")
        self.video_dims_height.setMinimumWidth(60)
        self.video_dims_height.setText("1080")
        dims_layout.addWidget(dims_label)
        dims_layout.addWidget(self.video_dims_width)
        dims_layout.addWidget(dims_comma)
        dims_layout.addWidget(self.video_dims_height)
        dims_layout.addStretch()
        layout_section.addLayout(dims_layout)
        
        area_layout.addLayout(layout_section)
        
        self.video_coords_x.textChanged.connect(self._on_video_coords_changed)
        self.video_coords_y.textChanged.connect(self._on_video_coords_changed)
        self.video_dims_width.textChanged.connect(self._on_video_dims_changed)
        self.video_dims_height.textChanged.connect(self._on_video_dims_changed)
        
        layout.addWidget(area_group)
        
        video_list_group = QGroupBox("Video List")
        video_list_group.setMinimumWidth(400)
        video_list_layout = QHBoxLayout(video_list_group)
        video_list_layout.setAlignment(Qt.AlignCenter)
        
        self.video_list = VideoIconView()
        self.video_list.setMinimumHeight(150)
        self.video_list.item_selected.connect(self._on_video_item_selected)
        self.video_list.item_deleted.connect(self._on_video_item_deleted)
        video_list_layout.addWidget(self.video_list, stretch=1)
        
        video_buttons_layout = QVBoxLayout()
        video_buttons_layout.setContentsMargins(0, 0, 0, 0)
        video_buttons_layout.setSpacing(4)
        video_buttons_layout.setAlignment(Qt.AlignCenter)
        
        self.video_add_btn = QPushButton("➕")
        self.video_add_btn.clicked.connect(self._on_video_add)
        self.video_delete_btn = QPushButton("🗑")
        self.video_delete_btn.clicked.connect(self._on_video_delete)
        self.video_up_btn = QPushButton("🔼")
        self.video_up_btn.clicked.connect(self._on_video_up)
        self.video_down_btn = QPushButton("🔽")
        self.video_down_btn.clicked.connect(self._on_video_down)
        
        video_buttons_layout.addWidget(self.video_add_btn)
        video_buttons_layout.addWidget(self.video_delete_btn)
        video_buttons_layout.addWidget(self.video_up_btn)
        video_buttons_layout.addWidget(self.video_down_btn)
        video_buttons_layout.addStretch()
        
        video_list_layout.addLayout(video_buttons_layout)
        
        layout.addWidget(video_list_group, stretch=1)
        
        video_shot_group = QGroupBox("Video Shot")
        video_shot_group.setMinimumWidth(250)
        video_shot_layout = QFormLayout(video_shot_group)
        
        self.video_shot_width_spin = QSpinBox()
        self.video_shot_width_spin.setMinimum(1)
        self.video_shot_width_spin.setMaximum(99999)
        self.video_shot_width_spin.valueChanged.connect(self._on_video_shot_size_changed)
        video_shot_layout.addRow("Width:", self.video_shot_width_spin)
        
        self.video_shot_height_spin = QSpinBox()
        self.video_shot_height_spin.setMinimum(1)
        self.video_shot_height_spin.setMaximum(99999)
        self.video_shot_height_spin.valueChanged.connect(self._on_video_shot_size_changed)
        video_shot_layout.addRow("Height:", self.video_shot_height_spin)
        
        self.video_shot_start_time = QTimeEdit()
        self.video_shot_start_time.setDisplayFormat("HH:mm:ss")
        self.video_shot_start_time.setTime(QTime(0, 0, 0))
        self.video_shot_start_time.timeChanged.connect(self._on_video_shot_time_changed)
        video_shot_layout.addRow("Start time:", self.video_shot_start_time)
        
        self.video_shot_end_time = QTimeEdit()
        self.video_shot_end_time.setDisplayFormat("HH:mm:ss")
        self.video_shot_end_time.setTime(QTime(0, 0, 30))
        self.video_shot_end_time.timeChanged.connect(self._on_video_shot_time_changed)
        video_shot_layout.addRow("End time:", self.video_shot_end_time)
        
        self.video_shot_duration_label = QLabel("00:00:30")
        video_shot_layout.addRow("Duration:", self.video_shot_duration_label)
        
        layout.addWidget(video_shot_group)
    
    def set_program_data(self, program, element):
        self.set_element(element, program)
        self.update_properties()
    
    def update_properties(self):
        if not self.current_element or not self.current_program:
            return
        
        screen_width, screen_height = self._get_screen_bounds()
        default_width = screen_width if screen_width else 1920
        default_height = screen_height if screen_height else 1080
        
        element_props = self.current_element.get("properties", {})
        
        x = element_props.get("x", 0)
        y = element_props.get("y", 0)
        self.video_coords_x.blockSignals(True)
        self.video_coords_y.blockSignals(True)
        self.video_coords_x.setText(str(x))
        self.video_coords_y.setText(str(y))
        self.video_coords_x.blockSignals(False)
        self.video_coords_y.blockSignals(False)
        
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        if not width or width <= 0:
            width = default_width
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["width"] = width
            self.current_element["width"] = width
        
        if not height or height <= 0:
            height = default_height
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["height"] = height
            self.current_element["height"] = height
        
        self.video_dims_width.blockSignals(True)
        self.video_dims_height.blockSignals(True)
        self.video_dims_width.setText(str(width))
        self.video_dims_height.setText(str(height))
        self.video_dims_width.blockSignals(False)
        self.video_dims_height.blockSignals(False)
        frame_props = element_props.get("frame", {})
        if hasattr(self, 'video_frame_checkbox'):
            frame_enabled = frame_props.get("enabled", False) if isinstance(frame_props, dict) else False
            self.video_frame_checkbox.blockSignals(True)
            self.video_frame_checkbox.setChecked(frame_enabled)
            self.video_frame_checkbox.setEnabled(True)
            self.video_frame_checkbox.blockSignals(False)
            
            if hasattr(self, 'video_frame_border_combo'):
                self.video_frame_border_combo.setEnabled(frame_enabled)
            if hasattr(self, 'video_frame_effect_combo'):
                self.video_frame_effect_combo.setEnabled(frame_enabled)
            if hasattr(self, 'video_frame_speed_combo'):
                self.video_frame_speed_combo.setEnabled(frame_enabled)
            
            if hasattr(self, 'video_frame_border_combo'):
                border = frame_props.get("border", "---")
                border_index = self.video_frame_border_combo.findText(border)
                if border_index >= 0:
                    self.video_frame_border_combo.setCurrentIndex(border_index)
                else:
                    self.video_frame_border_combo.setCurrentIndex(0)
            
            if hasattr(self, 'video_frame_effect_combo'):
                effect = frame_props.get("effect", "static")
                effect_index = self.video_frame_effect_combo.findText(effect)
                if effect_index >= 0:
                    self.video_frame_effect_combo.setCurrentIndex(effect_index)
                else:
                    self.video_frame_effect_combo.setCurrentIndex(0)
            
            if hasattr(self, 'video_frame_speed_combo'):
                speed = frame_props.get("speed", "in")
                speed_index = self.video_frame_speed_combo.findText(speed)
                if speed_index >= 0:
                    self.video_frame_speed_combo.setCurrentIndex(speed_index)
                else:
                    self.video_frame_speed_combo.setCurrentIndex(1)
        
        video_list = element_props.get("video_list", [])
        self.video_list.set_videos(video_list)
        
        video_shot = element_props.get("video_shot", {})
        video_shot_width = video_shot.get("width", default_width)
        video_shot_height = video_shot.get("height", default_height)
        
        if video_shot_width < 10 or video_shot_height < 10:
            video_shot_width = default_width
            video_shot_height = default_height
            if "video_shot" not in element_props:
                element_props["video_shot"] = {}
            element_props["video_shot"]["width"] = video_shot_width
            element_props["video_shot"]["height"] = video_shot_height
        
        self.video_shot_width_spin.setValue(video_shot_width)
        self.video_shot_height_spin.setValue(video_shot_height)
        
        start_time_str = video_shot.get("start_time", "00:00:00")
        time_parts = start_time_str.split(":")
        if len(time_parts) == 3:
            self.video_shot_start_time.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2])))
        
        end_time_str = video_shot.get("end_time", "00:00:30")
        time_parts = end_time_str.split(":")
        if len(time_parts) == 3:
            self.video_shot_end_time.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2])))
        
        self._update_duration()
    
    def _update_duration(self):
        start = self.video_shot_start_time.time()
        end = self.video_shot_end_time.time()
        start_secs = start.hour() * 3600 + start.minute() * 60 + start.second()
        end_secs = end.hour() * 3600 + end.minute() * 60 + end.second()
        duration_secs = max(0, end_secs - start_secs)
        hours = duration_secs // 3600
        minutes = (duration_secs % 3600) // 60
        seconds = duration_secs % 60
        self.video_shot_duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def _on_video_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        
        try:
            x = int(self.video_coords_x.text() or "0")
            y = int(self.video_coords_y.text() or "0")
        except ValueError:
            return
        
        try:
            width = int(self.video_dims_width.text() or "1920")
            height = int(self.video_dims_height.text() or "1080")
        except ValueError:
            width = self.current_element.get("width", 1920)
            height = self.current_element.get("height", 1080)
        
        x, y, width, height = self._constrain_to_screen(x, y, width, height)
        
        if x != int(self.video_coords_x.text() or "0") or y != int(self.video_coords_y.text() or "0"):
            self.video_coords_x.blockSignals(True)
            self.video_coords_y.blockSignals(True)
            self.video_coords_x.setText(str(x))
            self.video_coords_y.setText(str(y))
            self.video_coords_x.blockSignals(False)
            self.video_coords_y.blockSignals(False)
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        self.current_element["properties"]["x"] = x
        self.current_element["properties"]["y"] = y
        self.current_element["x"] = x
        self.current_element["y"] = y
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("video_position", (x, y))
        self._trigger_autosave()
    
    def _on_video_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        
        try:
            width = int(self.video_dims_width.text() or "1920")
            height = int(self.video_dims_height.text() or "1080")
        except ValueError:
            return
        
        if width <= 0:
            width = 1
        if height <= 0:
            height = 1
        
        try:
            x = int(self.video_coords_x.text() or "0")
            y = int(self.video_coords_y.text() or "0")
        except ValueError:
            x = self.current_element.get("x", 0)
            y = self.current_element.get("y", 0)
        
        x, y, width, height = self._constrain_to_screen(x, y, width, height)
        
        if width != int(self.video_dims_width.text() or "1920") or height != int(self.video_dims_height.text() or "1080"):
            self.video_dims_width.blockSignals(True)
            self.video_dims_height.blockSignals(True)
            self.video_dims_width.setText(str(width))
            self.video_dims_height.setText(str(height))
            self.video_dims_width.blockSignals(False)
            self.video_dims_height.blockSignals(False)
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        self.current_element["properties"]["width"] = width
        self.current_element["properties"]["height"] = height
        self.current_element["width"] = width
        self.current_element["height"] = height
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("video_size", (width, height))
        self._trigger_autosave()
    
    def _on_video_frame_enabled_changed(self, enabled: bool):
        if not hasattr(self, 'video_frame_checkbox'):
            return
        if not self.current_element or not self.current_program:
            self.video_frame_checkbox.blockSignals(True)
            self.video_frame_checkbox.setEnabled(False)
            self.video_frame_checkbox.setChecked(False)
            self.video_frame_checkbox.blockSignals(False)
            return
        
        self.video_frame_checkbox.setEnabled(True)
        
        self.video_frame_border_combo.setEnabled(enabled)
        self.video_frame_effect_combo.setEnabled(enabled)
        self.video_frame_speed_combo.setEnabled(enabled)
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["enabled"] = enabled
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("video_frame_enabled", enabled)
        self._trigger_autosave()
    
    def _on_video_frame_border_changed(self, border: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["border"] = border
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("video_frame_border", border)
        self._trigger_autosave()
    
    def _on_video_frame_effect_changed(self, effect: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["effect"] = effect
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("video_frame_effect", effect)
        self._trigger_autosave()
    
    def _on_video_frame_speed_changed(self, speed: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("video_frame_speed", speed)
        self._trigger_autosave()
    
    def _on_video_add(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        if file_path:
            if self.current_element:
                if "properties" not in self.current_element:
                    self.current_element["properties"] = {}
                if "video_list" not in self.current_element["properties"]:
                    self.current_element["properties"]["video_list"] = []
                self.current_element["properties"]["video_list"].append({"path": file_path})
                self.video_list.add_item(file_path)
                self.property_changed.emit("video_list", self.current_element["properties"]["video_list"])
                self._trigger_autosave()
    
    def _on_video_item_selected(self, index: int):
        pass
    
    def _on_video_item_deleted(self, index: int):
        if self.current_element and self.current_program:
            if "properties" in self.current_element and "video_list" in self.current_element["properties"]:
                self.current_element["properties"]["video_list"].pop(index)
                self.video_list.remove_item(index)
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("video_list", self.current_element["properties"]["video_list"])
                self._trigger_autosave()
    
    def _on_video_delete(self):
        current_index = self.video_list.get_current_index()
        if current_index >= 0 and self.current_element and self.current_program:
            if "properties" in self.current_element and "video_list" in self.current_element["properties"]:
                video_list = self.current_element["properties"]["video_list"]
                if 0 <= current_index < len(video_list):
                    self.current_element["properties"]["video_list"].pop(current_index)
                    self.video_list.remove_item(current_index)
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("video_list", self.current_element["properties"]["video_list"])
                self._trigger_autosave()
    
    def _on_video_up(self):
        current_index = self.video_list.get_current_index()
        if current_index > 0 and self.current_element and self.current_program:
            if "properties" in self.current_element and "video_list" in self.current_element["properties"]:
                video_list = self.current_element["properties"]["video_list"]
                new_index = self.video_list.move_item_up(current_index)
                video_list[current_index], video_list[current_index - 1] = video_list[current_index - 1], video_list[current_index]
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("video_list", video_list)
                self._trigger_autosave()
    
    def _on_video_down(self):
        current_index = self.video_list.get_current_index()
        if self.current_element and self.current_program and "properties" in self.current_element and "video_list" in self.current_element["properties"]:
            video_list = self.current_element["properties"]["video_list"]
            if 0 <= current_index < len(video_list) - 1:
                new_index = self.video_list.move_item_down(current_index)
                video_list[current_index], video_list[current_index + 1] = video_list[current_index + 1], video_list[current_index]
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("video_list", video_list)
                self._trigger_autosave()
    
    def _on_video_shot_size_changed(self):
        if not self.current_element:
            return
        
        width = self.video_shot_width_spin.value()
        height = self.video_shot_height_spin.value()
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "video_shot" not in self.current_element["properties"]:
            self.current_element["properties"]["video_shot"] = {}
        
        self.current_element["properties"]["video_shot"]["width"] = width
        self.current_element["properties"]["video_shot"]["height"] = height
        self.property_changed.emit("video_shot_size", (width, height))
    
    def _on_video_shot_time_changed(self):
        if self.current_element:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "video_shot" not in self.current_element["properties"]:
                self.current_element["properties"]["video_shot"] = {}
            
            start_str = self.video_shot_start_time.time().toString("HH:mm:ss")
            end_str = self.video_shot_end_time.time().toString("HH:mm:ss")
            
            self.current_element["properties"]["video_shot"]["start_time"] = start_str
            self.current_element["properties"]["video_shot"]["end_time"] = end_str
            
            self._update_duration()

