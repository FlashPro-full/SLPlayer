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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)
        
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #FFFFFF;
            }
            QLineEdit {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #3B3B3B;
                color: #FFFFFF;
                font-size: 12px;
                selection-background-color: #4A90E2;
                selection-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #3B3B3B;
            }
            QLineEdit:hover {
                border: 1px solid #666666;
            }
            QComboBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #3B3B3B;
                color: #FFFFFF;
                font-size: 12px;
                min-width: 80px;
            }
            QComboBox:hover {
                border: 1px solid #666666;
            }
            QComboBox:focus {
                border: 1px solid #4A90E2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #CCCCCC;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #2B2B2B;
                color: #FFFFFF;
                selection-background-color: #3B3B3B;
                selection-color: #FFFFFF;
                padding: 2px;
            }
            QTextEdit {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 6px;
                background-color: #3B3B3B;
                color: #FFFFFF;
                font-size: 12px;
                selection-background-color: #4A90E2;
                selection-color: #FFFFFF;
            }
            QTextEdit:focus {
                border: 1px solid #4A90E2;
            }
            QTextEdit:hover {
                border: 1px solid #666666;
            }
            QDoubleSpinBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #3B3B3B;
                color: #FFFFFF;
                font-size: 12px;
                selection-background-color: #4A90E2;
                selection-color: #FFFFFF;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #4A90E2;
            }
            QDoubleSpinBox:hover {
                border: 1px solid #666666;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                border: none;
                background-color: transparent;
                width: 16px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #F0F0F0;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
        """)
        
        area_group = QGroupBox("Area attribute")
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(10, 16, 10, 10)
        area_layout.setSpacing(8)
        area_layout.setAlignment(Qt.AlignTop)
        
        coords_row = QHBoxLayout()
        coords_row.setSpacing(6)
        coords_label = QLabel("📍")
        coords_label.setStyleSheet("font-size: 16px;")
        self.image_coords_x = QLineEdit()
        self.image_coords_x.setPlaceholderText("0")
        self.image_coords_x.setMinimumWidth(70)
        self.image_coords_x.setText("0")
        self.image_coords_x.textChanged.connect(self._on_image_coords_changed)
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        self.image_coords_y = QLineEdit()
        self.image_coords_y.setPlaceholderText("0")
        self.image_coords_y.setMinimumWidth(70)
        self.image_coords_y.setText("0")
        self.image_coords_y.textChanged.connect(self._on_image_coords_changed)
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.image_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.image_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.image_dims_width = QLineEdit()
        self.image_dims_width.setPlaceholderText("1920")
        self.image_dims_width.setMinimumWidth(70)
        self.image_dims_width.setText("1920")
        self.image_dims_width.textChanged.connect(self._on_image_dims_changed)
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.image_dims_height = QLineEdit()
        self.image_dims_height.setPlaceholderText("1080")
        self.image_dims_height.setMinimumWidth(70)
        self.image_dims_height.setText("1080")
        self.image_dims_height.textChanged.connect(self._on_image_dims_changed)
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.image_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.image_dims_height)
        area_layout.addLayout(dims_row)
        
        area_layout.addStretch()
        layout.addWidget(area_group)
        
        photo_list_group = QGroupBox("Photo List")
        photo_list_group.setMinimumWidth(300)
        photo_list_layout = QVBoxLayout(photo_list_group)
        photo_list_layout.setAlignment(Qt.AlignCenter)

        photo_buttons_layout = QHBoxLayout()
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
        
        self.photo_list = PhotoIconView()
        self.photo_list.setMinimumHeight(150)
        self.photo_list.item_selected.connect(self._on_photo_item_selected)
        self.photo_list.item_deleted.connect(self._on_photo_item_deleted)
        photo_list_layout.addWidget(self.photo_list, stretch=1)
        
        layout.addWidget(photo_list_group, stretch=1)
        
        animation_group = QGroupBox("Display")
        animation_group.setMinimumWidth(250)
        animation_main_layout = QHBoxLayout(animation_group)
        animation_main_layout.setContentsMargins(10, 16, 10, 10)
        animation_main_layout.setSpacing(12)
        
        buttons_row = QVBoxLayout()
        buttons_row.setSpacing(8)
        buttons_row.setAlignment(Qt.AlignLeft)
        buttons_row.setContentsMargins(0, 0, 0, 0)
        
        self.text_fixed_animation_btn = QPushButton("🚫")
        self.text_fixed_animation_btn.setFixedSize(44, 44)
        self.text_fixed_animation_btn.setToolTip("Fixed Animation")
        font = self.text_fixed_animation_btn.font()
        font.setPointSize(28)
        self.text_fixed_animation_btn.setFont(font)
        self.text_fixed_animation_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B3B3B;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
                border: 1px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #2B2B2B;
                border: 1px solid #2E5C8A;
            }
        """)
        self.text_fixed_animation_btn.clicked.connect(self._on_fixed_animation_clicked)
        buttons_row.addWidget(self.text_fixed_animation_btn)
        
        self.text_random_animation_btn = QPushButton("🔀")
        self.text_random_animation_btn.setFixedSize(44, 44)
        self.text_random_animation_btn.setToolTip("Selected Random")
        font = self.text_random_animation_btn.font()
        font.setPointSize(28)
        self.text_random_animation_btn.setFont(font)
        self.text_random_animation_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B3B3B;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
                border: 1px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #2B2B2B;
                border: 1px solid #2E5C8A;
            }
        """)
        self.text_random_animation_btn.clicked.connect(self._on_random_animation_clicked)
        buttons_row.addWidget(self.text_random_animation_btn)
        
        buttons_row.addStretch()
        animation_main_layout.addLayout(buttons_row)
        
        content_column = QHBoxLayout()
        content_column.setSpacing(8)
        content_column.setContentsMargins(0, 0, 0, 0)
        
        animation_layout = QVBoxLayout()
        animation_layout.setContentsMargins(0, 0, 0, 0)
        animation_layout.setSpacing(8)
        
        entrance_layout = QHBoxLayout()
        entrance_layout.setSpacing(8)
        entrance_layout.setContentsMargins(0, 0, 0, 0)
        self.image_entrance_animation_combo = QComboBox()
        self.image_entrance_animation_combo.addItems([
            "Random", "Immediate Show", "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ])
        self.image_entrance_animation_combo.setCurrentText("Random")
        self.image_entrance_animation_combo.currentTextChanged.connect(self._on_entrance_animation_changed)
        entrance_layout.addWidget(self.image_entrance_animation_combo)
        entrance_layout.addStretch()
        self.image_entrance_speed_combo = QComboBox()
        self.image_entrance_speed_combo.addItem("1 fast")
        self.image_entrance_speed_combo.addItems([f"{i}" for i in range(2, 9)])
        self.image_entrance_speed_combo.addItem("9 slow")
        self.image_entrance_speed_combo.setCurrentText("1 fast")
        self.image_entrance_speed_combo.currentTextChanged.connect(self._on_entrance_speed_changed)
        entrance_layout.addWidget(self.image_entrance_speed_combo)
        animation_layout.addLayout(entrance_layout)
        
        exit_layout = QHBoxLayout()
        exit_layout.setSpacing(8)
        exit_layout.setContentsMargins(0, 0, 0, 0)
        self.image_exit_animation_combo = QComboBox()
        self.image_exit_animation_combo.addItems([
            "Random", "Immediate Show", "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ])
        self.image_exit_animation_combo.setCurrentText("Random")
        self.image_exit_animation_combo.currentTextChanged.connect(self._on_exit_animation_changed)
        exit_layout.addWidget(self.image_exit_animation_combo)
        exit_layout.addStretch()
        self.image_exit_speed_combo = QComboBox()
        self.image_exit_speed_combo.addItem("1 fast")
        self.image_exit_speed_combo.addItems([f"{i}" for i in range(2, 9)])
        self.image_exit_speed_combo.addItem("9 slow")
        self.image_exit_speed_combo.setCurrentText("1 fast")
        self.image_exit_speed_combo.currentTextChanged.connect(self._on_exit_speed_changed)
        exit_layout.addWidget(self.image_exit_speed_combo)
        animation_layout.addLayout(exit_layout)
        
        hold_layout = QHBoxLayout()
        hold_layout.setSpacing(8)
        hold_layout.setContentsMargins(0, 0, 0, 0)
        hold_layout.setAlignment(Qt.AlignRight)
        self.image_hold_time_label = QLabel("Hold Time:")
        self.image_hold_time_label.setStyleSheet("font-size: 12px;")
        hold_layout.addWidget(self.image_hold_time_label)
        self.image_hold_time_spin = QDoubleSpinBox()
        self.image_hold_time_spin.setMinimum(0.0)
        self.image_hold_time_spin.setMaximum(999.9)
        self.image_hold_time_spin.setSingleStep(0.1)
        self.image_hold_time_spin.setDecimals(1)
        self.image_hold_time_spin.setSuffix(" second")
        self.image_hold_time_spin.setValue(0.0)
        self.image_hold_time_spin.valueChanged.connect(self._on_hold_time_changed)
        hold_layout.addWidget(self.image_hold_time_spin)
        animation_layout.addLayout(hold_layout)
        
        content_column.addLayout(animation_layout)
        content_column.addStretch()
        animation_main_layout.addLayout(content_column, stretch=9)
        
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
    
    def _on_fixed_animation_clicked(self):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        # Set both entrance and exit to "Immediate Show"
        self.image_entrance_animation_combo.setCurrentText("Immediate Show")
        self.image_exit_animation_combo.setCurrentText("Immediate Show")
        
        self.current_element["properties"]["animation"]["entrance"] = "Immediate Show"
        self.current_element["properties"]["animation"]["entrance_animation"] = get_animation_index("Immediate Show")
        self.current_element["properties"]["animation"]["exit"] = "Immediate Show"
        self.current_element["properties"]["animation"]["exit_animation"] = get_animation_index("Immediate Show")
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_animation_fixed", True)
        self._trigger_autosave()
    
    def _on_random_animation_clicked(self):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.image_entrance_animation_combo.setCurrentText("Random")
        self.image_exit_animation_combo.setCurrentText("Random")
        
        self.current_element["properties"]["animation"]["entrance"] = "Random"
        self.current_element["properties"]["animation"]["entrance_animation"] = get_animation_index("Random")
        self.current_element["properties"]["animation"]["exit"] = "Random"
        self.current_element["properties"]["animation"]["exit_animation"] = get_animation_index("Random")
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("image_animation_random", True)
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
                self.photo_list.set_photos(self.current_element["properties"]["photo_list"])
                self.property_changed.emit("photo_list", self.current_element["properties"]["photo_list"])
                self._trigger_autosave()
    
    def _on_photo_item_selected(self, index: int):
        pass
    
    def _on_photo_item_deleted(self, index: int):
        if self.current_element and self.current_program:
            if "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
                photo_list = self.current_element["properties"]["photo_list"]
                if 0 <= index < len(photo_list):
                    self.current_element["properties"]["photo_list"].pop(index)
                    if len(photo_list) > 0:
                        new_active = min(index, len(photo_list) - 1)
                    else:
                        new_active = -1
                    self.photo_list.set_photos(self.current_element["properties"]["photo_list"])
                    if new_active >= 0:
                        self.photo_list.set_active_index(new_active)
                    self.current_program.modified = datetime.now().isoformat()
                    self.property_changed.emit("photo_list", self.current_element["properties"]["photo_list"])
                    self._trigger_autosave()
    
    def _on_photo_delete(self):
        active_index = self.photo_list.get_active_index()
        if active_index >= 0 and self.current_element:
            if "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
                photo_list = self.current_element["properties"]["photo_list"]
                if 0 <= active_index < len(photo_list):
                    self.current_element["properties"]["photo_list"].pop(active_index)
                    if len(photo_list) > 0:
                        new_active = min(active_index, len(photo_list) - 1)
                    else:
                        new_active = -1
                    self.photo_list.set_photos(self.current_element["properties"]["photo_list"])
                    if new_active >= 0:
                        self.photo_list.set_active_index(new_active)
                    self.current_program.modified = datetime.now().isoformat()
                    self.property_changed.emit("photo_list", self.current_element["properties"]["photo_list"])
                    self._trigger_autosave()
    
    def _on_photo_up(self):
        active_index = self.photo_list.get_active_index()
        if active_index > 0 and self.current_element:
            if "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
                photo_list = self.current_element["properties"]["photo_list"]
                new_index = self.photo_list.move_item_up(active_index)
                photo_list[active_index], photo_list[active_index - 1] = photo_list[active_index - 1], photo_list[active_index]
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("photo_list", photo_list)
                self._trigger_autosave()
    
    def _on_photo_down(self):
        active_index = self.photo_list.get_active_index()
        if self.current_element and "properties" in self.current_element and "photo_list" in self.current_element["properties"]:
            photo_list = self.current_element["properties"]["photo_list"]
            if 0 <= active_index < len(photo_list) - 1:
                new_index = self.photo_list.move_item_down(active_index)
                photo_list[active_index], photo_list[active_index + 1] = photo_list[active_index + 1], photo_list[active_index]
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("photo_list", photo_list)
                self._trigger_autosave()
    

