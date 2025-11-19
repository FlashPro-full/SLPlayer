from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QGroupBox, QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit)
from PyQt5.QtCore import Qt
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class TextPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)
        main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        area_group = QGroupBox("Area attribute")
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(6, 6, 6, 6)
        area_layout.setSpacing(4)
        
        layout_section = QHBoxLayout()
        layout_section.setSpacing(4)
        
        coords_layout = QHBoxLayout()
        coords_layout.setSpacing(2)
        coords_label = QLabel("📍")
        self.text_coords_x = QLineEdit()
        self.text_coords_x.setPlaceholderText("0")
        self.text_coords_x.setMinimumWidth(60)
        self.text_coords_x.setText("0")
        self.text_coords_x.textChanged.connect(self._on_text_coords_changed)
        coords_comma = QLabel(",")
        self.text_coords_y = QLineEdit()
        self.text_coords_y.setPlaceholderText("0")
        self.text_coords_y.setMinimumWidth(60)
        self.text_coords_y.setText("0")
        self.text_coords_y.textChanged.connect(self._on_text_coords_changed)
        coords_layout.addWidget(coords_label)
        coords_layout.addWidget(self.text_coords_x)
        coords_layout.addWidget(coords_comma)
        coords_layout.addWidget(self.text_coords_y)
        layout_section.addLayout(coords_layout)
        
        dims_layout = QHBoxLayout()
        dims_layout.setSpacing(2)
        dims_label = QLabel("📐")
        self.text_dims_width = QLineEdit()
        self.text_dims_width.setPlaceholderText("1920")
        self.text_dims_width.setMinimumWidth(60)
        self.text_dims_width.setText("1920")
        self.text_dims_width.textChanged.connect(self._on_text_dims_changed)
        dims_comma = QLabel(",")
        self.text_dims_height = QLineEdit()
        self.text_dims_height.setPlaceholderText("1080")
        self.text_dims_height.setMinimumWidth(60)
        self.text_dims_height.setText("1080")
        self.text_dims_height.textChanged.connect(self._on_text_dims_changed)
        dims_layout.addWidget(dims_label)
        dims_layout.addWidget(self.text_dims_width)
        dims_layout.addWidget(dims_comma)
        dims_layout.addWidget(self.text_dims_height)
        layout_section.addLayout(dims_layout)
        
        layout_section.addStretch()
        area_layout.addLayout(layout_section)
        
        main_layout.addWidget(area_group)
        
        text_edit_group = QGroupBox("Text Content")
        text_edit_group.setMinimumWidth(400)
        text_edit_layout = QVBoxLayout(text_edit_group)
        text_edit_layout.setContentsMargins(6, 6, 6, 6)
        text_edit_layout.setSpacing(4)
        
        self.text_content_edit = QTextEdit()
        self.text_content_edit.setMinimumHeight(150)
        self.text_content_edit.setPlaceholderText("Enter text content here...")
        self.text_content_edit.textChanged.connect(self._on_text_content_changed)
        text_edit_layout.addWidget(self.text_content_edit, stretch=1)
        
        main_layout.addWidget(text_edit_group, stretch=1)
        
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)
        display_layout.setContentsMargins(6, 6, 6, 6)
        display_layout.setSpacing(4)
        
        display_section = QVBoxLayout()
        display_section.setSpacing(4)
        display_header = QHBoxLayout()
        display_label = QLabel("Display")
        display_header.addWidget(display_label)
        display_header.addStretch()
        display_section.addLayout(display_header)
        
        self.text_display_combo = QComboBox()
        self.text_display_combo.addItems(["Immediate Show", "Fade In", "Slide In", "Zoom In"])
        self.text_display_combo.setCurrentText("Immediate Show")
        self.text_display_combo.currentTextChanged.connect(self._on_text_display_changed)
        display_section.addWidget(self.text_display_combo)
        
        display_time_layout = QHBoxLayout()
        self.text_display_time = QSpinBox()
        self.text_display_time.setMinimum(0)
        self.text_display_time.setMaximum(999)
        self.text_display_time.setValue(5)
        self.text_display_time.valueChanged.connect(self._on_text_display_time_changed)
        display_time_layout.addWidget(self.text_display_time)
        display_time_layout.addStretch()
        display_section.addLayout(display_time_layout)
        
        display_layout.addLayout(display_section)
        
        clear_section = QVBoxLayout()
        clear_section.setSpacing(4)
        clear_header = QHBoxLayout()
        clear_label = QLabel("Clear")
        clear_header.addWidget(clear_label)
        clear_header.addStretch()
        clear_section.addLayout(clear_header)
        
        self.text_clear_combo = QComboBox()
        self.text_clear_combo.addItems(["Immediate Clear", "Fade Out", "Slide Out", "Zoom Out"])
        self.text_clear_combo.setCurrentText("Immediate Clear")
        self.text_clear_combo.currentTextChanged.connect(self._on_text_clear_changed)
        clear_section.addWidget(self.text_clear_combo)
        
        clear_time_layout = QHBoxLayout()
        self.text_clear_time = QSpinBox()
        self.text_clear_time.setMinimum(0)
        self.text_clear_time.setMaximum(999)
        self.text_clear_time.setValue(5)
        self.text_clear_time.valueChanged.connect(self._on_text_clear_time_changed)
        clear_time_layout.addWidget(self.text_clear_time)
        clear_time_layout.addStretch()
        clear_section.addLayout(clear_time_layout)
        
        display_layout.addLayout(clear_section)
        
        color_mode_layout = QVBoxLayout()
        color_mode_layout.setSpacing(4)
        self.text_color_mode_combo = QComboBox()
        self.text_color_mode_combo.addItems(["Colorful", "Monochrome", "Grayscale"])
        self.text_color_mode_combo.setCurrentText("Colorful")
        self.text_color_mode_combo.currentTextChanged.connect(self._on_text_color_mode_changed)
        color_mode_layout.addWidget(self.text_color_mode_combo)
        display_layout.addLayout(color_mode_layout)
        
        hold_layout = QVBoxLayout()
        hold_layout.setSpacing(4)
        hold_label = QLabel("Hold")
        hold_layout.addWidget(hold_label)
        hold_input_layout = QHBoxLayout()
        self.text_hold_time = QDoubleSpinBox()
        self.text_hold_time.setMinimum(0.0)
        self.text_hold_time.setMaximum(9999.9)
        self.text_hold_time.setValue(5.0)
        self.text_hold_time.setSuffix("S")
        self.text_hold_time.setDecimals(1)
        self.text_hold_time.valueChanged.connect(self._on_text_hold_time_changed)
        hold_input_layout.addWidget(self.text_hold_time)
        hold_input_layout.addStretch()
        hold_layout.addLayout(hold_input_layout)
        display_layout.addLayout(hold_layout)
        
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
        self.text_coords_x.blockSignals(True)
        self.text_coords_y.blockSignals(True)
        self.text_coords_x.setText(str(x))
        self.text_coords_y.setText(str(y))
        self.text_coords_x.blockSignals(False)
        self.text_coords_y.blockSignals(False)
        
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
        
        self.text_dims_width.blockSignals(True)
        self.text_dims_height.blockSignals(True)
        self.text_dims_width.setText(str(width))
        self.text_dims_height.setText(str(height))
        self.text_dims_width.blockSignals(False)
        self.text_dims_height.blockSignals(False)
        
        text_props = element_props.get("text", {})
        if isinstance(text_props, dict):
            text_content = text_props.get("content", "")
        else:
            text_content = str(text_props) if text_props else ""
        self.text_content_edit.blockSignals(True)
        self.text_content_edit.setPlainText(text_content)
        self.text_content_edit.blockSignals(False)
        
        display_props = element_props.get("display", {})
        display_mode = display_props.get("mode", "Immediate Show") if isinstance(display_props, dict) else "Immediate Show"
        display_time = display_props.get("time", 5) if isinstance(display_props, dict) else 5
        self.text_display_combo.setCurrentText(display_mode)
        self.text_display_time.setValue(display_time)
        
        clear_props = element_props.get("clear", {})
        clear_mode = clear_props.get("mode", "Immediate Clear") if isinstance(clear_props, dict) else "Immediate Clear"
        clear_time = clear_props.get("time", 5) if isinstance(clear_props, dict) else 5
        self.text_clear_combo.setCurrentText(clear_mode)
        self.text_clear_time.setValue(clear_time)
        
        color_mode = element_props.get("color_mode", "Colorful")
        self.text_color_mode_combo.setCurrentText(color_mode)
        
        hold_time = element_props.get("hold_time", 5.0)
        self.text_hold_time.setValue(hold_time)
    
    def _on_text_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        
        try:
            x = int(self.text_coords_x.text() or "0")
            y = int(self.text_coords_y.text() or "0")
            
            screen_width, screen_height = self._get_screen_bounds()
            default_width = screen_width if screen_width else 640
            default_height = screen_height if screen_height else 480
            
            element_props = self.current_element.get("properties", {})
            width = element_props.get("width", default_width)
            height = element_props.get("height", default_height)
            
            x, y, width, height = self._constrain_to_screen(x, y, width, height)
            
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            
            self.text_coords_x.blockSignals(True)
            self.text_coords_y.blockSignals(True)
            self.text_coords_x.setText(str(x))
            self.text_coords_y.setText(str(y))
            self.text_coords_x.blockSignals(False)
            self.text_coords_y.blockSignals(False)
            
            self.current_element["properties"]["x"] = x
            self.current_element["properties"]["y"] = y
            self.current_element["x"] = x
            self.current_element["y"] = y
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("text_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_text_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        
        try:
            screen_width, screen_height = self._get_screen_bounds()
            default_width = screen_width if screen_width else 640
            default_height = screen_height if screen_height else 480
            
            width = int(self.text_dims_width.text() or str(default_width))
            height = int(self.text_dims_height.text() or str(default_height))
            
            element_props = self.current_element.get("properties", {})
            x = element_props.get("x", 0)
            y = element_props.get("y", 0)
            
            x, y, width, height = self._constrain_to_screen(x, y, width, height)
            
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            
            self.text_dims_width.blockSignals(True)
            self.text_dims_height.blockSignals(True)
            self.text_dims_width.setText(str(width))
            self.text_dims_height.setText(str(height))
            self.text_dims_width.blockSignals(False)
            self.text_dims_height.blockSignals(False)
            
            self.current_element["properties"]["width"] = width
            self.current_element["properties"]["height"] = height
            self.current_element["width"] = width
            self.current_element["height"] = height
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("text_size", (width, height))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_text_content_changed(self):
        if not self.current_element or not self.current_program:
            return
        
        text_content = self.text_content_edit.toPlainText()
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        
        if "text" not in self.current_element["properties"]:
            self.current_element["properties"]["text"] = {}
        
        self.current_element["properties"]["text"]["content"] = text_content
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_content", text_content)
        self._trigger_autosave()
    
    def _on_text_display_changed(self, text: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "display" not in self.current_element["properties"]:
            self.current_element["properties"]["display"] = {}
        
        self.current_element["properties"]["display"]["mode"] = text
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_display_mode", text)
        self._trigger_autosave()
    
    def _on_text_display_time_changed(self, value: int):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "display" not in self.current_element["properties"]:
            self.current_element["properties"]["display"] = {}
        
        self.current_element["properties"]["display"]["time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_display_time", value)
        self._trigger_autosave()
    
    def _on_text_clear_changed(self, text: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "clear" not in self.current_element["properties"]:
            self.current_element["properties"]["clear"] = {}
        
        self.current_element["properties"]["clear"]["mode"] = text
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_clear_mode", text)
        self._trigger_autosave()
    
    def _on_text_clear_time_changed(self, value: int):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "clear" not in self.current_element["properties"]:
            self.current_element["properties"]["clear"] = {}
        
        self.current_element["properties"]["clear"]["time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_clear_time", value)
        self._trigger_autosave()
    
    def _on_text_color_mode_changed(self, text: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        
        self.current_element["properties"]["color_mode"] = text
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_color_mode", text)
        self._trigger_autosave()
    
    def _on_text_hold_time_changed(self, value: float):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        
        self.current_element["properties"]["hold_time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_hold_time", value)
        self._trigger_autosave()
    

