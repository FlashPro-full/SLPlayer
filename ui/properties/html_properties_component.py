from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class HtmlPropertiesComponent(BasePropertiesComponent):
    
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
        self.html_coords_x = QLineEdit()
        self.html_coords_x.setPlaceholderText("0")
        self.html_coords_x.setMinimumWidth(70)
        self.html_coords_x.setText("0")
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.html_coords_y = QLineEdit()
        self.html_coords_y.setPlaceholderText("0")
        self.html_coords_y.setMinimumWidth(70)
        self.html_coords_y.setText("0")
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.html_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.html_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.html_dims_width = QLineEdit()
        self.html_dims_width.setPlaceholderText("1920")
        self.html_dims_width.setMinimumWidth(70)
        self.html_dims_width.setText("1920")
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.html_dims_height = QLineEdit()
        self.html_dims_height.setPlaceholderText("1080")
        self.html_dims_height.setMinimumWidth(70)
        self.html_dims_height.setText("1080")
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.html_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.html_dims_height)
        area_layout.addLayout(dims_row)
        
        area_layout.addStretch()
        
        self.html_coords_x.textChanged.connect(self._on_coords_changed)
        self.html_coords_y.textChanged.connect(self._on_coords_changed)
        self.html_dims_width.textChanged.connect(self._on_dims_changed)
        self.html_dims_height.textChanged.connect(self._on_dims_changed)
        
        main_layout.addWidget(area_group)
        
        html_group = QGroupBox("HTML attribute")
        html_group.setMinimumWidth(350)
        html_layout = QVBoxLayout(html_group)
        html_layout.setContentsMargins(10, 16, 10, 10)
        html_layout.setSpacing(8)
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.html_url_input = QLineEdit()
        self.html_url_input.setPlaceholderText("https://www.google.com/")
        self.html_url_input.setText("https://www.google.com/")
        self.html_url_input.textChanged.connect(self._on_url_changed)
        url_layout.addWidget(self.html_url_input, stretch=1)
        html_layout.addLayout(url_layout)
        
        refresh_layout = QHBoxLayout()
        self.html_time_refresh_check = QCheckBox("Time refresh")
        self.html_time_refresh_check.setChecked(False)
        self.html_time_refresh_check.toggled.connect(self._on_time_refresh_toggled)
        refresh_layout.addWidget(self.html_time_refresh_check)
        
        self.html_time_refresh_value = QDoubleSpinBox()
        self.html_time_refresh_value.setMinimum(0.1)
        self.html_time_refresh_value.setMaximum(9999.9)
        self.html_time_refresh_value.setValue(15.0)
        self.html_time_refresh_value.setSuffix("s")
        self.html_time_refresh_value.setDecimals(1)
        self.html_time_refresh_value.setEnabled(False)
        self.html_time_refresh_value.valueChanged.connect(self._on_time_refresh_value_changed)
        refresh_layout.addWidget(self.html_time_refresh_value)
        refresh_layout.addStretch()
        html_layout.addLayout(refresh_layout)
        
        html_layout.addStretch()
        main_layout.addWidget(html_group)
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
        self.html_coords_x.blockSignals(True)
        self.html_coords_y.blockSignals(True)
        self.html_coords_x.setText(str(x))
        self.html_coords_y.setText(str(y))
        self.html_coords_x.blockSignals(False)
        self.html_coords_y.blockSignals(False)
        
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        if not width or width <= 0:
            width = default_width
        if not height or height <= 0:
            height = default_height
        
        self.html_dims_width.blockSignals(True)
        self.html_dims_height.blockSignals(True)
        self.html_dims_width.setText(str(width))
        self.html_dims_height.setText(str(height))
        self.html_dims_width.blockSignals(False)
        self.html_dims_height.blockSignals(False)
        
        html_props = element_props.get("html", {})
        url = html_props.get("url", "https://www.google.com/") if isinstance(html_props, dict) else "https://www.google.com/"
        self.html_url_input.blockSignals(True)
        self.html_url_input.setText(url)
        self.html_url_input.blockSignals(False)
        
        time_refresh_enabled = html_props.get("time_refresh_enabled", False) if isinstance(html_props, dict) else False
        time_refresh_value = html_props.get("time_refresh_value", 15.0) if isinstance(html_props, dict) else 15.0
        self.html_time_refresh_check.blockSignals(True)
        self.html_time_refresh_check.setChecked(time_refresh_enabled)
        self.html_time_refresh_check.blockSignals(False)
        self.html_time_refresh_value.setEnabled(time_refresh_enabled)
        self.html_time_refresh_value.blockSignals(True)
        self.html_time_refresh_value.setValue(time_refresh_value)
        self.html_time_refresh_value.blockSignals(False)
    
    def _on_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            x = int(self.html_coords_x.text() or "0")
            y = int(self.html_coords_y.text() or "0")
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
            self.property_changed.emit("html_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            width = int(self.html_dims_width.text() or "640")
            height = int(self.html_dims_height.text() or "480")
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
            self.property_changed.emit("html_size", (width, height))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_url_changed(self, url: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "html" not in self.current_element["properties"]:
            self.current_element["properties"]["html"] = {}
        self.current_element["properties"]["html"]["url"] = url
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("html_url", url)
        self._trigger_autosave()
    
    def _on_time_refresh_toggled(self, enabled: bool):
        self.html_time_refresh_value.setEnabled(enabled)
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "html" not in self.current_element["properties"]:
            self.current_element["properties"]["html"] = {}
        self.current_element["properties"]["html"]["time_refresh_enabled"] = enabled
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("html_time_refresh_enabled", enabled)
        self._trigger_autosave()
    
    def _on_time_refresh_value_changed(self, value: float):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "html" not in self.current_element["properties"]:
            self.current_element["properties"]["html"] = {}
        self.current_element["properties"]["html"]["time_refresh_value"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("html_time_refresh_value", value)
        self._trigger_autosave()

