"""
Text properties component
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QFileDialog, QGroupBox, QLineEdit, QCheckBox,
                             QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class TextPropertiesComponent(BasePropertiesComponent):
    """Text properties component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)
        main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Left side: Area Attribute group
        area_group = QGroupBox("Area attribute")
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(8, 8, 8, 8)
        area_layout.setSpacing(8)
        
        # Layout section: Coordinates and dimensions
        layout_section = QHBoxLayout()
        layout_section.setSpacing(4)
        
        # Coordinates (0, 0)
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
        
        # Dimensions with padlock
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
        self.text_padlock_btn = QPushButton("🔒")
        self.text_padlock_btn.setCheckable(True)
        self.text_padlock_btn.setChecked(True)
        self.text_padlock_btn.setMaximumWidth(30)
        self.text_padlock_btn.setToolTip("Lock/Unlock dimensions")
        self.text_padlock_btn.toggled.connect(self._on_text_padlock_toggled)
        dims_layout.addWidget(dims_label)
        dims_layout.addWidget(self.text_dims_width)
        dims_layout.addWidget(dims_comma)
        dims_layout.addWidget(self.text_dims_height)
        dims_layout.addWidget(self.text_padlock_btn)
        layout_section.addLayout(dims_layout)
        
        layout_section.addStretch()
        area_layout.addLayout(layout_section)
        
        # Frame section with border, effect, and speed controls
        frame_group_layout = QVBoxLayout()
        frame_group_layout.setSpacing(4)
        
        # Frame checkbox
        frame_checkbox_layout = QHBoxLayout()
        self.text_frame_checkbox = QCheckBox("Frame")
        self.text_frame_checkbox.toggled.connect(self._on_text_frame_enabled_changed)
        frame_checkbox_layout.addWidget(self.text_frame_checkbox)
        frame_checkbox_layout.addStretch()
        frame_group_layout.addLayout(frame_checkbox_layout)
        
        # Border selection
        border_layout = QHBoxLayout()
        border_layout.addWidget(QLabel("Border:"))
        self.text_frame_border_combo = QComboBox()
        borders = self.get_available_borders()
        if borders:
            self.text_frame_border_combo.addItems(["---"] + borders)
        else:
            self.text_frame_border_combo.addItems(["---", "000", "001", "002", "003"])
        self.text_frame_border_combo.setCurrentText("---")
        self.text_frame_border_combo.setEnabled(False)
        self.text_frame_border_combo.currentTextChanged.connect(self._on_text_frame_border_changed)
        border_layout.addWidget(self.text_frame_border_combo, stretch=1)
        frame_group_layout.addLayout(border_layout)
        
        # Effect selection
        effect_layout = QHBoxLayout()
        effect_layout.addWidget(QLabel("Effect:"))
        self.text_frame_effect_combo = QComboBox()
        self.text_frame_effect_combo.addItems(["static", "rotate", "twinkle"])
        self.text_frame_effect_combo.setCurrentText("static")
        self.text_frame_effect_combo.setEnabled(False)
        self.text_frame_effect_combo.currentTextChanged.connect(self._on_text_frame_effect_changed)
        effect_layout.addWidget(self.text_frame_effect_combo, stretch=1)
        frame_group_layout.addLayout(effect_layout)
        
        # Speed selection
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.text_frame_speed_combo = QComboBox()
        self.text_frame_speed_combo.addItems(["slow", "in", "fast"])
        self.text_frame_speed_combo.setCurrentText("in")
        self.text_frame_speed_combo.setEnabled(False)
        self.text_frame_speed_combo.currentTextChanged.connect(self._on_text_frame_speed_changed)
        speed_layout.addWidget(self.text_frame_speed_combo, stretch=1)
        frame_group_layout.addLayout(speed_layout)
        
        area_layout.addLayout(frame_group_layout)
        
        # Transparency section
        transparency_layout = QHBoxLayout()
        transparency_layout.setSpacing(4)
        transparency_label = QLabel("Transparency")
        transparency_layout.addWidget(transparency_label)
        self.text_transparency_input = QLineEdit()
        self.text_transparency_input.setMaximumWidth(60)
        self.text_transparency_input.setText("100%")
        self.text_transparency_input.textChanged.connect(self._on_text_transparency_changed)
        transparency_layout.addWidget(self.text_transparency_input)
        transparency_minus_btn = QPushButton("-")
        transparency_minus_btn.setMaximumWidth(30)
        transparency_minus_btn.clicked.connect(lambda: self._adjust_text_transparency(-1))
        transparency_plus_btn = QPushButton("+")
        transparency_plus_btn.setMaximumWidth(30)
        transparency_plus_btn.clicked.connect(lambda: self._adjust_text_transparency(1))
        transparency_layout.addWidget(transparency_minus_btn)
        transparency_layout.addWidget(transparency_plus_btn)
        transparency_layout.addStretch()
        area_layout.addLayout(transparency_layout)
        
        main_layout.addWidget(area_group)
        
        # Center: Large icon file view area
        icon_view_group = QGroupBox("Icon File")
        icon_view_layout = QVBoxLayout(icon_view_group)
        icon_view_layout.setContentsMargins(8, 8, 8, 8)
        icon_view_layout.setSpacing(8)
        
        # Large icon display area
        self.text_icon_view = QLabel()
        self.text_icon_view.setMinimumSize(200, 200)
        self.text_icon_view.setMaximumSize(400, 400)
        self.text_icon_view.setAlignment(Qt.AlignCenter)
        self.text_icon_view.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 2px dashed #CCCCCC;
                border-radius: 4px;
            }
        """)
        self.text_icon_view.setText("No Icon\n(Click to browse)")
        self.text_icon_view.setWordWrap(True)
        self.text_icon_view.mousePressEvent = self._on_text_icon_view_clicked
        icon_view_layout.addWidget(self.text_icon_view)
        
        # Icon file path display
        icon_path_layout = QHBoxLayout()
        icon_path_layout.setSpacing(4)
        self.text_icon_path = QLineEdit()
        self.text_icon_path.setPlaceholderText("Icon file path...")
        self.text_icon_path.setReadOnly(True)
        icon_path_layout.addWidget(self.text_icon_path)
        
        icon_browse_btn = QPushButton("Browse...")
        icon_browse_btn.clicked.connect(self._on_text_icon_browse)
        icon_path_layout.addWidget(icon_browse_btn)
        
        icon_clear_btn = QPushButton("Clear")
        icon_clear_btn.clicked.connect(self._on_text_icon_clear)
        icon_path_layout.addWidget(icon_clear_btn)
        
        icon_view_layout.addLayout(icon_path_layout)
        icon_view_layout.addStretch()
        
        main_layout.addWidget(icon_view_group, stretch=1)  # Center area gets stretch
        
        # Right side: Display panel
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)
        display_layout.setContentsMargins(8, 8, 8, 8)
        display_layout.setSpacing(8)
        
        # Display section
        display_section = QVBoxLayout()
        display_section.setSpacing(4)
        display_header = QHBoxLayout()
        display_icon = QLabel("🚫")
        display_label = QLabel("Display")
        display_header.addWidget(display_icon)
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
        
        # Clear section
        clear_section = QVBoxLayout()
        clear_section.setSpacing(4)
        clear_header = QHBoxLayout()
        clear_icon = QLabel("🔄")
        clear_label = QLabel("Clear")
        clear_header.addWidget(clear_icon)
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
        
        # Color Mode
        color_mode_layout = QVBoxLayout()
        color_mode_layout.setSpacing(4)
        self.text_color_mode_combo = QComboBox()
        self.text_color_mode_combo.addItems(["Colorful", "Monochrome", "Grayscale"])
        self.text_color_mode_combo.setCurrentText("Colorful")
        self.text_color_mode_combo.currentTextChanged.connect(self._on_text_color_mode_changed)
        color_mode_layout.addWidget(self.text_color_mode_combo)
        display_layout.addLayout(color_mode_layout)
        
        # Hold Time
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
    
    def resizeEvent(self, event):
        """Handle resize event to update icon display"""
        super().resizeEvent(event)
        self._resize_text_icon()
    
    def update_properties(self):
        """Update text properties from current element"""
        if not self.current_element or not self.current_program:
            return
        
        # Get screen dimensions for defaults
        screen_width, screen_height = self._get_screen_bounds()
        default_width = screen_width if screen_width else 1920
        default_height = screen_height if screen_height else 1080
        
        element_props = self.current_element.get("properties", {})
        
        # Update coordinates
        x = element_props.get("x", 0)
        y = element_props.get("y", 0)
        self.text_coords_x.blockSignals(True)
        self.text_coords_y.blockSignals(True)
        self.text_coords_x.setText(str(x))
        self.text_coords_y.setText(str(y))
        self.text_coords_x.blockSignals(False)
        self.text_coords_y.blockSignals(False)
        
        # Update dimensions - initialize to screen dimensions if missing or invalid
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        # If width/height are missing or invalid, set to screen dimensions
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
        
        # Update frame
        frame_props = element_props.get("frame", {})
        frame_enabled = frame_props.get("enabled", False) if isinstance(frame_props, dict) else False
        self.text_frame_checkbox.blockSignals(True)
        self.text_frame_checkbox.setChecked(frame_enabled)
        self.text_frame_checkbox.blockSignals(False)
        
        # Enable/disable frame controls
        self.text_frame_border_combo.setEnabled(frame_enabled)
        self.text_frame_effect_combo.setEnabled(frame_enabled)
        self.text_frame_speed_combo.setEnabled(frame_enabled)
        
        # Update border selection
        border = frame_props.get("border", "---") if isinstance(frame_props, dict) else "---"
        border_index = self.text_frame_border_combo.findText(border)
        if border_index >= 0:
            self.text_frame_border_combo.setCurrentIndex(border_index)
        else:
            self.text_frame_border_combo.setCurrentIndex(0)
        
        # Update effect selection
        effect = frame_props.get("effect", "static") if isinstance(frame_props, dict) else "static"
        effect_index = self.text_frame_effect_combo.findText(effect)
        if effect_index >= 0:
            self.text_frame_effect_combo.setCurrentIndex(effect_index)
        else:
            self.text_frame_effect_combo.setCurrentIndex(0)
        
        # Update speed selection
        speed = frame_props.get("speed", "in") if isinstance(frame_props, dict) else "in"
        speed_index = self.text_frame_speed_combo.findText(speed)
        if speed_index >= 0:
            self.text_frame_speed_combo.setCurrentIndex(speed_index)
        else:
            self.text_frame_speed_combo.setCurrentIndex(1)  # Default to "in"
        
        # Update transparency
        transparency = element_props.get("transparency", 100)
        self.text_transparency_input.blockSignals(True)
        self.text_transparency_input.setText(f"{transparency}%")
        self.text_transparency_input.blockSignals(False)
        
        # Update display settings
        display_props = element_props.get("display", {})
        display_mode = display_props.get("mode", "Immediate Show") if isinstance(display_props, dict) else "Immediate Show"
        display_time = display_props.get("time", 5) if isinstance(display_props, dict) else 5
        self.text_display_combo.setCurrentText(display_mode)
        self.text_display_time.setValue(display_time)
        
        # Update clear settings
        clear_props = element_props.get("clear", {})
        clear_mode = clear_props.get("mode", "Immediate Clear") if isinstance(clear_props, dict) else "Immediate Clear"
        clear_time = clear_props.get("time", 5) if isinstance(clear_props, dict) else 5
        self.text_clear_combo.setCurrentText(clear_mode)
        self.text_clear_time.setValue(clear_time)
        
        # Update color mode
        color_mode = element_props.get("color_mode", "Colorful")
        self.text_color_mode_combo.setCurrentText(color_mode)
        
        # Update hold time
        hold_time = element_props.get("hold_time", 5.0)
        self.text_hold_time.setValue(hold_time)
        
        # Update icon file
        icon_path = element_props.get("icon_path", "")
        self._update_text_icon_display(icon_path)
    
    def _on_text_coords_changed(self):
        """Handle text coordinates change"""
        if not self.current_element or not self.current_program:
            return
        
        try:
            x = int(self.text_coords_x.text() or "0")
            y = int(self.text_coords_y.text() or "0")
            
            # Get screen dimensions for defaults
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
        """Handle text dimensions change"""
        if not self.current_element or not self.current_program:
            return
        
        try:
            # Get screen dimensions for defaults
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
    
    def _on_text_padlock_toggled(self, checked: bool):
        """Handle text padlock toggle"""
        # TODO: Implement aspect ratio locking
        pass
    
    def _on_text_frame_enabled_changed(self, enabled: bool):
        """Handle text frame enabled change"""
        if not self.current_element or not self.current_program:
            return
        
        # Enable/disable all frame controls
        self.text_frame_border_combo.setEnabled(enabled)
        self.text_frame_effect_combo.setEnabled(enabled)
        self.text_frame_speed_combo.setEnabled(enabled)
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["enabled"] = enabled
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_frame_enabled", enabled)
        self._trigger_autosave()
    
    def _on_text_frame_border_changed(self, border: str):
        """Handle text frame border selection change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["border"] = border
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_frame_border", border)
        self._trigger_autosave()
    
    def _on_text_frame_effect_changed(self, effect: str):
        """Handle text frame effect selection change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["effect"] = effect
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_frame_effect", effect)
        self._trigger_autosave()
    
    def _on_text_frame_speed_changed(self, speed: str):
        """Handle text frame speed selection change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_frame_speed", speed)
        self._trigger_autosave()
    
    def _on_text_transparency_changed(self, text: str):
        """Handle text transparency change"""
        if not self.current_element or not self.current_program:
            return
        
        try:
            # Extract number from "100%" format
            transparency_str = text.replace("%", "").strip()
            transparency = int(transparency_str) if transparency_str else 100
            transparency = max(0, min(100, transparency))
            
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            
            self.current_element["properties"]["transparency"] = transparency
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("text_transparency", transparency)
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _adjust_text_transparency(self, delta: int):
        """Adjust text transparency by delta"""
        if not self.current_element:
            return
        
        try:
            current_text = self.text_transparency_input.text()
            transparency_str = current_text.replace("%", "").strip()
            transparency = int(transparency_str) if transparency_str else 100
            transparency = max(0, min(100, transparency + delta))
            self.text_transparency_input.setText(f"{transparency}%")
        except ValueError:
            pass
    
    def _on_text_display_changed(self, text: str):
        """Handle text display mode change"""
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
        """Handle text display time change"""
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
        """Handle text clear mode change"""
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
        """Handle text clear time change"""
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
        """Handle text color mode change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        
        self.current_element["properties"]["color_mode"] = text
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_color_mode", text)
        self._trigger_autosave()
    
    def _on_text_hold_time_changed(self, value: float):
        """Handle text hold time change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        
        self.current_element["properties"]["hold_time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_hold_time", value)
        self._trigger_autosave()
    
    def _on_text_icon_view_clicked(self, event):
        """Handle click on icon view area"""
        self._on_text_icon_browse()
    
    def _on_text_icon_browse(self):
        """Handle icon file browse button"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon File", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.ico *.svg);;All Files (*)"
        )
        if file_path and Path(file_path).exists():
            if self.current_element:
                if "properties" not in self.current_element:
                    self.current_element["properties"] = {}
                self.current_element["properties"]["icon_path"] = file_path
                self.current_program.modified = datetime.now().isoformat()
                self._update_text_icon_display(file_path)
                self.property_changed.emit("icon_path", file_path)
                self._trigger_autosave()
    
    def _on_text_icon_clear(self):
        """Handle icon clear button"""
        if self.current_element:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["icon_path"] = ""
            self.current_program.modified = datetime.now().isoformat()
            self._update_text_icon_display("")
            self.property_changed.emit("icon_path", "")
            self._trigger_autosave()
    
    def _update_text_icon_display(self, icon_path: str):
        """Update the icon display area with the icon file"""
        if not hasattr(self, 'text_icon_view') or not hasattr(self, 'text_icon_path'):
            return
        
        self.text_icon_path.setText(icon_path)
        
        # Store the icon path for later resizing
        if hasattr(self, 'text_icon_view'):
            self.text_icon_view._icon_path = icon_path
        
        if icon_path and Path(icon_path).exists():
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    # Store original pixmap
                    if hasattr(self, 'text_icon_view'):
                        self.text_icon_view._original_pixmap = pixmap
                    # Scale pixmap to fit the view area while maintaining aspect ratio
                    self._resize_text_icon()
                    self.text_icon_view.setText("")
                else:
                    self.text_icon_view.setText("Invalid Icon File")
                    self.text_icon_view.setPixmap(QPixmap())
                    if hasattr(self.text_icon_view, '_original_pixmap'):
                        delattr(self.text_icon_view, '_original_pixmap')
            except Exception as e:
                self.text_icon_view.setText(f"Error loading icon:\n{str(e)}")
                self.text_icon_view.setPixmap(QPixmap())
                if hasattr(self.text_icon_view, '_original_pixmap'):
                    delattr(self.text_icon_view, '_original_pixmap')
        else:
            self.text_icon_view.setText("No Icon\n(Click to browse)")
            self.text_icon_view.setPixmap(QPixmap())
            if hasattr(self.text_icon_view, '_original_pixmap'):
                delattr(self.text_icon_view, '_original_pixmap')
    
    def _resize_text_icon(self):
        """Resize the icon to fit the view area"""
        if not hasattr(self, 'text_icon_view'):
            return
        
        if not hasattr(self.text_icon_view, '_original_pixmap'):
            return
        
        view_size = self.text_icon_view.size()
        if view_size.width() <= 0 or view_size.height() <= 0:
            return
        
        original_pixmap = self.text_icon_view._original_pixmap
        scaled_pixmap = original_pixmap.scaled(
            view_size.width() - 20, view_size.height() - 20,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.text_icon_view.setPixmap(scaled_pixmap)

