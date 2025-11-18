"""
Image properties component
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QFileDialog, QGroupBox, QLineEdit, QCheckBox)
from PyQt5.QtCore import Qt
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class ImagePropertiesComponent(BasePropertiesComponent):
    """Image/Photo properties component"""
    
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
        self.image_coords_x = QLineEdit()
        self.image_coords_x.setPlaceholderText("0")
        self.image_coords_x.setMinimumWidth(60)
        self.image_coords_x.setText("0")
        coords_comma = QLabel(",")
        self.image_coords_y = QLineEdit()
        self.image_coords_y.setPlaceholderText("0")
        self.image_coords_y.setMinimumWidth(60)
        self.image_coords_y.setText("0")
        coords_layout.addWidget(coords_label)
        coords_layout.addWidget(self.image_coords_x)
        coords_layout.addWidget(coords_comma)
        coords_layout.addWidget(self.image_coords_y)
        layout_section.addLayout(coords_layout)
        
        # Dimensions with padlock
        dims_layout = QHBoxLayout()
        dims_layout.setSpacing(2)
        dims_label = QLabel("📐")
        self.image_dims_width = QLineEdit()
        self.image_dims_width.setPlaceholderText("1920")
        self.image_dims_width.setMinimumWidth(60)
        self.image_dims_width.setText("1920")
        dims_comma = QLabel(",")
        self.image_dims_height = QLineEdit()
        self.image_dims_height.setPlaceholderText("1080")
        self.image_dims_height.setMinimumWidth(60)
        self.image_dims_height.setText("1080")
        self.image_padlock_btn = QPushButton("🔒")
        self.image_padlock_btn.setCheckable(True)
        self.image_padlock_btn.setChecked(True)
        self.image_padlock_btn.setMaximumWidth(30)
        self.image_padlock_btn.setToolTip("Lock/Unlock dimensions")
        dims_layout.addWidget(dims_label)
        dims_layout.addWidget(self.image_dims_width)
        dims_layout.addWidget(dims_comma)
        dims_layout.addWidget(self.image_dims_height)
        dims_layout.addWidget(self.image_padlock_btn)
        layout_section.addLayout(dims_layout)
        
        layout_section.addStretch()
        area_layout.addLayout(layout_section)
        
        # Connect signals
        self.image_coords_x.textChanged.connect(self._on_image_coords_changed)
        self.image_coords_y.textChanged.connect(self._on_image_coords_changed)
        self.image_dims_width.textChanged.connect(self._on_image_dims_changed)
        self.image_dims_height.textChanged.connect(self._on_image_dims_changed)
        
        # Frame section with border, effect, and speed controls
        frame_group_layout = QVBoxLayout()
        frame_group_layout.setSpacing(4)
        
        # Frame checkbox
        frame_checkbox_layout = QHBoxLayout()
        self.image_frame_checkbox = QCheckBox("Frame")
        self.image_frame_checkbox.toggled.connect(self._on_image_frame_enabled_changed)
        frame_checkbox_layout.addWidget(self.image_frame_checkbox)
        frame_checkbox_layout.addStretch()
        frame_group_layout.addLayout(frame_checkbox_layout)
        
        # Border selection
        border_layout = QHBoxLayout()
        border_layout.addWidget(QLabel("Border:"))
        self.image_frame_border_combo = QComboBox()
        borders = self.get_available_borders()
        if borders:
            self.image_frame_border_combo.addItems(["---"] + borders)
        else:
            self.image_frame_border_combo.addItems(["---", "000", "001", "002", "003"])
        self.image_frame_border_combo.setCurrentText("---")
        self.image_frame_border_combo.setEnabled(False)
        self.image_frame_border_combo.currentTextChanged.connect(self._on_image_frame_border_changed)
        border_layout.addWidget(self.image_frame_border_combo, stretch=1)
        frame_group_layout.addLayout(border_layout)
        
        # Effect selection
        effect_layout = QHBoxLayout()
        effect_layout.addWidget(QLabel("Effect:"))
        self.image_frame_effect_combo = QComboBox()
        self.image_frame_effect_combo.addItems(["static", "rotate", "twinkle"])
        self.image_frame_effect_combo.setCurrentText("static")
        self.image_frame_effect_combo.setEnabled(False)
        self.image_frame_effect_combo.currentTextChanged.connect(self._on_image_frame_effect_changed)
        effect_layout.addWidget(self.image_frame_effect_combo, stretch=1)
        frame_group_layout.addLayout(effect_layout)
        
        # Speed selection
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.image_frame_speed_combo = QComboBox()
        self.image_frame_speed_combo.addItems(["slow", "in", "fast"])
        self.image_frame_speed_combo.setCurrentText("in")
        self.image_frame_speed_combo.setEnabled(False)
        self.image_frame_speed_combo.currentTextChanged.connect(self._on_image_frame_speed_changed)
        speed_layout.addWidget(self.image_frame_speed_combo, stretch=1)
        frame_group_layout.addLayout(speed_layout)
        
        area_layout.addLayout(frame_group_layout)
        
        # Transparency section
        transparency_layout = QHBoxLayout()
        transparency_layout.setSpacing(4)
        transparency_label = QLabel("Transparency")
        transparency_layout.addWidget(transparency_label)
        self.image_transparency_input = QLineEdit()
        self.image_transparency_input.setMaximumWidth(60)
        self.image_transparency_input.setText("100%")
        self.image_transparency_input.textChanged.connect(self._on_image_transparency_changed)
        transparency_layout.addWidget(self.image_transparency_input)
        transparency_minus_btn = QPushButton("-")
        transparency_minus_btn.setMaximumWidth(30)
        transparency_minus_btn.clicked.connect(lambda: self._adjust_image_transparency(-1))
        transparency_plus_btn = QPushButton("+")
        transparency_plus_btn.setMaximumWidth(30)
        transparency_plus_btn.clicked.connect(lambda: self._adjust_image_transparency(1))
        transparency_layout.addWidget(transparency_minus_btn)
        transparency_layout.addWidget(transparency_plus_btn)
        transparency_layout.addStretch()
        area_layout.addLayout(transparency_layout)
        
        main_layout.addWidget(area_group)
        
        # Right side: Action buttons
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(4)
        actions_layout.setAlignment(Qt.AlignTop)
        
        add_btn = QPushButton("➕")
        add_btn.setMaximumSize(40, 40)
        add_btn.setToolTip("Add")
        add_btn.clicked.connect(self._on_image_add)
        actions_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("🗑")
        delete_btn.setMaximumSize(40, 40)
        delete_btn.setToolTip("Delete")
        delete_btn.clicked.connect(self._on_image_delete)
        actions_layout.addWidget(delete_btn)
        
        down_btn = QPushButton("🔽")
        down_btn.setMaximumSize(40, 40)
        down_btn.setToolTip("Move Down")
        down_btn.clicked.connect(self._on_image_move_down)
        actions_layout.addWidget(down_btn)
        
        up_btn = QPushButton("🔼")
        up_btn.setMaximumSize(40, 40)
        up_btn.setToolTip("Move Up")
        up_btn.clicked.connect(self._on_image_move_up)
        actions_layout.addWidget(up_btn)
        
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)
        
        main_layout.addStretch()
    
    def update_properties(self):
        """Update image properties from current element"""
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
        self.image_coords_x.blockSignals(True)
        self.image_coords_y.blockSignals(True)
        self.image_coords_x.setText(str(x))
        self.image_coords_y.setText(str(y))
        self.image_coords_x.blockSignals(False)
        self.image_coords_y.blockSignals(False)
        
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
        
        self.image_dims_width.blockSignals(True)
        self.image_dims_height.blockSignals(True)
        self.image_dims_width.setText(str(width))
        self.image_dims_height.setText(str(height))
        self.image_dims_width.blockSignals(False)
        self.image_dims_height.blockSignals(False)
        
        # Update frame
        frame_props = element_props.get("frame", {})
        frame_enabled = frame_props.get("enabled", False) if isinstance(frame_props, dict) else False
        self.image_frame_checkbox.blockSignals(True)
        self.image_frame_checkbox.setChecked(frame_enabled)
        self.image_frame_checkbox.blockSignals(False)
        
        # Enable/disable frame controls
        self.image_frame_border_combo.setEnabled(frame_enabled)
        self.image_frame_effect_combo.setEnabled(frame_enabled)
        self.image_frame_speed_combo.setEnabled(frame_enabled)
        
        # Update border selection
        border = frame_props.get("border", "---") if isinstance(frame_props, dict) else "---"
        border_index = self.image_frame_border_combo.findText(border)
        if border_index >= 0:
            self.image_frame_border_combo.setCurrentIndex(border_index)
        else:
            self.image_frame_border_combo.setCurrentIndex(0)
        
        # Update effect selection
        effect = frame_props.get("effect", "static") if isinstance(frame_props, dict) else "static"
        effect_index = self.image_frame_effect_combo.findText(effect)
        if effect_index >= 0:
            self.image_frame_effect_combo.setCurrentIndex(effect_index)
        else:
            self.image_frame_effect_combo.setCurrentIndex(0)
        
        # Update speed selection
        speed = frame_props.get("speed", "in") if isinstance(frame_props, dict) else "in"
        speed_index = self.image_frame_speed_combo.findText(speed)
        if speed_index >= 0:
            self.image_frame_speed_combo.setCurrentIndex(speed_index)
        else:
            self.image_frame_speed_combo.setCurrentIndex(1)  # Default to "in"
        
        # Update transparency
        transparency = element_props.get("transparency", 100)
        self.image_transparency_input.blockSignals(True)
        self.image_transparency_input.setText(f"{transparency}%")
        self.image_transparency_input.blockSignals(False)
    
    def _on_image_frame_enabled_changed(self, enabled: bool):
        """Handle image frame enabled change"""
        if not self.current_element or not self.current_program:
            return
        
        # Enable/disable all frame controls
        self.image_frame_border_combo.setEnabled(enabled)
        self.image_frame_effect_combo.setEnabled(enabled)
        self.image_frame_speed_combo.setEnabled(enabled)
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["enabled"] = enabled
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_frame_enabled", enabled)
        self._trigger_autosave()
    
    def _on_image_frame_border_changed(self, border: str):
        """Handle image frame border selection change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["border"] = border
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_frame_border", border)
        self._trigger_autosave()
    
    def _on_image_frame_effect_changed(self, effect: str):
        """Handle image frame effect selection change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["effect"] = effect
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_frame_effect", effect)
        self._trigger_autosave()
    
    def _on_image_frame_speed_changed(self, speed: str):
        """Handle image frame speed selection change"""
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        
        self.current_element["properties"]["frame"]["speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_frame_speed", speed)
        self._trigger_autosave()
    
    def _on_image_transparency_changed(self, text: str):
        """Handle image transparency change"""
        if not self.current_element:
            return
        try:
            transparency = int(text.replace("%", "").strip())
            transparency = max(0, min(100, transparency))
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["transparency"] = transparency
            self.property_changed.emit("image_transparency", transparency)
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _adjust_image_transparency(self, delta: int):
        """Adjust image transparency by delta"""
        if not self.current_element:
            return
        try:
            current_text = self.image_transparency_input.text()
            current = int(current_text.replace("%", "").strip())
            new_value = max(0, min(100, current + delta))
            self.image_transparency_input.setText(f"{new_value}%")
        except ValueError:
            pass
    
    def _on_image_coords_changed(self):
        """Handle image coordinates change"""
        if not self.current_element or not self.current_program:
            return
        
        try:
            x = int(self.image_coords_x.text() or "0")
            y = int(self.image_coords_y.text() or "0")
            
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
            
            self.image_coords_x.blockSignals(True)
            self.image_coords_y.blockSignals(True)
            self.image_coords_x.setText(str(x))
            self.image_coords_y.setText(str(y))
            self.image_coords_x.blockSignals(False)
            self.image_coords_y.blockSignals(False)
            
            self.current_element["properties"]["x"] = x
            self.current_element["properties"]["y"] = y
            self.current_element["x"] = x
            self.current_element["y"] = y
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("image_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_image_dims_changed(self):
        """Handle image dimensions change"""
        if not self.current_element or not self.current_program:
            return
        
        try:
            width = int(self.image_dims_width.text() or "640")
            height = int(self.image_dims_height.text() or "480")
            
            element_props = self.current_element.get("properties", {})
            x = element_props.get("x", 0)
            y = element_props.get("y", 0)
            
            x, y, width, height = self._constrain_to_screen(x, y, width, height)
            
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            
            self.image_dims_width.blockSignals(True)
            self.image_dims_height.blockSignals(True)
            self.image_dims_width.setText(str(width))
            self.image_dims_height.setText(str(height))
            self.image_dims_width.blockSignals(False)
            self.image_dims_height.blockSignals(False)
            
            self.current_element["properties"]["width"] = width
            self.current_element["properties"]["height"] = height
            self.current_element["width"] = width
            self.current_element["height"] = height
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("image_size", (width, height))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_image_add(self):
        """Handle image add button"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.svg);;All Files (*)"
        )
        if file_path and self.current_element:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "image_list" not in self.current_element["properties"]:
                self.current_element["properties"]["image_list"] = []
            self.current_element["properties"]["image_list"].append({"path": file_path})
            self.property_changed.emit("image_list", self.current_element["properties"]["image_list"])
            self._trigger_autosave()
    
    def _on_image_delete(self):
        """Handle image delete button"""
        # Implementation depends on requirements
        pass
    
    def _on_image_move_down(self):
        """Handle image move down button"""
        # Implementation depends on requirements
        pass
    
    def _on_image_move_up(self):
        """Handle image move up button"""
        # Implementation depends on requirements
        pass

