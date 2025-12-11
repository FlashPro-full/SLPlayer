from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox)
from PyQt5.QtCore import Qt
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class HdmiPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)
        main_layout.setAlignment(Qt.AlignTop)
        
        area_group = QGroupBox("Area attribute")
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(10, 16, 10, 10)
        area_layout.setSpacing(8)
        area_layout.setAlignment(Qt.AlignTop)
        
        coords_row = QHBoxLayout()
        coords_row.setSpacing(6)
        coords_label = QLabel("📍")
        coords_label.setStyleSheet("font-size: 16px;")
        self.hdmi_coords_x = QLineEdit()
        self.hdmi_coords_x.setPlaceholderText("0")
        self.hdmi_coords_x.setMinimumWidth(70)
        self.hdmi_coords_x.setText("0")
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.hdmi_coords_y = QLineEdit()
        self.hdmi_coords_y.setPlaceholderText("0")
        self.hdmi_coords_y.setMinimumWidth(70)
        self.hdmi_coords_y.setText("0")
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.hdmi_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.hdmi_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.hdmi_dims_width = QLineEdit()
        self.hdmi_dims_width.setPlaceholderText("1920")
        self.hdmi_dims_width.setMinimumWidth(70)
        self.hdmi_dims_width.setText("1920")
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.hdmi_dims_height = QLineEdit()
        self.hdmi_dims_height.setPlaceholderText("1080")
        self.hdmi_dims_height.setMinimumWidth(70)
        self.hdmi_dims_height.setText("1080")
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.hdmi_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.hdmi_dims_height)
        area_layout.addLayout(dims_row)
        
        area_layout.addStretch()
        
        self.hdmi_coords_x.textChanged.connect(self._on_coords_changed)
        self.hdmi_coords_y.textChanged.connect(self._on_coords_changed)
        self.hdmi_dims_width.textChanged.connect(self._on_dims_changed)
        self.hdmi_dims_height.textChanged.connect(self._on_dims_changed)
        
        main_layout.addWidget(area_group)
        
        display_group = QGroupBox("Display attribute")
        display_layout = QVBoxLayout(display_group)
        display_layout.setContentsMargins(10, 16, 10, 10)
        display_layout.setSpacing(8)
        
        display_mode_layout = QHBoxLayout()
        display_mode_layout.addWidget(QLabel("Display Mode:"))
        self.hdmi_display_mode_combo = QComboBox()
        self.hdmi_display_mode_combo.addItems(["Full Screen Zoom", "Screen Capture"])
        self.hdmi_display_mode_combo.setCurrentText("Full Screen Zoom")
        self.hdmi_display_mode_combo.currentTextChanged.connect(self._on_display_mode_changed)
        display_mode_layout.addWidget(self.hdmi_display_mode_combo, stretch=1)
        display_layout.addLayout(display_mode_layout)
        
        display_layout.addStretch()
        main_layout.addWidget(display_group)
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
        self.hdmi_coords_x.blockSignals(True)
        self.hdmi_coords_y.blockSignals(True)
        self.hdmi_coords_x.setText(str(x))
        self.hdmi_coords_y.setText(str(y))
        self.hdmi_coords_x.blockSignals(False)
        self.hdmi_coords_y.blockSignals(False)
        
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        if not width or width <= 0:
            width = default_width
        if not height or height <= 0:
            height = default_height
        
        self.hdmi_dims_width.blockSignals(True)
        self.hdmi_dims_height.blockSignals(True)
        self.hdmi_dims_width.setText(str(width))
        self.hdmi_dims_height.setText(str(height))
        self.hdmi_dims_width.blockSignals(False)
        self.hdmi_dims_height.blockSignals(False)
        
        hdmi_props = element_props.get("hdmi", {})
        display_mode = hdmi_props.get("display_mode", "Full Screen Zoom") if isinstance(hdmi_props, dict) else "Full Screen Zoom"
        display_mode_index = self.hdmi_display_mode_combo.findText(display_mode)
        if display_mode_index >= 0:
            self.hdmi_display_mode_combo.blockSignals(True)
            self.hdmi_display_mode_combo.setCurrentIndex(display_mode_index)
            self.hdmi_display_mode_combo.blockSignals(False)
    
    def _on_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            x = int(self.hdmi_coords_x.text() or "0")
            y = int(self.hdmi_coords_y.text() or "0")
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
            self.property_changed.emit("hdmi_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            width = int(self.hdmi_dims_width.text() or "640")
            height = int(self.hdmi_dims_height.text() or "480")
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
            self.property_changed.emit("hdmi_size", (width, height))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_display_mode_changed(self, display_mode: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "hdmi" not in self.current_element["properties"]:
            self.current_element["properties"]["hdmi"] = {}
        self.current_element["properties"]["hdmi"]["display_mode"] = display_mode
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("hdmi_display_mode", display_mode)
        self._trigger_autosave()

