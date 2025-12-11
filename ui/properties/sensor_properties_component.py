from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class SensorPropertiesComponent(BasePropertiesComponent):
    
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
        self.sensor_coords_x = QLineEdit()
        self.sensor_coords_x.setPlaceholderText("0")
        self.sensor_coords_x.setMinimumWidth(70)
        self.sensor_coords_x.setText("0")
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #FFFFFF; font-weight: bold;")
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
        dims_comma.setStyleSheet("color: #FFFFFF; font-weight: bold;")
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
        
        main_layout.addWidget(area_group)
        
        other_group = QGroupBox("Other")
        other_layout = QVBoxLayout(other_group)
        other_layout.setContentsMargins(10, 16, 10, 10)
        other_layout.setSpacing(8)
        
        sensor_type_layout = QHBoxLayout()
        sensor_type_layout.addWidget(QLabel("Sensor Type:"))
        self.sensor_type_combo = QComboBox()
        self.sensor_types = [
            "temp",
            "Air Humidity",
            "PM2.5",
            "PM10",
            "Wind power",
            "Wind Direction",
            "Noise",
            "Pressure",
            "Light Intensity",
            "CO2"
        ]
        self.sensor_type_combo.addItems(self.sensor_types)
        self.sensor_type_combo.setCurrentText("temp")
        self.sensor_type_combo.currentTextChanged.connect(self._on_sensor_type_changed)
        sensor_type_layout.addWidget(self.sensor_type_combo, stretch=1)
        other_layout.addLayout(sensor_type_layout)
        
        fixed_text_layout = QHBoxLayout()
        fixed_text_layout.addWidget(QLabel("Fixed Text:"))
        self.sensor_fixed_text = QLineEdit()
        self.sensor_fixed_text.setText("The Temperature")
        self.sensor_fixed_text.textChanged.connect(self._on_fixed_text_changed)
        fixed_text_layout.addWidget(self.sensor_fixed_text, stretch=1)
        fixed_text_layout.addStretch()
        other_layout.addLayout(fixed_text_layout)

        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Arial", "Times New Roman", "Courier New", "Verdana", "Georgia",
            "Palatino", "Garamond", "Bookman", "Comic Sans MS", "Trebuchet MS",
            "Arial Black", "Impact", "Tahoma", "Lucida Console", "Monaco"
        ])
        self.font_family_combo.currentTextChanged.connect(self._on_font_family_changed)
        font_row.addWidget(self.font_family_combo, stretch=1)
        font_row.addStretch()

        self.font_color_btn = QPushButton("A")
        self.font_color_btn.setToolTip("Font Color")
        self.font_color_btn.clicked.connect(self._on_font_color_clicked)
        self.font_color = QColor(Qt.white)
        self._update_font_color_button()
        font_row.addWidget(self.font_color_btn)
        font_row.addStretch()
        
        other_layout.addLayout(font_row)
        
        sensor_unit_layout = QHBoxLayout()
        sensor_unit_layout.addWidget(QLabel("Sensor Unit:"))
        self.sensor_unit_input = QLineEdit()
        self.sensor_unit_input.setPlaceholderText("°C")
        self.sensor_unit_input.textChanged.connect(self._on_sensor_unit_changed)
        sensor_unit_layout.addWidget(self.sensor_unit_input, stretch=1)
        other_layout.addLayout(sensor_unit_layout)
        
        other_layout.addStretch()
        main_layout.addWidget(other_group)
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
        
        sensor_props = element_props.get("sensor", {})
        sensor_type = sensor_props.get("sensor_type", "temp") if isinstance(sensor_props, dict) else "temp"
        sensor_type_index = self.sensor_type_combo.findText(sensor_type)
        if sensor_type_index >= 0:
            self.sensor_type_combo.blockSignals(True)
            self.sensor_type_combo.setCurrentIndex(sensor_type_index)
            self.sensor_type_combo.blockSignals(False)
        
        default_fixed_text = self._get_default_fixed_text(sensor_type)
        fixed_text = sensor_props.get("fixed_text", default_fixed_text) if isinstance(sensor_props, dict) else default_fixed_text
        self.sensor_fixed_text.blockSignals(True)
        self.sensor_fixed_text.setText(fixed_text)
        self.sensor_fixed_text.blockSignals(False)
        
        font_family = sensor_props.get("font_family", "Arial") if isinstance(sensor_props, dict) else "Arial"
        font_family_index = self.font_family_combo.findText(font_family)
        if font_family_index >= 0:
            self.font_family_combo.blockSignals(True)
            self.font_family_combo.setCurrentIndex(font_family_index)
            self.font_family_combo.blockSignals(False)
        
        font_color_str = sensor_props.get("font_color", "#FFFFFF") if isinstance(sensor_props, dict) else "#FFFFFF"
        self.font_color = QColor(font_color_str)
        self._update_font_color_button()
        
        default_unit = self._get_default_unit(sensor_type)
        unit = sensor_props.get("unit", default_unit) if isinstance(sensor_props, dict) else default_unit
        self.sensor_unit_input.blockSignals(True)
        self.sensor_unit_input.setText(unit)
        self.sensor_unit_input.blockSignals(False)
    
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
    
    def _get_default_fixed_text(self, sensor_type: str) -> str:
        text_map = {
            "temp": "The Temperature",
            "Air Humidity": "The Humidity",
            "PM2.5": "The PM2.5:",
            "PM10": "The PM10:",
            "Wind power": "The Wind Grade",
            "Wind Direction": "The Wind Direction",
            "Noise": "The Noise",
            "Pressure": "The Pressure",
            "Light Intensity": "The Light Intensity",
            "CO2": "The CO2"
        }
        return text_map.get(sensor_type, f"The {sensor_type}")
    
    def _get_default_unit(self, sensor_type: str) -> str:
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
    
    def _on_sensor_type_changed(self, sensor_type: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "sensor" not in self.current_element["properties"]:
            self.current_element["properties"]["sensor"] = {}
        self.current_element["properties"]["sensor"]["sensor_type"] = sensor_type
        
        default_text = self._get_default_fixed_text(sensor_type)
        default_unit = self._get_default_unit(sensor_type)
        
        self.sensor_fixed_text.blockSignals(True)
        self.sensor_fixed_text.setText(default_text)
        self.sensor_fixed_text.blockSignals(False)
        
        self.sensor_unit_input.blockSignals(True)
        self.sensor_unit_input.setText(default_unit)
        self.sensor_unit_input.blockSignals(False)
        
        self.current_element["properties"]["sensor"]["fixed_text"] = default_text
        self.current_element["properties"]["sensor"]["unit"] = default_unit
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_type", sensor_type)
        self._trigger_autosave()
    
    def _on_fixed_text_changed(self, text: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "sensor" not in self.current_element["properties"]:
            self.current_element["properties"]["sensor"] = {}
        self.current_element["properties"]["sensor"]["fixed_text"] = text
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_fixed_text", text)
        self._trigger_autosave()
    
    def _on_font_family_changed(self, font_family: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "sensor" not in self.current_element["properties"]:
            self.current_element["properties"]["sensor"] = {}
        self.current_element["properties"]["sensor"]["font_family"] = font_family
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_font_family", font_family)
        self._trigger_autosave()
    
    def _on_font_color_clicked(self):
        color = QColorDialog.getColor(self.font_color)
        if color.isValid():
            self.font_color = color
            self._update_font_color_button()
            if not self.current_element or not self.current_program:
                return
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "sensor" not in self.current_element["properties"]:
                self.current_element["properties"]["sensor"] = {}
            self.current_element["properties"]["sensor"]["font_color"] = color.name()
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("sensor_font_color", color.name())
            self._trigger_autosave()
    
    def _on_sensor_unit_changed(self, unit: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "sensor" not in self.current_element["properties"]:
            self.current_element["properties"]["sensor"] = {}
        self.current_element["properties"]["sensor"]["unit"] = unit
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("sensor_unit", unit)
        self._trigger_autosave()
    
    def _update_font_color_button(self):
        self.font_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #3B3B3B;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
                color: {self.font_color.name()};
            }}
            QPushButton:hover {{
                background-color: #4B4B4B;
                border: 1px solid #4A90E2;
            }}
            QPushButton:pressed {{
                background-color: #5B5B5B;
            }}
        """)

