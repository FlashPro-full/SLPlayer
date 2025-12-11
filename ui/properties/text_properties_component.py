from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QGroupBox, QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QFont, QColor, QPen, QBrush
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent
from config.animation_effects import get_animation_index, get_animation_name
from ui.widgets.text_editor_toolbar import TextEditorToolbar


class TextPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        main_layout.setAlignment(Qt.AlignTop)
        
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
                background-color: #000000;
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
                background-color: #4B4B4B;
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
        self.text_coords_x = QLineEdit()
        self.text_coords_x.setPlaceholderText("0")
        self.text_coords_x.setMinimumWidth(70)
        self.text_coords_x.setText("0")
        self.text_coords_x.textChanged.connect(self._on_text_coords_changed)
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        self.text_coords_y = QLineEdit()
        self.text_coords_y.setPlaceholderText("0")
        self.text_coords_y.setMinimumWidth(70)
        self.text_coords_y.setText("0")
        self.text_coords_y.textChanged.connect(self._on_text_coords_changed)
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.text_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.text_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.text_dims_width = QLineEdit()
        self.text_dims_width.setPlaceholderText("1920")
        self.text_dims_width.setMinimumWidth(70)
        self.text_dims_width.setText("1920")
        self.text_dims_width.textChanged.connect(self._on_text_dims_changed)
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.text_dims_height = QLineEdit()
        self.text_dims_height.setPlaceholderText("1080")
        self.text_dims_height.setMinimumWidth(70)
        self.text_dims_height.setText("1080")
        self.text_dims_height.textChanged.connect(self._on_text_dims_changed)
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.text_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.text_dims_height)
        area_layout.addLayout(dims_row)
        
        main_layout.addWidget(area_group)
        
        text_edit_group = QGroupBox("Text Content")
        text_edit_layout = QVBoxLayout(text_edit_group)
        text_edit_layout.setContentsMargins(10, 16, 10, 10)
        text_edit_layout.setSpacing(8)
        
        self.text_content_edit = QTextEdit()
        self.text_content_edit.setMinimumHeight(180)
        self.text_content_edit.setPlaceholderText("Enter text content here...")
        self.text_content_edit.textChanged.connect(self._on_text_content_changed)
        
        self.text_editor_toolbar = TextEditorToolbar(self.text_content_edit, self)
        self.text_editor_toolbar.format_changed.connect(self._on_format_changed)
        
        text_edit_layout.addWidget(self.text_editor_toolbar)
        text_edit_layout.addWidget(self.text_content_edit, stretch=1)
        
        main_layout.addWidget(text_edit_group)
        
        display_group = QGroupBox("Display")
        display_group.setMinimumWidth(250)
        display_main_layout = QHBoxLayout(display_group)
        display_main_layout.setContentsMargins(10, 16, 10, 10)
        display_main_layout.setSpacing(12)
        
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
        display_main_layout.addLayout(buttons_row)
        
        content_column = QHBoxLayout()
        content_column.setSpacing(8)
        content_column.setContentsMargins(0, 0, 0, 0)
        
        animation_layout = QVBoxLayout()
        animation_layout.setContentsMargins(0, 0, 0, 0)
        animation_layout.setSpacing(8)
        
        entrance_layout = QHBoxLayout()
        entrance_layout.setSpacing(8)
        entrance_layout.setContentsMargins(0, 0, 0, 0)
        self.text_entrance_animation_combo = QComboBox()
        self.text_entrance_animation_combo.addItems([
            "Random", "Immediate Show", "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ])
        self.text_entrance_animation_combo.setCurrentText("Random")
        self.text_entrance_animation_combo.currentTextChanged.connect(self._on_entrance_animation_changed)
        entrance_layout.addWidget(self.text_entrance_animation_combo)
        entrance_layout.addStretch()
        self.text_entrance_speed_combo = QComboBox()
        self.text_entrance_speed_combo.addItem("1 fast")
        self.text_entrance_speed_combo.addItems([f"{i}" for i in range(2, 9)])
        self.text_entrance_speed_combo.addItem("9 slow")
        self.text_entrance_speed_combo.setCurrentText("1 fast")
        self.text_entrance_speed_combo.currentTextChanged.connect(self._on_entrance_speed_changed)
        entrance_layout.addWidget(self.text_entrance_speed_combo)
        animation_layout.addLayout(entrance_layout)
        
        exit_layout = QHBoxLayout()
        exit_layout.setSpacing(8)
        exit_layout.setContentsMargins(0, 0, 0, 0)
        self.text_exit_animation_combo = QComboBox()
        self.text_exit_animation_combo.addItems([
            "Random", "Immediate Clear", "Move Left", "Move Right", "Move Up", "Move Down",
            "Cover Left", "Cover Right", "Cover Up", "Cover Down",
            "Top Left Cover", "Top Right Cover", "Bottom Left Cover", "Bottom Right Cover",
            "Open From Middle", "Up Down Open", "Close From Middle", "Up Down Close",
            "Gradual Change", "Vertical Blinds", "Horizontal Blinds", "Twinkle"
        ])
        self.text_exit_animation_combo.setCurrentText("Random")
        self.text_exit_animation_combo.currentTextChanged.connect(self._on_exit_animation_changed)
        exit_layout.addWidget(self.text_exit_animation_combo)
        exit_layout.addStretch()
        self.text_exit_speed_combo = QComboBox()
        self.text_exit_speed_combo.addItem("1 fast")
        self.text_exit_speed_combo.addItems([f"{i}" for i in range(2, 9)])
        self.text_exit_speed_combo.addItem("9 slow")
        self.text_exit_speed_combo.setCurrentText("1 fast")
        self.text_exit_speed_combo.currentTextChanged.connect(self._on_exit_speed_changed)
        exit_layout.addWidget(self.text_exit_speed_combo)
        animation_layout.addLayout(exit_layout)
        
        hold_layout = QHBoxLayout()
        hold_layout.setSpacing(8)
        hold_layout.setContentsMargins(0, 0, 0, 0)
        hold_layout.setAlignment(Qt.AlignRight)
        self.text_hold_time_label = QLabel("Hold Time:")
        self.text_hold_time_label.setStyleSheet("font-size: 12px;")
        hold_layout.addWidget(self.text_hold_time_label)
        self.text_hold_time = QDoubleSpinBox()
        self.text_hold_time.setMinimum(0.0)
        self.text_hold_time.setMaximum(999.9)
        self.text_hold_time.setSingleStep(0.1)
        self.text_hold_time.setDecimals(1)
        self.text_hold_time.setSuffix(" second")
        self.text_hold_time.setValue(0.0)
        self.text_hold_time.valueChanged.connect(self._on_text_hold_time_changed)
        hold_layout.addWidget(self.text_hold_time)
        animation_layout.addLayout(hold_layout)
        
        content_column.addLayout(animation_layout)
        content_column.addStretch()
        display_main_layout.addLayout(content_column, stretch=9)
        
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
            text_format = text_props.get("format", {})
            if "background_color" in text_props and "text_bg_color" not in text_format:
                text_format["text_bg_color"] = text_props.get("background_color")
        else:
            text_content = str(text_props) if text_props else ""
            text_format = {}
        
        self.text_content_edit.blockSignals(True)
        self.text_content_edit.setPlainText(text_content)
        
        if text_format:
            self._apply_format_to_text_edit(text_format)
        else:
            # Apply default format with white font color, size 12, and center alignment
            default_format = {
                "font_color": "#FFFFFF",
                "font_size": 12,
                "alignment": "center",
                "vertical_alignment": "middle"
            }
            self._apply_format_to_text_edit(default_format)
            # Save default format to element so it persists
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "text" not in self.current_element["properties"]:
                self.current_element["properties"]["text"] = {}
            self.current_element["properties"]["text"]["format"] = default_format
        
        self.text_content_edit.blockSignals(False)
        
        animation = element_props.get("animation", {})
        
        entrance_animation = animation.get("entrance", "Random")
        entrance_animation_index = animation.get("entrance_animation", None)
        if entrance_animation_index is not None:
            entrance_animation = get_animation_name(entrance_animation_index)
        elif isinstance(entrance_animation, int):
            entrance_animation = get_animation_name(entrance_animation)
        entrance_index = self.text_entrance_animation_combo.findText(entrance_animation)
        if entrance_index >= 0:
            self.text_entrance_animation_combo.setCurrentIndex(entrance_index)
        
        entrance_speed = animation.get("entrance_speed", "1 fast")
        entrance_speed_index = self.text_entrance_speed_combo.findText(entrance_speed)
        if entrance_speed_index >= 0:
            self.text_entrance_speed_combo.setCurrentIndex(entrance_speed_index)
        
        exit_animation = animation.get("exit", "Random")
        exit_animation_index = animation.get("exit_animation", None)
        if exit_animation_index is not None:
            exit_animation = get_animation_name(exit_animation_index)
        elif isinstance(exit_animation, int):
            exit_animation = get_animation_name(exit_animation)
        exit_index = self.text_exit_animation_combo.findText(exit_animation)
        if exit_index >= 0:
            self.text_exit_animation_combo.setCurrentIndex(exit_index)
        
        exit_speed = animation.get("exit_speed", "1 fast")
        exit_speed_index = self.text_exit_speed_combo.findText(exit_speed)
        if exit_speed_index >= 0:
            self.text_exit_speed_combo.setCurrentIndex(exit_speed_index)
        
        hold_time = animation.get("hold_time", 5.0)
        self.text_hold_time.blockSignals(True)
        self.text_hold_time.setValue(hold_time)
        self.text_hold_time.blockSignals(False)
    
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
        # Map to XML attributes
        import base64
        self.current_element["properties"]["text"]["play_text"] = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')
        # Html attribute stores rich text format (for now, same as content)
        self.current_element["properties"]["text"]["html"] = text_content
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_content", text_content)
        self._trigger_autosave()
    
    def _on_fixed_animation_clicked(self):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.text_entrance_animation_combo.setCurrentText("Immediate Show")
        self.text_exit_animation_combo.setCurrentText("Immediate Clear")
        
        self.current_element["properties"]["animation"]["entrance"] = "Immediate Show"
        self.current_element["properties"]["animation"]["entrance_animation"] = get_animation_index("Immediate Show")
        self.current_element["properties"]["animation"]["exit"] = "Immediate Clear"
        self.current_element["properties"]["animation"]["exit_animation"] = get_animation_index("Immediate Clear")
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_animation_fixed", True)
        self._trigger_autosave()
    
    def _on_random_animation_clicked(self):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.text_entrance_animation_combo.setCurrentText("Random")
        self.text_exit_animation_combo.setCurrentText("Random")
        
        self.current_element["properties"]["animation"]["entrance"] = "Random"
        self.current_element["properties"]["animation"]["entrance_animation"] = get_animation_index("Random")
        self.current_element["properties"]["animation"]["exit"] = "Random"
        self.current_element["properties"]["animation"]["exit_animation"] = get_animation_index("Random")
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_animation_random", True)
        self._trigger_autosave()
    
    def _on_entrance_animation_changed(self, animation: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["entrance"] = animation
        self.current_element["properties"]["animation"]["entrance_animation"] = get_animation_index(animation)
        self.current_element["properties"]["animation"]["disp_effect"] = get_animation_index(animation)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_entrance_animation", animation)
        self._trigger_autosave()
    
    def _on_entrance_speed_changed(self, speed: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["entrance_speed"] = speed
        speed_num = 4
        if speed == "1 fast":
            speed_num = 1
        elif speed == "9 slow":
            speed_num = 9
        else:
            try:
                speed_num = int(speed)
            except ValueError:
                speed_num = 4
        self.current_element["properties"]["animation"]["disp_time"] = speed_num
        self.current_element["properties"]["animation"]["speed_time_index"] = speed_num
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_entrance_speed", speed)
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
        self.current_element["properties"]["animation"]["clear_effect"] = get_animation_index(animation)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_exit_animation", animation)
        self._trigger_autosave()
    
    def _on_exit_speed_changed(self, speed: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["exit_speed"] = speed
        speed_num = 4
        if speed == "1 fast":
            speed_num = 1
        elif speed == "9 slow":
            speed_num = 9
        else:
            try:
                speed_num = int(speed)
            except ValueError:
                speed_num = 4
        self.current_element["properties"]["animation"]["clear_time"] = speed_num
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_exit_speed", speed)
        self._trigger_autosave()
    
    def _on_text_hold_time_changed(self, value: float):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "text" not in self.current_element["properties"]:
            self.current_element["properties"]["text"] = {}
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["hold_time"] = value
        self.current_element["properties"]["text"]["hold_time"] = int(value * 10)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_hold_time", value)
        self._trigger_autosave()
        if "animation" not in self.current_element["properties"]:
            self.current_element["properties"]["animation"] = {}
        
        self.current_element["properties"]["animation"]["hold_time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_hold_time", value)
        self._trigger_autosave()
    
    def _apply_format_to_text_edit(self, format_data: dict):
        if not self.text_content_edit:
            return
        
        cursor = self.text_content_edit.textCursor()
        cursor.select(QTextCursor.Document)
        char_format = cursor.charFormat()
        
        if format_data.get("font_family"):
            font = char_format.font()
            font.setFamily(format_data["font_family"])
            char_format.setFont(font)
        
        if format_data.get("font_size"):
            font = char_format.font()
            font.setPointSize(format_data["font_size"])
            char_format.setFont(font)
        else:
            # Set default font size if not specified
            font = char_format.font()
            if font.pointSize() < 6:
                font.setPointSize(12)
                char_format.setFont(font)
        
        if format_data.get("bold") is not None:
            char_format.setFontWeight(QFont.Bold if format_data["bold"] else QFont.Normal)
        
        if format_data.get("italic") is not None:
            char_format.setFontItalic(format_data["italic"])
        
        if format_data.get("underline") is not None:
            char_format.setFontUnderline(format_data["underline"])
        
        if format_data.get("font_color"):
            color = QColor(format_data["font_color"])
            char_format.setForeground(color)
            self.text_editor_toolbar.font_color = color
            self.text_editor_toolbar._update_font_color_button()
        else:
            # Set default white color if not specified
            color = QColor(Qt.white)
            char_format.setForeground(color)
            self.text_editor_toolbar.font_color = color
            self.text_editor_toolbar._update_font_color_button()
        
        if format_data.get("text_bg_color"):
            color = QColor(format_data["text_bg_color"])
            char_format.setBackground(color)
            self.text_editor_toolbar.text_bg_color = color
            self.text_editor_toolbar._update_text_bg_color_button()
        else:
            char_format.setBackground(QBrush())
            char_format.clearBackground()
            self.text_editor_toolbar.text_bg_color = None
            self.text_editor_toolbar._update_text_bg_color_button()
        
        if format_data.get("outline") is not None:
            if format_data["outline"]:
                pen = QPen(QColor(Qt.black))
                pen.setStyle(Qt.SolidLine)
                pen.setWidth(1)
                char_format.setTextOutline(pen)
            else:
                pen = QPen(Qt.NoPen)
                char_format.setTextOutline(pen)
        
        font = char_format.font()
        self.text_editor_toolbar.font_size_spin.blockSignals(True)
        self.text_editor_toolbar.font_family_combo.blockSignals(True)
        if format_data.get("font_size"):
            self.text_editor_toolbar.font_size_spin.setValue(format_data["font_size"])
        else:
            self.text_editor_toolbar.font_size_spin.setValue(font.pointSize() if font.pointSize() > 0 else 12)
        if format_data.get("font_family"):
            self.text_editor_toolbar.font_family_combo.setCurrentText(format_data["font_family"])
        else:
            self.text_editor_toolbar.font_family_combo.setCurrentText(font.family())
        self.text_editor_toolbar.font_size_spin.blockSignals(False)
        self.text_editor_toolbar.font_family_combo.blockSignals(False)
        
        self.text_editor_toolbar.bold_btn.blockSignals(True)
        self.text_editor_toolbar.italic_btn.blockSignals(True)
        self.text_editor_toolbar.underline_btn.blockSignals(True)
        if format_data.get("bold") is not None:
            self.text_editor_toolbar.bold_btn.setChecked(format_data["bold"])
        else:
            self.text_editor_toolbar.bold_btn.setChecked(char_format.fontWeight() == QFont.Bold)
        if format_data.get("italic") is not None:
            self.text_editor_toolbar.italic_btn.setChecked(format_data["italic"])
        else:
            self.text_editor_toolbar.italic_btn.setChecked(char_format.fontItalic())
        if format_data.get("underline") is not None:
            self.text_editor_toolbar.underline_btn.setChecked(format_data["underline"])
        else:
            self.text_editor_toolbar.underline_btn.setChecked(char_format.fontUnderline())
        self.text_editor_toolbar.bold_btn.blockSignals(False)
        self.text_editor_toolbar.italic_btn.blockSignals(False)
        self.text_editor_toolbar.underline_btn.blockSignals(False)
        
        if format_data.get("outline") is not None:
            self.text_editor_toolbar.outline_btn.blockSignals(True)
            self.text_editor_toolbar.outline_btn.setChecked(format_data["outline"])
            self.text_editor_toolbar.outline_btn.blockSignals(False)
        
        horizontal_align = Qt.AlignHCenter
        vertical_align = Qt.AlignVCenter
        
        if format_data.get("alignment"):
            alignment_str = format_data["alignment"]
            if alignment_str == "left":
                horizontal_align = Qt.AlignLeft
            elif alignment_str == "center":
                horizontal_align = Qt.AlignHCenter
            elif alignment_str == "right":
                horizontal_align = Qt.AlignRight
        
        if format_data.get("vertical_alignment"):
            vertical_str = format_data["vertical_alignment"]
            if vertical_str == "top":
                vertical_align = Qt.AlignTop
            elif vertical_str == "middle":
                vertical_align = Qt.AlignVCenter
            elif vertical_str == "bottom":
                vertical_align = Qt.AlignBottom
        
        block_format = cursor.blockFormat()
        block_format.setAlignment(horizontal_align)
        cursor.setBlockFormat(block_format)
        
        cursor.setCharFormat(char_format)
        cursor.clearSelection()
        self.text_content_edit.setTextCursor(cursor)
        
        default_char_format = QTextCharFormat()
        default_color = QColor(format_data["font_color"]) if format_data.get("font_color") else QColor(Qt.white)
        default_char_format.setForeground(default_color)
        if format_data.get("font_family"):
            font = default_char_format.font()
            font.setFamily(format_data["font_family"])
            default_char_format.setFont(font)
        if format_data.get("font_size"):
            font = default_char_format.font()
            font.setPointSize(format_data["font_size"])
            default_char_format.setFont(font)
        self.text_content_edit.setCurrentCharFormat(default_char_format)
        
        self.text_editor_toolbar._horizontal_alignment = horizontal_align
        self.text_editor_toolbar._vertical_alignment = vertical_align
        self.text_editor_toolbar.align_left_btn.setChecked(horizontal_align == Qt.AlignLeft)
        self.text_editor_toolbar.align_center_btn.setChecked(horizontal_align == Qt.AlignHCenter)
        self.text_editor_toolbar.align_right_btn.setChecked(horizontal_align == Qt.AlignRight)
        self.text_editor_toolbar.align_top_btn.setChecked(vertical_align == Qt.AlignTop)
        self.text_editor_toolbar.align_middle_btn.setChecked(vertical_align == Qt.AlignVCenter)
        self.text_editor_toolbar.align_bottom_btn.setChecked(vertical_align == Qt.AlignBottom)
    
    def _on_format_changed(self, format_data: dict):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "text" not in self.current_element["properties"]:
            self.current_element["properties"]["text"] = {}
        if "format" not in self.current_element["properties"]["text"]:
            self.current_element["properties"]["text"]["format"] = {}
        
        # Always ensure alignment is in format_data (default to center if not specified)
        if "alignment" not in format_data:
            format_data["alignment"] = "center"
        if "vertical_alignment" not in format_data:
            format_data["vertical_alignment"] = "middle"
        
        self.current_element["properties"]["text"]["format"].update(format_data)
        
        # Map format properties to XML attributes
        if format_data.get("font_color"):
            self.current_element["properties"]["text"]["text_color"] = format_data["font_color"]
        if format_data.get("text_bg_color"):
            self.current_element["properties"]["text"]["background_color"] = format_data["text_bg_color"]
        if format_data.get("font_family"):
            self.current_element["properties"]["text"]["text_font_name"] = format_data["font_family"]
        if format_data.get("font_size"):
            self.current_element["properties"]["text"]["text_font_size"] = format_data["font_size"]
        if format_data.get("outline") is not None:
            self.current_element["properties"]["text"]["use_stroke"] = 1 if format_data["outline"] else 0
        # Always save alignment (default to center if not specified)
        align_str = format_data.get("alignment", "center")
        if align_str == "left":
            self.current_element["properties"]["text"]["content_align"] = 4
            self.current_element["properties"]["text"]["content_h_align"] = 4
        elif align_str == "center":
            self.current_element["properties"]["text"]["content_align"] = 132
            self.current_element["properties"]["text"]["content_h_align"] = 4
        elif align_str == "right":
            self.current_element["properties"]["text"]["content_align"] = 8
            self.current_element["properties"]["text"]["content_h_align"] = 8
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("text_format", format_data)
        self._trigger_autosave()
    

