from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QFileDialog, QGroupBox, QLineEdit,
                             QDoubleSpinBox, QFormLayout)
from PyQt5.QtCore import Qt
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent
from ui.widgets.photo_icon_view import PhotoIconView
from config.animation_effects import get_animation_index, get_animation_name


class ImagePropertiesComponent(BasePropertiesComponent):
    
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
        coords_layout.addStretch()
        layout_section.addLayout(coords_layout)
        
        dims_layout = QHBoxLayout()
        dims_layout.setSpacing(2)
        dims_label = QLabel("📐")
        self.image_dims_width = QLineEdit()
        self.image_dims_width.setPlaceholderText("screen width")
        self.image_dims_width.setMinimumWidth(60)
        dims_comma = QLabel(",")
        self.image_dims_height = QLineEdit()
        self.image_dims_height.setPlaceholderText("screen height")
        self.image_dims_height.setMinimumWidth(60)
        dims_layout.addWidget(dims_label)
        dims_layout.addWidget(self.image_dims_width)
        dims_layout.addWidget(dims_comma)
        dims_layout.addWidget(self.image_dims_height)
        dims_layout.addStretch()
        layout_section.addLayout(dims_layout)
        
        area_layout.addLayout(layout_section)
        
        self.image_coords_x.textChanged.connect(self._on_image_coords_changed)
        self.image_coords_y.textChanged.connect(self._on_image_coords_changed)
        self.image_dims_width.textChanged.connect(self._on_image_dims_changed)
        self.image_dims_height.textChanged.connect(self._on_image_dims_changed)
        
        layout.addWidget(area_group)
        
        photo_list_group = QGroupBox("Photo List")
        photo_list_group.setMinimumWidth(400)
        photo_list_layout = QHBoxLayout(photo_list_group)
        photo_list_layout.setAlignment(Qt.AlignCenter)
        
        self.photo_list = PhotoIconView()
        self.photo_list.setMinimumHeight(150)
        self.photo_list.item_selected.connect(self._on_photo_item_selected)
        self.photo_list.item_deleted.connect(self._on_photo_item_deleted)
        photo_list_layout.addWidget(self.photo_list, stretch=1)
        
        photo_buttons_layout = QVBoxLayout()
        photo_buttons_layout.setContentsMargins(0, 0, 0, 0)
        photo_buttons_layout.setSpacing(4)
        photo_buttons_layout.setAlignment(Qt.AlignCenter)
        
        self.photo_add_btn = QPushButton("➕")
        self.photo_add_btn.clicked.connect(self._on_photo_add)
        self.photo_delete_btn = QPushButton("🗑")
        self.photo_delete_btn.clicked.connect(self._on_photo_delete)
        self.photo_up_btn = QPushButton("🔼")
        self.photo_up_btn.clicked.connect(self._on_photo_up)
        self.photo_down_btn = QPushButton("🔽")
        self.photo_down_btn.clicked.connect(self._on_photo_down)
        
        photo_buttons_layout.addWidget(self.photo_add_btn)
        photo_buttons_layout.addWidget(self.photo_delete_btn)
        photo_buttons_layout.addWidget(self.photo_up_btn)
        photo_buttons_layout.addWidget(self.photo_down_btn)
        photo_buttons_layout.addStretch()
        
        photo_list_layout.addLayout(photo_buttons_layout)
        
        layout.addWidget(photo_list_group, stretch=1)
        
        animation_group = QGroupBox("Animation")
        animation_group.setMinimumWidth(250)
        animation_layout = QFormLayout(animation_group)
        
        entrance_animation_layout = QHBoxLayout()
        entrance_icon = QLabel("🚫")
        entrance_animation_layout.addWidget(entrance_icon)
        self.image_entrance_animation_combo = QComboBox()
        self.image_entrance_animation_combo.addItems([
            "Random", "None", "Fade", "Fly In", "Wipe", "Split", "Strips",
            "Circle", "Wheel", "Zoom", "Box", "Plus", "Checkerboard", "Blinds",
            "Diamond", "Dissolve", "Peek", "Bounce", "Flash", "Grow & Turn",
            "Spiral", "Swivel", "Unfold", "Fade & Zoom", "Float In", "Pinwheel",
            "Rise Up", "Swing", "Zoom & Fade", "Zoom & Turn"
        ])
        self.image_entrance_animation_combo.setCurrentText("Random")
        self.image_entrance_animation_combo.currentTextChanged.connect(self._on_entrance_animation_changed)
        entrance_animation_layout.addWidget(self.image_entrance_animation_combo, stretch=1)
        animation_layout.addRow("Display", entrance_animation_layout)
        
        entrance_speed_layout = QHBoxLayout()
        entrance_speed_layout.addStretch()
        self.image_entrance_speed_combo = QComboBox()
        self.image_entrance_speed_combo.addItems([f"{i} fast" if i > 1 else "1 fast" for i in range(1, 11)])
        self.image_entrance_speed_combo.setCurrentText("1 fast")
        self.image_entrance_speed_combo.currentTextChanged.connect(self._on_entrance_speed_changed)
        entrance_speed_layout.addWidget(self.image_entrance_speed_combo, stretch=1)
        animation_layout.addRow("", entrance_speed_layout)
        
        exit_animation_layout = QHBoxLayout()
        exit_icon = QLabel("🔄")
        exit_animation_layout.addWidget(exit_icon)
        self.image_exit_animation_combo = QComboBox()
        self.image_exit_animation_combo.addItems([
            "Random", "None", "Fade", "Fly Out", "Wipe", "Split", "Strips",
            "Circle", "Wheel", "Zoom", "Box", "Plus", "Checkerboard", "Blinds",
            "Diamond", "Dissolve", "Peek", "Bounce", "Flash", "Grow & Turn",
            "Spiral", "Swivel", "Unfold", "Fade & Zoom", "Float Out", "Pinwheel",
            "Rise Up", "Swing", "Zoom & Fade", "Zoom & Turn"
        ])
        self.image_exit_animation_combo.setCurrentText("Random")
        self.image_exit_animation_combo.currentTextChanged.connect(self._on_exit_animation_changed)
        exit_animation_layout.addWidget(self.image_exit_animation_combo, stretch=1)
        animation_layout.addRow("Clear", exit_animation_layout)
        
        exit_speed_layout = QHBoxLayout()
        exit_speed_layout.addStretch()
        self.image_exit_speed_combo = QComboBox()
        self.image_exit_speed_combo.addItems([f"{i} fast" if i > 1 else "1 fast" for i in range(1, 11)])
        self.image_exit_speed_combo.setCurrentText("1 fast")
        self.image_exit_speed_combo.currentTextChanged.connect(self._on_exit_speed_changed)
        exit_speed_layout.addWidget(self.image_exit_speed_combo, stretch=1)
        animation_layout.addRow("", exit_speed_layout)
        
        self.image_hold_time_spin = QDoubleSpinBox()
        self.image_hold_time_spin.setMinimum(0.0)
        self.image_hold_time_spin.setMaximum(999.9)
        self.image_hold_time_spin.setSingleStep(0.1)
        self.image_hold_time_spin.setDecimals(1)
        self.image_hold_time_spin.setSuffix(" second")
        self.image_hold_time_spin.setValue(0.0)
        self.image_hold_time_spin.valueChanged.connect(self._on_hold_time_changed)
        animation_layout.addRow("Hold", self.image_hold_time_spin)
        
        layout.addWidget(animation_group)
    
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
        self.image_coords_x.blockSignals(True)
        self.image_coords_y.blockSignals(True)
        self.image_coords_x.setText(str(x))
        self.image_coords_y.setText(str(y))
        self.image_coords_x.blockSignals(False)
        self.image_coords_y.blockSignals(False)
        
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
        
        self.image_dims_width.blockSignals(True)
        self.image_dims_height.blockSignals(True)
        self.image_dims_width.setText(str(width))
        self.image_dims_height.setText(str(height))
        self.image_dims_width.blockSignals(False)
        self.image_dims_height.blockSignals(False)
        
        animation = element_props.get("animation", {})
        
        entrance_animation = animation.get("entrance", "Random")
        entrance_animation_index = animation.get("entrance_animation", None)
        
        if entrance_animation_index is not None:
            entrance_animation = get_animation_name(entrance_animation_index)
        elif isinstance(entrance_animation, int):
            entrance_animation = get_animation_name(entrance_animation)
        
        entrance_index = self.image_entrance_animation_combo.findText(entrance_animation)
        if entrance_index >= 0:
            self.image_entrance_animation_combo.setCurrentIndex(entrance_index)
        
        entrance_speed = animation.get("entrance_speed", "1 fast")
        entrance_speed_index = self.image_entrance_speed_combo.findText(entrance_speed)
        if entrance_speed_index >= 0:
            self.image_entrance_speed_combo.setCurrentIndex(entrance_speed_index)
        
        exit_animation = animation.get("exit", "Random")
        exit_animation_index = animation.get("exit_animation", None)
        
        if exit_animation_index is not None:
            exit_animation = get_animation_name(exit_animation_index)
        elif isinstance(exit_animation, int):
            exit_animation = get_animation_name(exit_animation)
        
        exit_index = self.image_exit_animation_combo.findText(exit_animation)
        if exit_index >= 0:
            self.image_exit_animation_combo.setCurrentIndex(exit_index)
        
        exit_speed = animation.get("exit_speed", "1 fast")
        exit_speed_index = self.image_exit_speed_combo.findText(exit_speed)
        if exit_speed_index >= 0:
            self.image_exit_speed_combo.setCurrentIndex(exit_speed_index)
        
        hold_time = animation.get("hold_time", 0.0)
        self.image_hold_time_spin.blockSignals(True)
        self.image_hold_time_spin.setValue(hold_time)
        self.image_hold_time_spin.blockSignals(False)
        
        photo_list = element_props.get("photo_list", element_props.get("image_list", []))
        self.photo_list.set_photos(photo_list)
    
    def _on_entrance_animation_changed(self, animation: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["entrance"] = animation
        self.current_element["properties"]["animation"]["entrance_animation"] = get_animation_index(animation)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_entrance_animation", animation)
        self._trigger_autosave()
    
    def _on_entrance_speed_changed(self, speed: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["entrance_speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_entrance_speed", speed)
        self._trigger_autosave()
    
    def _on_exit_animation_changed(self, animation: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["exit"] = animation
        self.current_element["properties"]["animation"]["exit_animation"] = get_animation_index(animation)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_exit_animation", animation)
        self._trigger_autosave()
    
    def _on_exit_speed_changed(self, speed: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["exit_speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_exit_speed", speed)
        self._trigger_autosave()
    
    def _on_hold_time_changed(self, value: float):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["hold_time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_hold_time", value)
        self._trigger_autosave()
    
    def _on_image_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        
        try:
            x = int(self.image_coords_x.text() or "0")
            y = int(self.image_coords_y.text() or "0")
            
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
    
    def _on_photo_add(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.svg);;All Files (*)"
        )
        if file_path:
            if self.current_element:
                if "properties" not in self.current_element:
                    self.current_element["properties"] = {}
                if "photo_list" not in self.current_element["properties"]:
                    self.current_element["properties"]["photo_list"] = []
                self.current_element["properties"]["photo_list"].append({"path": file_path})
                self.photo_list.add_item(file_path)
                self.property_changed.emit("photo_list", self.current_element["properties"]["photo_list"])
                self._trigger_autosave()
    
    def _on_photo_item_selected(self, index: int):
        pass
    
    def _on_photo_item_deleted(self, index: int):
        if self.current_element:
            if "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
                self.current_element["properties"]["photo_list"].pop(index)
                self.photo_list.remove_item(index)
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("photo_list", self.current_element["properties"]["photo_list"])
                self._trigger_autosave()
    
    def _on_photo_delete(self):
        current_index = self.photo_list.get_current_index()
        if current_index >= 0 and self.current_element:
            if "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
                photo_list = self.current_element["properties"]["photo_list"]
                if 0 <= current_index < len(photo_list):
                    self.current_element["properties"]["photo_list"].pop(current_index)
                    self.photo_list.remove_item(current_index)
                    self.current_program.modified = datetime.now().isoformat()
                    self.property_changed.emit("photo_list", self.current_element["properties"]["photo_list"])
                    self._trigger_autosave()
    
    def _on_photo_up(self):
        current_index = self.photo_list.get_current_index()
        if current_index > 0 and self.current_element:
            if "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
                photo_list = self.current_element["properties"]["photo_list"]
                new_index = self.photo_list.move_item_up(current_index)
                photo_list[current_index], photo_list[current_index - 1] = photo_list[current_index - 1], photo_list[current_index]
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("photo_list", photo_list)
                self._trigger_autosave()
    
    def _on_photo_down(self):
        current_index = self.photo_list.get_current_index()
        if self.current_element and "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
            photo_list = self.current_element["properties"]["photo_list"]
            if 0 <= current_index < len(photo_list) - 1:
                new_index = self.photo_list.move_item_down(current_index)
                photo_list[current_index], photo_list[current_index + 1] = photo_list[current_index + 1], photo_list[current_index]
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("photo_list", photo_list)
                self._trigger_autosave()
    

