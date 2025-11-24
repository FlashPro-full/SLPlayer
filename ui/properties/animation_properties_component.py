from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox, QTextEdit,
                             QSpinBox, QColorDialog, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat, QFont, QBrush
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent
from ui.widgets.text_editor_toolbar import TextEditorToolbar


class AnimationPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)
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
            QLineEdit, QSpinBox, QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #4A90E2;
            }
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 6px;
                background-color: #000000;
                color: #FFFFFF;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 1px solid #4A90E2;
            }
            QPushButton {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 8px;
                background-color: #FFFFFF;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E8F4F8;
                border: 1px solid #4A90E2;
            }
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 6px;
                background-color: #FFFFFF;
                font-size: 12px;
            }
        """)
        
        # Area attribute group (same as Text)
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
        self.animation_coords_x = QLineEdit()
        self.animation_coords_x.setPlaceholderText("0")
        self.animation_coords_x.setMinimumWidth(70)
        self.animation_coords_x.setText("0")
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.animation_coords_y = QLineEdit()
        self.animation_coords_y.setPlaceholderText("0")
        self.animation_coords_y.setMinimumWidth(70)
        self.animation_coords_y.setText("0")
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.animation_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.animation_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.animation_dims_width = QLineEdit()
        self.animation_dims_width.setPlaceholderText("1920")
        self.animation_dims_width.setMinimumWidth(70)
        self.animation_dims_width.setText("1920")
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.animation_dims_height = QLineEdit()
        self.animation_dims_height.setPlaceholderText("1080")
        self.animation_dims_height.setMinimumWidth(70)
        self.animation_dims_height.setText("1080")
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.animation_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.animation_dims_height)
        area_layout.addLayout(dims_row)
        
        frame_group_layout = QVBoxLayout()
        frame_group_layout.setSpacing(4)
        
        area_layout.addLayout(frame_group_layout)
        area_layout.addStretch()
        main_layout.addWidget(area_group)
        
        # Text editor group
        text_edit_group = QGroupBox("Text editor")
        text_edit_group.setMinimumWidth(400)
        text_edit_layout = QVBoxLayout(text_edit_group)
        text_edit_layout.setContentsMargins(10, 16, 10, 10)
        text_edit_layout.setSpacing(4)
        
        self.animation_text_content_edit = QTextEdit()
        self.animation_text_content_edit.setMinimumHeight(150)
        self.animation_text_content_edit.textChanged.connect(self._on_text_content_changed)
        
        self.animation_text_editor_toolbar = TextEditorToolbar(self.animation_text_content_edit, self)
        self.animation_text_editor_toolbar.format_changed.connect(self._on_format_changed)
        
        text_edit_layout.addWidget(self.animation_text_editor_toolbar)
        text_edit_layout.addWidget(self.animation_text_content_edit, stretch=1)
        
        main_layout.addWidget(text_edit_group, stretch=1)
        
        # Animation style group
        animation_style_group = QGroupBox("Animation style")
        animation_style_group.setMinimumWidth(300)
        animation_style_layout = QVBoxLayout(animation_style_group)
        animation_style_layout.setContentsMargins(10, 16, 10, 10)
        animation_style_layout.setSpacing(8)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        
        # 7 colors gradient flow
        gradient_colors_layout = QVBoxLayout()
        gradient_colors_layout.setSpacing(4)
        gradient_label = QLabel("Gradient Colors (7 colors):")
        gradient_colors_layout.addWidget(gradient_label)
        
        self.gradient_color_buttons = []
        for i in range(7):
            color_row = QHBoxLayout()
            color_row.setSpacing(4)
            color_label = QLabel(f"Color {i+1}:")
            color_btn = QPushButton("Choose Color")
            color_btn.setMinimumWidth(120)
            color_btn.clicked.connect(lambda checked, idx=i: self._on_gradient_color_clicked(idx))
            self.gradient_color_buttons.append(color_btn)
            color_row.addWidget(color_label)
            color_row.addWidget(color_btn, stretch=1)
            gradient_colors_layout.addLayout(color_row)
        
        form_layout.addRow("", gradient_colors_layout)
        
        # Writing direction
        writing_direction_layout = QHBoxLayout()
        self.writing_direction_combo = QComboBox()
        self.writing_direction_combo.addItems(["Horizontal Line Writing", "Vertical Line Writing"])
        self.writing_direction_combo.currentTextChanged.connect(self._on_writing_direction_changed)
        writing_direction_layout.addWidget(self.writing_direction_combo, stretch=1)
        form_layout.addRow("Writing Direction:", writing_direction_layout)
        
        # Character movement
        character_movement_layout = QHBoxLayout()
        self.character_movement_check = QCheckBox("Move one character at one step")
        self.character_movement_check.setChecked(True)
        self.character_movement_check.toggled.connect(self._on_character_movement_changed)
        character_movement_layout.addWidget(self.character_movement_check)
        character_movement_layout.addStretch()
        form_layout.addRow("", character_movement_layout)
        
        # Speed
        speed_layout = QHBoxLayout()
        self.animation_speed_spin = QSpinBox()
        self.animation_speed_spin.setRange(1, 100)
        self.animation_speed_spin.setValue(10)
        self.animation_speed_spin.setSuffix(" chars/sec")
        self.animation_speed_spin.valueChanged.connect(self._on_animation_speed_changed)
        speed_layout.addWidget(self.animation_speed_spin, stretch=1)
        form_layout.addRow("Speed:", speed_layout)
        
        animation_style_layout.addLayout(form_layout)
        animation_style_layout.addStretch()
        
        main_layout.addWidget(animation_style_group)
        main_layout.addStretch()
        
        # Connect signals
        self.animation_coords_x.textChanged.connect(self._on_coords_changed)
        self.animation_coords_y.textChanged.connect(self._on_coords_changed)
        self.animation_dims_width.textChanged.connect(self._on_dims_changed)
        self.animation_dims_height.textChanged.connect(self._on_dims_changed)
    
    def _on_gradient_color_clicked(self, index: int):
        color = QColorDialog.getColor()
        if color.isValid():
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "animation_style" not in self.current_element["properties"]:
                self.current_element["properties"]["animation_style"] = {}
            if "gradient_colors" not in self.current_element["properties"]["animation_style"]:
                self.current_element["properties"]["animation_style"]["gradient_colors"] = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"]
            
            gradient_colors = self.current_element["properties"]["animation_style"]["gradient_colors"]
            while len(gradient_colors) < 7:
                gradient_colors.append("#000000")
            gradient_colors[index] = color.name()
            
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("animation_gradient_color", (index, color.name()))
            self._trigger_autosave()
            
            self.gradient_color_buttons[index].setStyleSheet(f"background-color: {color.name()};")
    
    def _on_writing_direction_changed(self, direction: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation_style" not in self.current_element["properties"]:
            self.current_element["properties"]["animation_style"] = {}
        self.current_element["properties"]["animation_style"]["writing_direction"] = direction
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("animation_writing_direction", direction)
        self._trigger_autosave()
    
    def _on_character_movement_changed(self, enabled: bool):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation_style" not in self.current_element["properties"]:
            self.current_element["properties"]["animation_style"] = {}
        self.current_element["properties"]["animation_style"]["character_movement"] = enabled
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("animation_character_movement", enabled)
        self._trigger_autosave()
    
    def _on_animation_speed_changed(self, speed: int):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation_style" not in self.current_element["properties"]:
            self.current_element["properties"]["animation_style"] = {}
        self.current_element["properties"]["animation_style"]["speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("animation_speed", speed)
        self._trigger_autosave()
    
    def _on_text_content_changed(self):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "text" not in self.current_element["properties"]:
            self.current_element["properties"]["text"] = {}
        
        text_content = self.animation_text_content_edit.toPlainText()
        self.current_element["properties"]["text"]["content"] = text_content
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("animation_text_content", text_content)
        self._trigger_autosave()
    
    def _on_format_changed(self, format_data: Dict):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "text" not in self.current_element["properties"]:
            self.current_element["properties"]["text"] = {}
        if "format" not in self.current_element["properties"]["text"]:
            self.current_element["properties"]["text"]["format"] = {}
        
        self.current_element["properties"]["text"]["format"].update(format_data)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("animation_text_format", format_data)
        self._trigger_autosave()
    
    def _on_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            x = int(self.animation_coords_x.text() or "0")
            y = int(self.animation_coords_y.text() or "0")
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
            self.property_changed.emit("animation_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            width = int(self.animation_dims_width.text() or "640")
            height = int(self.animation_dims_height.text() or "480")
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
            self.property_changed.emit("animation_size", (width, height))
            self._trigger_autosave()
        except ValueError:
            pass
    
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
        self.animation_coords_x.blockSignals(True)
        self.animation_coords_y.blockSignals(True)
        self.animation_coords_x.setText(str(x))
        self.animation_coords_y.setText(str(y))
        self.animation_coords_x.blockSignals(False)
        self.animation_coords_y.blockSignals(False)
        
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        if not width or width <= 0:
            width = default_width
        if not height or height <= 0:
            height = default_height
        
        self.animation_dims_width.blockSignals(True)
        self.animation_dims_height.blockSignals(True)
        self.animation_dims_width.setText(str(width))
        self.animation_dims_height.setText(str(height))
        self.animation_dims_width.blockSignals(False)
        self.animation_dims_height.blockSignals(False)
        
        # Load text content and format
        text_props = element_props.get("text", {})
        if isinstance(text_props, dict):
            text_content = text_props.get("content", "")
            self.animation_text_content_edit.blockSignals(True)
            self.animation_text_content_edit.setPlainText(text_content)
            self.animation_text_content_edit.blockSignals(False)
            
            text_format = text_props.get("format", {})
            self._apply_format_to_text_edit(text_format)
        
        # Load animation style
        animation_style = element_props.get("animation_style", {})
        gradient_colors = animation_style.get("gradient_colors", ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"])
        for i, color_btn in enumerate(self.gradient_color_buttons):
            if i < len(gradient_colors):
                color = gradient_colors[i]
                color_btn.setStyleSheet(f"background-color: {color};")
        
        writing_direction = animation_style.get("writing_direction", "Horizontal Line Writing")
        writing_direction_index = self.writing_direction_combo.findText(writing_direction)
        if writing_direction_index >= 0:
            self.writing_direction_combo.setCurrentIndex(writing_direction_index)
        else:
            self.writing_direction_combo.setCurrentIndex(0)
        
        character_movement = animation_style.get("character_movement", True)
        self.character_movement_check.blockSignals(True)
        self.character_movement_check.setChecked(character_movement)
        self.character_movement_check.blockSignals(False)
        
        speed = animation_style.get("speed", 10)
        self.animation_speed_spin.blockSignals(True)
        self.animation_speed_spin.setValue(speed)
        self.animation_speed_spin.blockSignals(False)
    
    def _apply_format_to_text_edit(self, text_format: Dict):
        """Apply format to text edit similar to text_properties_component"""
        if not text_format:
            return
        
        cursor = self.animation_text_content_edit.textCursor()
        cursor.select(QTextCursor.Document)
        
        char_format = QTextCharFormat()
        font = QFont()
        
        if text_format.get("font_family"):
            font.setFamily(text_format.get("font_family"))
        if text_format.get("font_size"):
            font.setPointSize(text_format.get("font_size"))
        if text_format.get("bold"):
            font.setBold(True)
        if text_format.get("italic"):
            font.setItalic(True)
        if text_format.get("underline"):
            font.setUnderline(True)
        char_format.setFont(font)
        
        if text_format.get("font_color"):
            char_format.setForeground(QColor(text_format.get("font_color")))
        
        text_bg_color_str = text_format.get("text_bg_color")
        if text_bg_color_str:
            text_bg_color = QColor(text_bg_color_str)
            char_format.setBackground(QBrush(text_bg_color))
        else:
            char_format.setBackground(QBrush())
            char_format.clearBackground()
        
        cursor.setCharFormat(char_format)
        cursor.clearSelection()
        self.animation_text_content_edit.setTextCursor(cursor)
