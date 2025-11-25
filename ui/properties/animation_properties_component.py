from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox, QTextEdit,
                             QSpinBox, QColorDialog, QFormLayout, QGridLayout, QScrollArea,
                             QFrame, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat, QFont, QBrush, QPainter, QPixmap, QPen, QTransform
from typing import Optional, Dict
from datetime import datetime
import math
from ui.properties.base_properties_component import BasePropertiesComponent
from ui.widgets.text_editor_toolbar import TextEditorToolbar
from ui.utils.color_utils import get_gradient_color_at_position
from ui.utils import animation_effects


class AnimationStyleThumbnail(QFrame):
    selected = pyqtSignal(int)
    
    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.is_selected = False
        self.setFixedSize(80, 80)
        self.start_time = QDateTime.currentDateTime()
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(50)
        self.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 2px solid #CCCCCC;
                border-radius: 4px;
            }
        """)
    
    def set_selected(self, selected: bool):
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #000000;
                    border: 3px solid #00FF00;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #000000;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                }
            """)
        self.update()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.index)
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(4, 4, -4, -4)
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        font_metrics = painter.fontMetrics()
        
        text = "ABC"
        text_length = len(text)
        elapsed_ms = self.start_time.msecsTo(QDateTime.currentDateTime())
        elapsed_sec = elapsed_ms / 1000.0
        
        text_width = font_metrics.width(text)
        text_height = font_metrics.height()
        
        base_x = rect.x() + (rect.width() - text_width) / 2
        base_y = rect.y() + rect.height() / 2 + font_metrics.ascent() / 2 - font_metrics.descent() / 2
        
        hold_time = 1.0
        speed = 5
        
        char_positions = []
        current_x = base_x
        for char in text:
            char_width = font_metrics.width(char)
            char_positions.append((current_x, char_width))
            current_x += char_width
        
        is_continuous_scroll = self.index in [0, 1, 2, 3]
        
        if is_continuous_scroll:
            if self.index == 0 or self.index == 1:
                scroll_speed = speed * 10
                scroll_offset = (elapsed_sec * scroll_speed) % text_width
                
                num_repeats = max(3, int((rect.width() + text_width) / max(text_width, 1)) + 2)
                start_offset = -text_width
                
                for repeat_idx in range(num_repeats):
                    if self.index == 0:
                        text_offset_x = start_offset + (repeat_idx * text_width) - scroll_offset
                    else:
                        text_offset_x = start_offset + (repeat_idx * text_width) + scroll_offset
                    
                    if text_offset_x + text_width < rect.x() - text_width or text_offset_x > rect.x() + rect.width() + text_width:
                        continue
                    
                    for i, char in enumerate(text):
                        char_x_base, char_width = char_positions[i]
                        char_height = font_metrics.height()
                        
                        draw_x = int(text_offset_x + (char_x_base - min(pos[0] for pos in char_positions)))
                        draw_y = int(base_y)
                        
                        if draw_x + char_width < rect.x() or draw_x > rect.x() + rect.width():
                            continue
                        
                        color = animation_effects.get_animation_color(self.index, i, text_length, elapsed_sec)
                        
                        painter.save()
                        painter.setPen(QPen(color))
                        painter.setOpacity(1.0)
                        painter.drawText(draw_x, draw_y, char)
                        painter.restore()
            elif self.index == 2 or self.index == 3:
                vertical_char_width = max(font_metrics.width(char) for char in text)
                vertical_text_height = sum(font_metrics.height() for _ in text)
                
                vertical_base_x = rect.x() + (rect.width() - vertical_char_width) / 2
                vertical_base_y = rect.y()
                
                scroll_speed = speed * 10
                scroll_offset = (elapsed_sec * scroll_speed) % max(vertical_text_height, 1)
                
                num_repeats = max(3, int((rect.height() + vertical_text_height) / max(vertical_text_height, 1)) + 2)
                start_offset = -vertical_text_height
                
                char_heights = []
                current_y = 0
                for char in text:
                    char_height = font_metrics.height()
                    char_heights.append((current_y, char_height))
                    current_y += char_height
                
                for repeat_idx in range(num_repeats):
                    if self.index == 2:
                        text_offset_y = start_offset + (repeat_idx * vertical_text_height) - scroll_offset
                    else:
                        text_offset_y = start_offset + (repeat_idx * vertical_text_height) + scroll_offset
                    
                    if text_offset_y + vertical_text_height < rect.y() - vertical_text_height or text_offset_y > rect.y() + rect.height() + vertical_text_height:
                        continue
                    
                    for i, char in enumerate(text):
                        char_y_offset, char_height = char_heights[i]
                        char_width = font_metrics.width(char)
                        ascent = font_metrics.ascent()
                        
                        draw_x = int(vertical_base_x + (vertical_char_width - char_width) / 2)
                        draw_y = int(vertical_base_y + text_offset_y + char_y_offset + ascent)
                        
                        if draw_y + char_height < rect.y() or draw_y > rect.y() + rect.height():
                            continue
                        
                        color = animation_effects.get_animation_color(self.index, i, text_length, elapsed_sec)
                        
                        painter.save()
                        painter.setPen(QPen(color))
                        painter.setOpacity(1.0)
                        painter.drawText(draw_x, draw_y, char)
                        painter.restore()
        else:
            for i, char in enumerate(text):
                char_x_base, char_width = char_positions[i]
                char_height = font_metrics.height()
                
                transform = animation_effects.get_animation_transform(
                    self.index, i, text_length, elapsed_sec, hold_time, speed,
                    char_x_base, base_y, char_width, char_height,
                    text_width, text_height
                )
                
                color = animation_effects.get_animation_color(self.index, i, text_length, elapsed_sec)
                
                painter.save()
                painter.setPen(QPen(color))
                
                opacity = transform.get('opacity', 1.0)
                painter.setOpacity(opacity)
                
                char_x = transform.get('x', char_x_base)
                char_y = transform.get('y', base_y)
                scale_x = transform.get('scale_x', 1.0)
                scale_y = transform.get('scale_y', 1.0)
                rotation = transform.get('rotation', 0.0)
                
                pivot_x = transform.get('pivot_x', char_x + char_width / 2)
                pivot_y = transform.get('pivot_y', char_y)
                
                transform_matrix = QTransform()
                transform_matrix.translate(pivot_x, pivot_y)
                transform_matrix.rotate(math.degrees(rotation))
                transform_matrix.scale(scale_x, scale_y)
                transform_matrix.translate(-pivot_x, -pivot_y)
                
                dx = char_x - char_x_base
                dy = char_y - base_y
                transform_matrix.translate(dx, dy)
                
                painter.setTransform(transform_matrix)
                painter.drawText(int(char_x_base), int(base_y), char)
                painter.restore()


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
                selection-background-color: #4A90E2;
                selection-color: #FFFFFF;
            }
            QTextEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #000000;
                color: #FFFFFF;
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
        animation_style_group.setMinimumWidth(600)
        animation_style_layout = QVBoxLayout(animation_style_group)
        animation_style_layout.setContentsMargins(10, 16, 10, 10)
        animation_style_layout.setSpacing(8)
        
        # Header section with numeric inputs
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Hold time input (6.00)
        self.animation_holdtime_spin = QDoubleSpinBox()
        self.animation_holdtime_spin.setRange(0.0, 100.0)
        self.animation_holdtime_spin.setValue(6.0)
        self.animation_holdtime_spin.setDecimals(2)
        self.animation_holdtime_spin.setSingleStep(0.1)
        self.animation_holdtime_spin.setSuffix(" sec")
        self.animation_holdtime_spin.valueChanged.connect(self._on_animation_holdtime_changed)
        header_layout.addWidget(self.animation_holdtime_spin)
        
        # Animation speed combo (5)
        self.animation_speed_combo = QComboBox()
        self.animation_speed_combo.addItem("1 fast")
        self.animation_speed_combo.addItems([f"{i}" for i in range(2, 9)])
        self.animation_speed_combo.addItem("9 slow")
        self.animation_speed_combo.setCurrentText("5")
        self.animation_speed_combo.setMinimumWidth(80)
        self.animation_speed_combo.currentTextChanged.connect(self._on_animation_speed_changed)
        header_layout.addWidget(self.animation_speed_combo)
        
        animation_style_layout.addLayout(header_layout)
        
        # Thumbnail grid with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
        """)
        
        grid_widget = QWidget()
        self.thumbnail_grid_layout = QGridLayout(grid_widget)
        self.thumbnail_grid_layout.setContentsMargins(10, 10, 10, 10)
        self.thumbnail_grid_layout.setSpacing(8)
        
        self.animation_thumbnails = []
        self.selected_thumbnail_index = 0
        
        for i in range(34):
            row = i // 4
            col = i % 4
            thumbnail = AnimationStyleThumbnail(i, self)
            thumbnail.selected.connect(self._on_thumbnail_selected)
            self.animation_thumbnails.append(thumbnail)
            self.thumbnail_grid_layout.addWidget(thumbnail, row, col)
        
        # Set first thumbnail as selected
        if self.animation_thumbnails:
            self.animation_thumbnails[0].set_selected(True)
        
        scroll_area.setWidget(grid_widget)
        animation_style_layout.addWidget(scroll_area)
        
        main_layout.addWidget(animation_style_group)
        main_layout.addStretch()
        
        # Connect signals
        self.animation_coords_x.textChanged.connect(self._on_coords_changed)
        self.animation_coords_y.textChanged.connect(self._on_coords_changed)
        self.animation_dims_width.textChanged.connect(self._on_dims_changed)
        self.animation_dims_height.textChanged.connect(self._on_dims_changed)
    
    def _on_animation_holdtime_changed(self, value: float):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation_style" not in self.current_element["properties"]:
            self.current_element["properties"]["animation_style"] = {}
        self.current_element["properties"]["animation_style"]["hold_time"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("animation_hold_time", value)
        self._trigger_autosave()
    
    def _on_animation_speed_changed(self, speed_text: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "animation_style" not in self.current_element["properties"]:
            self.current_element["properties"]["animation_style"] = {}
        
        # Parse speed value from combo text
        speed = 5  # default
        if speed_text == "1 fast":
            speed = 1
        elif speed_text == "9 slow":
            speed = 9
        else:
            try:
                speed = int(speed_text)
            except ValueError:
                speed = 5
        
        self.current_element["properties"]["animation_style"]["speed"] = speed
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("animation_speed", speed)
        self._trigger_autosave()
    
    def _on_thumbnail_selected(self, index: int):
        if not self.current_element or not self.current_program:
            return
        
        # Deselect previous thumbnail
        if 0 <= self.selected_thumbnail_index < len(self.animation_thumbnails):
            self.animation_thumbnails[self.selected_thumbnail_index].set_selected(False)
        
        # Select new thumbnail
        self.selected_thumbnail_index = index
        if 0 <= index < len(self.animation_thumbnails):
            self.animation_thumbnails[index].set_selected(True)
            
            # Update element properties
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "animation_style" not in self.current_element["properties"]:
                self.current_element["properties"]["animation_style"] = {}
            
            self.current_element["properties"]["animation_style"]["style_index"] = index
            
            if index < 13:
                writing_direction = "Horizontal Line Writing"
            else:
                writing_direction = "Vertical Line Writing"
            
            if index < 9 or (index >= 18 and index < 22):
                character_movement = True
            else:
                character_movement = False
            
            self.current_element["properties"]["animation_style"]["writing_direction"] = writing_direction
            self.current_element["properties"]["animation_style"]["character_movement"] = character_movement
            
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("animation_style_index", index)
            self.property_changed.emit("animation_writing_direction", writing_direction)
            self.property_changed.emit("animation_character_movement", character_movement)
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
        style_index = animation_style.get("style_index", 0)
        if hasattr(self, 'animation_thumbnails') and 0 <= style_index < len(self.animation_thumbnails):
            # Update selection without triggering property change (already loading)
            if 0 <= self.selected_thumbnail_index < len(self.animation_thumbnails):
                self.animation_thumbnails[self.selected_thumbnail_index].set_selected(False)
            self.selected_thumbnail_index = style_index
            self.animation_thumbnails[style_index].set_selected(True)
        
        hold_time = animation_style.get("hold_time", 6.0)
        if hasattr(self, 'animation_holdtime_spin'):
            self.animation_holdtime_spin.blockSignals(True)
            self.animation_holdtime_spin.setValue(hold_time)
            self.animation_holdtime_spin.blockSignals(False)
        
        speed = animation_style.get("speed", 5)
        if hasattr(self, 'animation_speed_combo'):
            self.animation_speed_combo.blockSignals(True)
            # Convert speed value to combo text
            if speed == 1:
                self.animation_speed_combo.setCurrentText("1 fast")
            elif speed == 9:
                self.animation_speed_combo.setCurrentText("9 slow")
            else:
                self.animation_speed_combo.setCurrentText(str(speed))
            self.animation_speed_combo.blockSignals(False)
    
    def save_all_animation_text_properties(self):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        
        element_props = self.current_element["properties"]
        
        try:
            x = int(self.animation_coords_x.text() or "0")
            y = int(self.animation_coords_y.text() or "0")
            element_props["x"] = x
            element_props["y"] = y
            self.current_element["x"] = x
            self.current_element["y"] = y
        except ValueError:
            pass
        
        try:
            width = int(self.animation_dims_width.text() or "640")
            height = int(self.animation_dims_height.text() or "480")
            element_props["width"] = width
            element_props["height"] = height
            self.current_element["width"] = width
            self.current_element["height"] = height
        except ValueError:
            pass
        
        if "text" not in element_props:
            element_props["text"] = {}
        
        text_content = self.animation_text_content_edit.toPlainText()
        element_props["text"]["content"] = text_content
        
        if hasattr(self, 'animation_text_editor_toolbar') and self.animation_text_editor_toolbar:
            toolbar = self.animation_text_editor_toolbar
            alignment_str = "left"
            if toolbar._horizontal_alignment == Qt.AlignHCenter:
                alignment_str = "center"
            elif toolbar._horizontal_alignment == Qt.AlignRight:
                alignment_str = "right"
            
            vertical_alignment_str = "top"
            if toolbar._vertical_alignment == Qt.AlignVCenter:
                vertical_alignment_str = "middle"
            elif toolbar._vertical_alignment == Qt.AlignBottom:
                vertical_alignment_str = "bottom"
            
            if "format" not in element_props["text"]:
                element_props["text"]["format"] = {}
            
            format_dict = element_props["text"]["format"]
            format_dict["font_family"] = toolbar.font_family_combo.currentText()
            format_dict["font_size"] = toolbar.font_size_spin.value()
            format_dict["bold"] = toolbar.bold_btn.isChecked()
            format_dict["italic"] = toolbar.italic_btn.isChecked()
            format_dict["underline"] = toolbar.underline_btn.isChecked()
            format_dict["font_color"] = toolbar.font_color.name() if toolbar.font_color else None
            format_dict["text_bg_color"] = toolbar.text_bg_color.name() if toolbar.text_bg_color else None
            format_dict["outline"] = toolbar.outline_btn.isChecked()
            format_dict["alignment"] = alignment_str
            format_dict["vertical_alignment"] = vertical_alignment_str
        
        if "animation_style" not in element_props:
            element_props["animation_style"] = {}
        
        animation_style = element_props["animation_style"]
        animation_style["style_index"] = self.selected_thumbnail_index if hasattr(self, 'selected_thumbnail_index') else 0
        
        if hasattr(self, 'animation_holdtime_spin'):
            animation_style["hold_time"] = self.animation_holdtime_spin.value()
        
        if hasattr(self, 'animation_speed_combo'):
            speed_text = self.animation_speed_combo.currentText()
            speed = 5
            if speed_text == "1 fast":
                speed = 1
            elif speed_text == "9 slow":
                speed = 9
            else:
                try:
                    speed = int(speed_text)
                except ValueError:
                    speed = 5
            animation_style["speed"] = speed
        
        style_index = animation_style.get("style_index", 0)
        if style_index < 13:
            animation_style["writing_direction"] = "Horizontal Line Writing"
        else:
            animation_style["writing_direction"] = "Vertical Line Writing"
        
        if style_index < 9 or (style_index >= 18 and style_index < 22):
            animation_style["character_movement"] = True
        else:
            animation_style["character_movement"] = False
        
        self.current_program.modified = datetime.now().isoformat()
    
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
        font_size_val = text_format.get("font_size")
        if font_size_val is not None:
            font.setPointSize(int(font_size_val))
        if text_format.get("bold"):
            font.setBold(True)
        if text_format.get("italic"):
            font.setItalic(True)
        if text_format.get("underline"):
            font.setUnderline(True)
        char_format.setFont(font)
        
        if text_format.get("font_color"):
            char_format.setForeground(QColor(text_format.get("font_color")))
        else:
            char_format.setForeground(QColor("#FFFFFF"))
        
        text_bg_color_str = text_format.get("text_bg_color")
        if text_bg_color_str:
            text_bg_color = QColor(text_bg_color_str)
            char_format.setBackground(QBrush(text_bg_color))
        else:
            char_format.setBackground(QBrush())
            char_format.clearBackground()
        
        outline = text_format.get("outline", False)
        if outline:
            pen = QPen(QColor(Qt.black))
            pen.setStyle(Qt.SolidLine)
            pen.setWidth(1)
            char_format.setTextOutline(pen)
        else:
            pen = QPen(Qt.NoPen)
            char_format.setTextOutline(pen)
        
        horizontal_align = Qt.AlignLeft
        vertical_align = Qt.AlignTop
        
        if text_format.get("alignment"):
            alignment_str = text_format["alignment"]
            if alignment_str == "center":
                horizontal_align = Qt.AlignHCenter
            elif alignment_str == "right":
                horizontal_align = Qt.AlignRight
        
        if text_format.get("vertical_alignment"):
            vertical_str = text_format["vertical_alignment"]
            if vertical_str == "middle":
                vertical_align = Qt.AlignVCenter
            elif vertical_str == "bottom":
                vertical_align = Qt.AlignBottom
        
        from PyQt5.QtGui import QTextBlockFormat
        block_format = QTextBlockFormat()
        block_format.setAlignment(horizontal_align)
        cursor.setBlockFormat(block_format)
        
        cursor.setCharFormat(char_format)
        cursor.clearSelection()
        self.animation_text_content_edit.setTextCursor(cursor)
        
        if hasattr(self, 'animation_text_editor_toolbar') and self.animation_text_editor_toolbar:
            toolbar = self.animation_text_editor_toolbar
            toolbar._horizontal_alignment = horizontal_align
            toolbar._vertical_alignment = vertical_align
            toolbar.align_left_btn.blockSignals(True)
            toolbar.align_center_btn.blockSignals(True)
            toolbar.align_right_btn.blockSignals(True)
            toolbar.align_left_btn.setChecked(horizontal_align == Qt.AlignLeft)
            toolbar.align_center_btn.setChecked(horizontal_align == Qt.AlignHCenter)
            toolbar.align_right_btn.setChecked(horizontal_align == Qt.AlignRight)
            toolbar.align_left_btn.blockSignals(False)
            toolbar.align_center_btn.blockSignals(False)
            toolbar.align_right_btn.blockSignals(False)
            toolbar.align_top_btn.blockSignals(True)
            toolbar.align_middle_btn.blockSignals(True)
            toolbar.align_bottom_btn.blockSignals(True)
            toolbar.align_top_btn.setChecked(vertical_align == Qt.AlignTop)
            toolbar.align_middle_btn.setChecked(vertical_align == Qt.AlignVCenter)
            toolbar.align_bottom_btn.setChecked(vertical_align == Qt.AlignBottom)
            toolbar.align_top_btn.blockSignals(False)
            toolbar.align_middle_btn.blockSignals(False)
            toolbar.align_bottom_btn.blockSignals(False)
