from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox)
from PyQt5.QtCore import Qt
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class SensorPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)
        main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        area_group = QGroupBox("Area attribute")
        area_group.setMaximumWidth(200)
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(10, 16, 10, 10)
        area_layout.setSpacing(8)
        area_layout.setAlignment(Qt.AlignTop)
        
        coords_row = QHBoxLayout()
        coords_row.setSpacing(6)
        coords_label = QLabel("📍")
        coords_label.setStyleSheet("font-size: 16px;")
        self.sensor_coords_x = QLineEdit()
        self.sensor_coords_x.setPlaceholderText("0")
        self.sensor_coords_x.setMinimumWidth(70)
        self.sensor_coords_x.setText("0")
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.sensor_coords_y = QLineEdit()
        self.sensor_coords_y.setPlaceholderText("0")
        self.sensor_coords_y.setMinimumWidth(70)
        self.sensor_coords_y.setText("0")
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.sensor_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.sensor_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.sensor_dims_width = QLineEdit()
        self.sensor_dims_width.setPlaceholderText("1920")
        self.sensor_dims_width.setMinimumWidth(70)
        self.sensor_dims_width.setText("1920")
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.sensor_dims_height = QLineEdit()
        self.sensor_dims_height.setPlaceholderText("1080")
        self.sensor_dims_height.setMinimumWidth(70)
        self.sensor_dims_height.setText("1080")
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.sensor_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.sensor_dims_height)
        area_layout.addLayout(dims_row)
        
        area_layout.addStretch()
        
        self.sensor_coords_x.textChanged.connect(self._on_coords_changed)
        self.sensor_coords_y.textChanged.connect(self._on_coords_changed)
        self.sensor_dims_width.textChanged.connect(self._on_dims_changed)
        self.sensor_dims_height.textChanged.connect(self._on_dims_changed)
        
        frame_group_layout = QVBoxLayout()
        frame_group_layout.setSpacing(4)
        
        frame_checkbox_layout = QHBoxLayout()
        self.sensor_frame_checkbox = QCheckBox("Frame")
        self.sensor_frame_checkbox.toggled.connect(self._on_frame_enabled_changed)
        frame_checkbox_layout.addWidget(self.sensor_frame_checkbox)
        frame_checkbox_layout.addStretch()
        frame_group_layout.addLayout(frame_checkbox_layout)
        
        border_layout = QHBoxLayout()
        border_layout.addWidget(QLabel("Border:"))
        self.sensor_frame_border_combo = QComboBox()
        borders = self.get_available_borders()
        if borders:
            self.sensor_frame_border_combo.addItems(["---"] + borders)
        else:
            self.sensor_frame_border_combo.addItems(["---", "000", "001", "002", "003"])
        self.sensor_frame_border_combo.setCurrentText("---")
        self.sensor_frame_border_combo.setEnabled(False)
        self.sensor_frame_border_combo.currentTextChanged.connect(self._on_frame_border_changed)
        border_layout.addWidget(self.sensor_frame_border_combo, stretch=1)
        frame_group_layout.addLayout(border_layout)
        
        effect_layout = QHBoxLayout()
        effect_layout.addWidget(QLabel("Effect:"))
        self.sensor_frame_effect_combo = QComboBox()
        self.sensor_frame_effect_combo.addItems(["static", "rotate", "twinkle"])
        self.sensor_frame_effect_combo.setCurrentText("static")
        self.sensor_frame_effect_combo.setEnabled(False)
        self.sensor_frame_effect_combo.currentTextChanged.connect(self._on_frame_effect_changed)
        effect_layout.addWidget(self.sensor_frame_effect_combo, stretch=1)
        frame_group_layout.addLayout(effect_layout)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.sensor_frame_speed_combo = QComboBox()
        self.sensor_frame_speed_combo.addItems(["slow", "in", "fast"])
        self.sensor_frame_speed_combo.setCurrentText("in")
        self.sensor_frame_speed_combo.setEnabled(False)
        self.sensor_frame_speed_combo.currentTextChanged.connect(self._on_frame_speed_changed)
        speed_layout.addWidget(self.sensor_frame_speed_combo, stretch=1)
        frame_group_layout.addLayout(speed_layout)
        
        area_layout.addLayout(frame_group_layout)
        
        main_layout.addWidget(area_group)
        main_layout.addStretch()
    
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
        self.sensor_coords_x.blockSignals(True)
        self.sensor_coords_y.blockSignals(True)
        self.sensor_coords_x.setText(str(x))
        self.sensor_coords_y.setText(str(y))
        self.sensor_coords_x.blockSignals(False)
        self.sensor_coords_y.blockSignals(False)
        
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        if not width or width <= 0:
            width = default_width
        if not height or height <= 0:
            height = default_height
        
        self.sensor_dims_width.blockSignals(True)
        self.sensor_dims_height.blockSignals(True)
        self.sensor_dims_width.setText(str(width))
        self.sensor_dims_height.setText(str(height))
        self.sensor_dims_width.blockSignals(False)
        self.sensor_dims_height.blockSignals(False)
        
        frame_props = element_props.get("frame", {})
        frame_enabled = frame_props.get("enabled", False) if isinstance(frame_props, dict) else False
        self.sensor_frame_checkbox.blockSignals(True)
        self.sensor_frame_checkbox.setChecked(frame_enabled)
        self.sensor_frame_checkbox.setEnabled(True)
        self.sensor_frame_checkbox.blockSignals(False)
        
        self.sensor_frame_border_combo.setEnabled(frame_enabled)
        self.sensor_frame_effect_combo.setEnabled(frame_enabled)
        self.sensor_frame_speed_combo.setEnabled(frame_enabled)
        
        border = frame_props.get("border", "---") if isinstance(frame_props, dict) else "---"
        border_index = self.sensor_frame_border_combo.findText(border)
        if border_index >= 0:
            self.sensor_frame_border_combo.setCurrentIndex(border_index)
        else:
            self.sensor_frame_border_combo.setCurrentIndex(0)
        
        effect = frame_props.get("effect", "static") if isinstance(frame_props, dict) else "static"
        effect_index = self.sensor_frame_effect_combo.findText(effect)
        if effect_index >= 0:
            self.sensor_frame_effect_combo.setCurrentIndex(effect_index)
        else:
            self.sensor_frame_effect_combo.setCurrentIndex(0)
        
        speed = frame_props.get("speed", "in") if isinstance(frame_props, dict) else "in"
        speed_index = self.sensor_frame_speed_combo.findText(speed)
        if speed_index >= 0:
            self.sensor_frame_speed_combo.setCurrentIndex(speed_index)
        else:
            self.sensor_frame_speed_combo.setCurrentIndex(1)
    
    def _on_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            x = int(self.sensor_coords_x.text() or "0")
            y = int(self.sensor_coords_y.text() or "0")
            screen_width, screen_height = self._get_screen_bounds()
            default_width = screen_width if screen_width else 640
            default_height = screen_height if screen_height else 480
            element_props = self.current_element.get("properties", {})
            width = element_props.get("width", default_width)
            height = element_props.get("height", default_height)
            x, y, width, height = self._constrain_to_screen(x, y, width, height)
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["x"] = x
            self.current_element["properties"]["y"] = y
            self.current_element["x"] = x
            self.current_element["y"] = y
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("sensor_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            width = int(self.sensor_dims_width.text() or "640")
            height = int(self.sensor_dims_height.text() or "480")
            element_props = self.current_element.get("properties", {})
            x = element_props.get("x", 0)
            y = element_props.get("y", 0)
            x, y, width, height = self._constrain_to_screen(x, y, width, height)
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["width"] = width
            self.current_element["properties"]["height"] = height
            self.current_element["width"] = width
            self.current_element["height"] = height
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("sensor_size", (width, height))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_frame_enabled_changed(self, enabled: bool):
        if not self.current_element or not self.current_program:
            self.sensor_frame_checkbox.blockSignals(True)
            self.sensor_frame_checkbox.setEnabled(False)
            self.sensor_frame_checkbox.setChecked(False)
            self.sensor_frame_checkbox.blockSignals(False)
            return
        
        self.sensor_frame_checkbox.setEnabled(True)
        self.sensor_frame_border_combo.setEnabled(enabled)
        self.sensor_frame_effect_combo.setEnabled(enabled)
        self.sensor_frame_speed_combo.setEnabled(enabled)
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        self.current_element["properties"]["frame"]["enabled"] = enabled
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_frame_enabled", enabled)
        self._trigger_autosave()
    
    def _on_frame_border_changed(self, border: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        self.current_element["properties"]["frame"]["border"] = border
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_frame_border", border)
        self._trigger_autosave()
    
    def _on_frame_effect_changed(self, effect: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        self.current_element["properties"]["frame"]["effect"] = effect
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_frame_effect", effect)
        self._trigger_autosave()
    
    def _on_frame_speed_changed(self, speed: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        self.current_element["properties"]["frame"]["speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_frame_speed", speed)
        self._trigger_autosave()

