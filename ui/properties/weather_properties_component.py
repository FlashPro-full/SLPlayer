from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox, QCompleter,
                             QToolButton, QButtonGroup)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
from ui.properties.base_properties_component import BasePropertiesComponent
from config.animation_effects import get_animation_index, get_animation_name


class WeatherPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.city_list = []
        self._load_city_list()
        self.init_ui()
    
    def _load_city_list(self):
        """Load city list from file"""
        try:
            city_file = Path(__file__).parent.parent.parent / "resources" / "Reference" / "resources" / "weather" / "china-city-list.txt"
            if city_file.exists():
                with open(city_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Skip header lines
                    for line in lines[2:]:  # Skip first 2 lines (header)
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            city_name = parts[2]  # Chinese city name
                            if city_name:
                                self.city_list.append(city_name)
        except Exception:
            # If file not found, use empty list
            self.city_list = []
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: #FAFAFA;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #333333;
            }
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #FFFFFF;
                font-size: 12px;
            }
            QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #FFFFFF;
                font-size: 12px;
            }
            QPushButton {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 8px;
                background-color: #FFFFFF;
                font-size: 12px;
            }
            QCheckBox {
                font-size: 12px;
            }
        """)
        
        # Area attribute group (same as text)
        area_group = QGroupBox("Area attribute")
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(10, 16, 10, 10)
        area_layout.setSpacing(8)
        
        # Coordinates
        coords_row = QHBoxLayout()
        coords_row.setSpacing(6)
        coords_label = QLabel("📍")
        coords_label.setStyleSheet("font-size: 16px;")
        self.weather_coords_x = QLineEdit()
        self.weather_coords_x.setPlaceholderText("0")
        self.weather_coords_x.setMinimumWidth(70)
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.weather_coords_y = QLineEdit()
        self.weather_coords_y.setPlaceholderText("0")
        self.weather_coords_y.setMinimumWidth(70)
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.weather_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.weather_coords_y)
        area_layout.addLayout(coords_row)
        
        # Dimensions
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.weather_dims_width = QLineEdit()
        self.weather_dims_width.setPlaceholderText("1920")
        self.weather_dims_width.setMinimumWidth(70)
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.weather_dims_height = QLineEdit()
        self.weather_dims_height.setPlaceholderText("1080")
        self.weather_dims_height.setMinimumWidth(70)
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.weather_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.weather_dims_height)
        area_layout.addLayout(dims_row)
        
        # Frame options
        frame_group_layout = QVBoxLayout()
        frame_group_layout.setSpacing(4)
        
        effect_layout = QHBoxLayout()
        effect_layout.addWidget(QLabel("Effect:"))
        self.weather_frame_effect_combo = QComboBox()
        self.weather_frame_effect_combo.addItems(["static", "rotate", "twinkle"])
        self.weather_frame_effect_combo.setCurrentText("static")
        self.weather_frame_effect_combo.setEnabled(True)
        self.weather_frame_effect_combo.currentTextChanged.connect(self._on_frame_effect_changed)
        effect_layout.addWidget(self.weather_frame_effect_combo, stretch=1)
        frame_group_layout.addLayout(effect_layout)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.weather_frame_speed_combo = QComboBox()
        self.weather_frame_speed_combo.addItems(["slow", "in", "fast"])
        self.weather_frame_speed_combo.setCurrentText("in")
        self.weather_frame_speed_combo.setEnabled(True)
        self.weather_frame_speed_combo.currentTextChanged.connect(self._on_frame_speed_changed)
        speed_layout.addWidget(self.weather_frame_speed_combo, stretch=1)
        frame_group_layout.addLayout(speed_layout)
        
        area_layout.addLayout(frame_group_layout)
        area_layout.addStretch()
        
        main_layout.addWidget(area_group)
        
        # No title group
        no_title_group = QGroupBox("No title group")
        no_title_layout = QVBoxLayout(no_title_group)
        no_title_layout.setContentsMargins(10, 16, 10, 10)
        no_title_layout.setSpacing(8)
        
        # City search, Font Family, Horizontal Align
        city_row = QHBoxLayout()
        city_row.setSpacing(8)
        
        # City search input with autocomplete
        city_label = QLabel("City:")
        self.weather_city_input = QLineEdit()
        self.weather_city_input.setPlaceholderText("Search city...")
        self.weather_city_input.textChanged.connect(self._on_city_changed)
        
        # Setup autocomplete
        completer = QCompleter(self.city_list, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.weather_city_input.setCompleter(completer)
        
        city_row.addWidget(city_label)
        city_row.addWidget(self.weather_city_input, stretch=1)
        
        # Font Family
        font_label = QLabel("Font Family:")
        self.weather_font_family_combo = QComboBox()
        self.weather_font_family_combo.addItems(["Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", "Comic Sans MS"])
        self.weather_font_family_combo.currentTextChanged.connect(self._on_font_family_changed)
        city_row.addWidget(font_label)
        city_row.addWidget(self.weather_font_family_combo)
        
        # Horizontal Align buttons
        align_label = QLabel("Align:")
        self.weather_align_left_btn = QToolButton()
        self.weather_align_left_btn.setText("◀")
        self.weather_align_left_btn.setCheckable(True)
        self.weather_align_left_btn.setToolTip("Left")
        self.weather_align_center_btn = QToolButton()
        self.weather_align_center_btn.setText("⬌")
        self.weather_align_center_btn.setCheckable(True)
        self.weather_align_center_btn.setToolTip("Center")
        self.weather_align_right_btn = QToolButton()
        self.weather_align_right_btn.setText("▶")
        self.weather_align_right_btn.setCheckable(True)
        self.weather_align_right_btn.setToolTip("Right")
        
        self.weather_align_group = QButtonGroup(self)
        self.weather_align_group.addButton(self.weather_align_left_btn, 0)
        self.weather_align_group.addButton(self.weather_align_center_btn, 1)
        self.weather_align_group.addButton(self.weather_align_right_btn, 2)
        self.weather_align_group.buttonClicked.connect(self._on_align_changed)
        
        # Set center as default
        self.weather_align_center_btn.setChecked(True)
        
        align_btn_layout = QHBoxLayout()
        align_btn_layout.setSpacing(2)
        align_btn_layout.addWidget(self.weather_align_left_btn)
        align_btn_layout.addWidget(self.weather_align_center_btn)
        align_btn_layout.addWidget(self.weather_align_right_btn)
        
        city_row.addWidget(align_label)
        city_row.addLayout(align_btn_layout)
        city_row.addStretch()
        
        no_title_layout.addLayout(city_row)
        
        # Display Mode selector
        display_mode_layout = QHBoxLayout()
        display_mode_label = QLabel("Display Mode:")
        self.weather_display_mode_combo = QComboBox()
        self.weather_display_mode_combo.addItems(["Multiline mode", "Single line mode"])
        self.weather_display_mode_combo.currentTextChanged.connect(self._on_display_mode_changed)
        display_mode_layout.addWidget(display_mode_label)
        display_mode_layout.addWidget(self.weather_display_mode_combo)
        display_mode_layout.addStretch()
        no_title_layout.addLayout(display_mode_layout)
        
        # Attributes
        attributes_layout = QVBoxLayout()
        attributes_layout.setSpacing(6)
        
        # City attribute
        self._add_attribute_row(attributes_layout, "city", "City", "#FF0000")
        # Date attribute
        self._add_attribute_row(attributes_layout, "date", "Date", "#0000FF")
        # Temperature attribute (with oC and F buttons)
        self._add_temperature_row(attributes_layout)
        # Weather attribute
        self._add_attribute_row(attributes_layout, "weather", "Weather", "#00FF00")
        # Wind speed and Direction attribute
        self._add_attribute_row(attributes_layout, "wind", "Wind speed and Direction", "#FF00FF")
        # Air Humidity attribute
        self._add_attribute_row(attributes_layout, "humidity", "Air Humidity", "#00FFFF")
        # Air Quality attribute
        self._add_attribute_row(attributes_layout, "air_quality", "Air Quality", "#FFFF00")
        # PM 2.5 attribute
        self._add_attribute_row(attributes_layout, "pm25", "PM 2.5", "#FFA500")
        
        no_title_layout.addLayout(attributes_layout)
        no_title_layout.addStretch()
        
        main_layout.addWidget(no_title_group)
        
        # Animation group (same as text)
        animation_group = QGroupBox("Animation")
        animation_layout = QVBoxLayout(animation_group)
        animation_layout.setContentsMargins(10, 16, 10, 10)
        animation_layout.setSpacing(8)
        
        # Fixed and Random buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)
        self.weather_fixed_animation_btn = QPushButton("🚫")
        self.weather_fixed_animation_btn.setFixedSize(44, 44)
        self.weather_fixed_animation_btn.setToolTip("Fixed Animation")
        font = self.weather_fixed_animation_btn.font()
        font.setPointSize(28)
        self.weather_fixed_animation_btn.setFont(font)
        self.weather_fixed_animation_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E8F4F8;
                border: 1px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #D0E8F2;
                border: 1px solid #2E5C8A;
            }
        """)
        self.weather_fixed_animation_btn.clicked.connect(self._on_fixed_animation_clicked)
        buttons_row.addWidget(self.weather_fixed_animation_btn)
        
        self.weather_random_animation_btn = QPushButton("🔀")
        self.weather_random_animation_btn.setFixedSize(44, 44)
        self.weather_random_animation_btn.setToolTip("Selected Random")
        font = self.weather_random_animation_btn.font()
        font.setPointSize(28)
        self.weather_random_animation_btn.setFont(font)
        self.weather_random_animation_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E8F4F8;
                border: 1px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #D0E8F2;
                border: 1px solid #2E5C8A;
            }
        """)
        self.weather_random_animation_btn.clicked.connect(self._on_random_animation_clicked)
        buttons_row.addWidget(self.weather_random_animation_btn)
        buttons_row.addStretch()
        animation_layout.addLayout(buttons_row)
        
        # Entrance animation
        entrance_layout = QHBoxLayout()
        entrance_layout.addWidget(QLabel("Entrance:"))
        self.weather_entrance_animation_combo = QComboBox()
        animations = self._get_animation_list()
        self.weather_entrance_animation_combo.addItems(animations)
        self.weather_entrance_animation_combo.currentTextChanged.connect(self._on_entrance_animation_changed)
        entrance_layout.addWidget(self.weather_entrance_animation_combo, stretch=1)
        animation_layout.addLayout(entrance_layout)
        
        entrance_speed_layout = QHBoxLayout()
        entrance_speed_layout.addWidget(QLabel("Speed:"))
        self.weather_entrance_speed_combo = QComboBox()
        self.weather_entrance_speed_combo.addItem("1 fast")
        self.weather_entrance_speed_combo.addItems([f"{i}" for i in range(2, 9)])
        self.weather_entrance_speed_combo.addItem("9 slow")
        self.weather_entrance_speed_combo.setCurrentText("1 fast")
        self.weather_entrance_speed_combo.setMinimumWidth(80)
        self.weather_entrance_speed_combo.currentTextChanged.connect(self._on_entrance_speed_changed)
        entrance_speed_layout.addWidget(self.weather_entrance_speed_combo)
        animation_layout.addLayout(entrance_speed_layout)
        
        # Exit animation
        exit_layout = QHBoxLayout()
        exit_layout.addWidget(QLabel("Exit:"))
        self.weather_exit_animation_combo = QComboBox()
        self.weather_exit_animation_combo.addItems(animations)
        self.weather_exit_animation_combo.currentTextChanged.connect(self._on_exit_animation_changed)
        exit_layout.addWidget(self.weather_exit_animation_combo, stretch=1)
        animation_layout.addLayout(exit_layout)
        
        exit_speed_layout = QHBoxLayout()
        exit_speed_layout.addWidget(QLabel("Speed:"))
        self.weather_exit_speed_combo = QComboBox()
        self.weather_exit_speed_combo.addItem("1 fast")
        self.weather_exit_speed_combo.addItems([f"{i}" for i in range(2, 9)])
        self.weather_exit_speed_combo.addItem("9 slow")
        self.weather_exit_speed_combo.setCurrentText("1 fast")
        self.weather_exit_speed_combo.setMinimumWidth(80)
        self.weather_exit_speed_combo.currentTextChanged.connect(self._on_exit_speed_changed)
        exit_speed_layout.addWidget(self.weather_exit_speed_combo)
        animation_layout.addLayout(exit_speed_layout)
        
        # Hold time
        hold_time_layout = QHBoxLayout()
        hold_time_layout.addWidget(QLabel("Hold Time:"))
        from PyQt5.QtWidgets import QDoubleSpinBox
        self.weather_hold_time = QDoubleSpinBox()
        self.weather_hold_time.setMinimum(0.0)
        self.weather_hold_time.setMaximum(999.0)
        self.weather_hold_time.setSingleStep(0.1)
        self.weather_hold_time.setValue(5.0)
        self.weather_hold_time.valueChanged.connect(self._on_hold_time_changed)
        hold_time_layout.addWidget(self.weather_hold_time)
        hold_time_layout.addStretch()
        animation_layout.addLayout(hold_time_layout)
        
        animation_layout.addStretch()
        main_layout.addWidget(animation_group)
        
        main_layout.addStretch()
        
        # Connect signals
        self.weather_coords_x.textChanged.connect(self._on_coords_changed)
        self.weather_coords_y.textChanged.connect(self._on_coords_changed)
        self.weather_dims_width.textChanged.connect(self._on_dims_changed)
        self.weather_dims_height.textChanged.connect(self._on_dims_changed)
    
    def _add_attribute_row(self, layout, key, label, default_color):
        """Add an attribute row with checkbox and color button"""
        row = QHBoxLayout()
        row.setSpacing(8)
        
        check = QCheckBox(label)
        check.setObjectName(f"weather_{key}_check")
        check.toggled.connect(lambda checked, k=key: self._on_attribute_enabled_changed(k, checked))
        row.addWidget(check)
        row.addStretch()
        
        color_btn = QPushButton("")
        color_btn.setObjectName(f"weather_{key}_color_btn")
        color_btn.setStyleSheet(f"background-color: {default_color};")
        color_btn.setFixedSize(30, 25)
        color_btn.clicked.connect(lambda checked, k=key: self._on_attribute_color_clicked(k))
        row.addWidget(color_btn)
        
        layout.addLayout(row)
        
        # Store references
        setattr(self, f"weather_{key}_check", check)
        setattr(self, f"weather_{key}_color_btn", color_btn)
    
    def _add_temperature_row(self, layout):
        """Add temperature row with checkbox, oC/F buttons, and color button"""
        row = QHBoxLayout()
        row.setSpacing(8)
        
        check = QCheckBox("Temp")
        check.setObjectName("weather_temp_check")
        check.toggled.connect(lambda checked: self._on_attribute_enabled_changed("temp", checked))
        row.addWidget(check)
        row.addStretch()
        
        # oC and F buttons
        self.weather_temp_unit_c_btn = QToolButton()
        self.weather_temp_unit_c_btn.setText("°C")
        self.weather_temp_unit_c_btn.setCheckable(True)
        self.weather_temp_unit_c_btn.setChecked(True)
        self.weather_temp_unit_c_btn.clicked.connect(lambda: self._on_temp_unit_changed("C"))
        
        self.weather_temp_unit_f_btn = QToolButton()
        self.weather_temp_unit_f_btn.setText("°F")
        self.weather_temp_unit_f_btn.setCheckable(True)
        self.weather_temp_unit_f_btn.clicked.connect(lambda: self._on_temp_unit_changed("F"))
        
        self.weather_temp_unit_group = QButtonGroup(self)
        self.weather_temp_unit_group.addButton(self.weather_temp_unit_c_btn, 0)
        self.weather_temp_unit_group.addButton(self.weather_temp_unit_f_btn, 1)
        
        temp_unit_layout = QHBoxLayout()
        temp_unit_layout.setSpacing(2)
        temp_unit_layout.addWidget(self.weather_temp_unit_c_btn)
        temp_unit_layout.addWidget(self.weather_temp_unit_f_btn)
        row.addLayout(temp_unit_layout)
        
        color_btn = QPushButton("")
        color_btn.setObjectName("weather_temp_color_btn")
        color_btn.setStyleSheet("background-color: #FF0000;")
        color_btn.setFixedSize(30, 25)
        color_btn.clicked.connect(lambda: self._on_attribute_color_clicked("temp"))
        row.addWidget(color_btn)
        
        layout.addLayout(row)
        
        # Store references
        setattr(self, "weather_temp_check", check)
        setattr(self, "weather_temp_color_btn", color_btn)
    
    def _get_animation_list(self):
        """Get list of available animations"""
        animations = ["Immediate Show", "Random"]
        for i in range(100):  # Assuming max 100 animations
            name = get_animation_name(i)
            if name and name not in animations:
                animations.append(name)
        return animations
    
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
        
        # Area attribute
        x = element_props.get("x", 0)
        y = element_props.get("y", 0)
        self.weather_coords_x.blockSignals(True)
        self.weather_coords_y.blockSignals(True)
        self.weather_coords_x.setText(str(x))
        self.weather_coords_y.setText(str(y))
        self.weather_coords_x.blockSignals(False)
        self.weather_coords_y.blockSignals(False)
        
        width = element_props.get("width", default_width)
        height = element_props.get("height", default_height)
        self.weather_dims_width.blockSignals(True)
        self.weather_dims_height.blockSignals(True)
        self.weather_dims_width.setText(str(width))
        self.weather_dims_height.setText(str(height))
        self.weather_dims_width.blockSignals(False)
        self.weather_dims_height.blockSignals(False)
        
        # Frame
        frame_props = element_props.get("frame", {})
        # Effect and speed are always enabled (no checkbox to disable frame)
        self.weather_frame_effect_combo.setEnabled(True)
        self.weather_frame_speed_combo.setEnabled(True)
        
        effect = frame_props.get("effect", "static") if isinstance(frame_props, dict) else "static"
        effect_index = self.weather_frame_effect_combo.findText(effect)
        if effect_index >= 0:
            self.weather_frame_effect_combo.setCurrentIndex(effect_index)
        
        speed = frame_props.get("speed", "in") if isinstance(frame_props, dict) else "in"
        speed_index = self.weather_frame_speed_combo.findText(speed)
        if speed_index >= 0:
            self.weather_frame_speed_combo.setCurrentIndex(speed_index)
        
        # Weather properties
        weather_props = element_props.get("weather", {})
        
        # City
        city = weather_props.get("city", "")
        self.weather_city_input.blockSignals(True)
        self.weather_city_input.setText(city)
        self.weather_city_input.blockSignals(False)
        
        # Font Family
        font_family = weather_props.get("font_family", "Arial")
        font_index = self.weather_font_family_combo.findText(font_family)
        if font_index >= 0:
            self.weather_font_family_combo.setCurrentIndex(font_index)
        
        # Alignment
        alignment = weather_props.get("alignment", "center")
        if alignment == "left":
            self.weather_align_left_btn.setChecked(True)
        elif alignment == "right":
            self.weather_align_right_btn.setChecked(True)
        else:
            self.weather_align_center_btn.setChecked(True)
        
        # Display Mode
        display_mode = weather_props.get("display_mode", "Multiline mode")
        display_index = self.weather_display_mode_combo.findText(display_mode)
        if display_index >= 0:
            self.weather_display_mode_combo.setCurrentIndex(display_index)
        
        # Attributes
        attributes = ["city", "date", "temp", "weather", "wind", "humidity", "air_quality", "pm25"]
        for attr in attributes:
            check = getattr(self, f"weather_{attr}_check", None)
            color_btn = getattr(self, f"weather_{attr}_color_btn", None)
            if check and color_btn:
                enabled = weather_props.get(f"{attr}_enabled", False)
                color = weather_props.get(f"{attr}_color", "#FF0000")
                check.blockSignals(True)
                check.setChecked(enabled)
                check.blockSignals(False)
                color_btn.setStyleSheet(f"background-color: {color};")
        
        # Temperature unit
        temp_unit = weather_props.get("temp_unit", "C")
        if temp_unit == "F":
            self.weather_temp_unit_f_btn.setChecked(True)
        else:
            self.weather_temp_unit_c_btn.setChecked(True)
        
        # Animation
        animation = element_props.get("animation", {})
        entrance_animation = animation.get("entrance", "Random")
        entrance_index = self.weather_entrance_animation_combo.findText(entrance_animation)
        if entrance_index >= 0:
            self.weather_entrance_animation_combo.setCurrentIndex(entrance_index)
        
        entrance_speed = animation.get("entrance_speed", "1 fast")
        entrance_speed_index = self.weather_entrance_speed_combo.findText(entrance_speed)
        if entrance_speed_index >= 0:
            self.weather_entrance_speed_combo.setCurrentIndex(entrance_speed_index)
        
        exit_animation = animation.get("exit", "Random")
        exit_index = self.weather_exit_animation_combo.findText(exit_animation)
        if exit_index >= 0:
            self.weather_exit_animation_combo.setCurrentIndex(exit_index)
        
        exit_speed = animation.get("exit_speed", "1 fast")
        exit_speed_index = self.weather_exit_speed_combo.findText(exit_speed)
        if exit_speed_index >= 0:
            self.weather_exit_speed_combo.setCurrentIndex(exit_speed_index)
        
        hold_time = animation.get("hold_time", 5.0)
        self.weather_hold_time.blockSignals(True)
        self.weather_hold_time.setValue(hold_time)
        self.weather_hold_time.blockSignals(False)
    
    def _update_weather_property(self, key: str, value):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "weather" not in self.current_element["properties"]:
            self.current_element["properties"]["weather"] = {}
        self.current_element["properties"]["weather"][key] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit(f"weather_{key}", value)
        self._trigger_autosave()
    
    def _on_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            x = int(self.weather_coords_x.text() or "0")
            y = int(self.weather_coords_y.text() or "0")
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
            self.property_changed.emit("weather_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            width = int(self.weather_dims_width.text() or "640")
            height = int(self.weather_dims_height.text() or "480")
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
            self.property_changed.emit("weather_size", (width, height))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_frame_effect_changed(self, effect: str):
        self._update_frame_property("effect", effect)
    
    def _on_frame_speed_changed(self, speed: str):
        self._update_frame_property("speed", speed)
    
    def _update_frame_property(self, key: str, value):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "frame" not in self.current_element["properties"]:
            self.current_element["properties"]["frame"] = {}
        self.current_element["properties"]["frame"][key] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit(f"weather_frame_{key}", value)
        self._trigger_autosave()
    
    def _on_city_changed(self, text: str):
        self._update_weather_property("city", text)
    
    def _on_font_family_changed(self, font_family: str):
        self._update_weather_property("font_family", font_family)
    
    def _on_align_changed(self, button):
        if button == self.weather_align_left_btn:
            alignment = "left"
        elif button == self.weather_align_right_btn:
            alignment = "right"
        else:
            alignment = "center"
        self._update_weather_property("alignment", alignment)
    
    def _on_display_mode_changed(self, mode: str):
        self._update_weather_property("display_mode", mode)
    
    def _on_attribute_enabled_changed(self, key: str, enabled: bool):
        self._update_weather_property(f"{key}_enabled", enabled)
    
    def _on_attribute_color_clicked(self, key: str):
        color_btn = getattr(self, f"weather_{key}_color_btn", None)
        if not color_btn:
            return
        
        current_color = QColor("#FF0000")
        current_style = color_btn.styleSheet()
        if "background-color:" in current_style:
            try:
                color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                current_color = QColor(color_str)
            except:
                pass
        
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_weather_property(f"{key}_color", color.name())
            color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_temp_unit_changed(self, unit: str):
        self._update_weather_property("temp_unit", unit)
    
    def _on_entrance_animation_changed(self, animation: str):
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        self.current_element["properties"]["animation"]["entrance"] = animation
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("weather_entrance_animation", animation)
        self._trigger_autosave()
    
    def _on_entrance_speed_changed(self, speed: str):
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        self.current_element["properties"]["animation"]["entrance_speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("weather_entrance_speed", speed)
        self._trigger_autosave()
    
    def _on_exit_animation_changed(self, animation: str):
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        self.current_element["properties"]["animation"]["exit"] = animation
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("weather_exit_animation", animation)
        self._trigger_autosave()
    
    def _on_exit_speed_changed(self, speed: str):
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        self.current_element["properties"]["animation"]["exit_speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("weather_exit_speed", speed)
        self._trigger_autosave()
    
    def _on_hold_time_changed(self, value: float):
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        self.current_element["properties"]["animation"]["hold_time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("weather_hold_time", value)
        self._trigger_autosave()
    
    def _on_fixed_animation_clicked(self):
        """Set entrance and exit animations to Immediate Show"""
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        self.current_element["properties"]["animation"]["entrance"] = "Immediate Show"
        self.current_element["properties"]["animation"]["exit"] = "Immediate Show"
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("weather_animation_fixed", True)
        self._trigger_autosave()
        # Update UI
        entrance_index = self.weather_entrance_animation_combo.findText("Immediate Show")
        if entrance_index >= 0:
            self.weather_entrance_animation_combo.setCurrentIndex(entrance_index)
        exit_index = self.weather_exit_animation_combo.findText("Immediate Show")
        if exit_index >= 0:
            self.weather_exit_animation_combo.setCurrentIndex(exit_index)
    
    def _on_random_animation_clicked(self):
        """Set entrance and exit animations to Random"""
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        self.current_element["properties"]["animation"]["entrance"] = "Random"
        self.current_element["properties"]["animation"]["exit"] = "Random"
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("weather_animation_random", True)
        self._trigger_autosave()
        # Update UI
        entrance_index = self.weather_entrance_animation_combo.findText("Random")
        if entrance_index >= 0:
            self.weather_entrance_animation_combo.setCurrentIndex(entrance_index)
        exit_index = self.weather_exit_animation_combo.findText("Random")
        if exit_index >= 0:
            self.weather_exit_animation_combo.setCurrentIndex(exit_index)
