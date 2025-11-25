from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox, QRadioButton,
                             QButtonGroup, QDateTimeEdit, QTimeEdit, QSpinBox, QColorDialog)
from PyQt5.QtCore import Qt, QDateTime, QTime
from PyQt5.QtGui import QColor
from typing import Optional, Dict
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent


class TimingPropertiesComponent(BasePropertiesComponent):
    
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
            QRadioButton {
                font-size: 12px;
            }
            QDateTimeEdit, QTimeEdit {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
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
        self.timing_coords_x = QLineEdit()
        self.timing_coords_x.setPlaceholderText("0")
        self.timing_coords_x.setMinimumWidth(70)
        self.timing_coords_x.setText("0")
        coords_comma = QLabel(",")
        coords_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.timing_coords_y = QLineEdit()
        self.timing_coords_y.setPlaceholderText("0")
        self.timing_coords_y.setMinimumWidth(70)
        self.timing_coords_y.setText("0")
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.timing_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.timing_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_row.setSpacing(6)
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.timing_dims_width = QLineEdit()
        self.timing_dims_width.setPlaceholderText("1920")
        self.timing_dims_width.setMinimumWidth(70)
        self.timing_dims_width.setText("1920")
        dims_comma = QLabel(",")
        dims_comma.setStyleSheet("color: #666666; font-weight: bold;")
        self.timing_dims_height = QLineEdit()
        self.timing_dims_height.setPlaceholderText("1080")
        self.timing_dims_height.setMinimumWidth(70)
        self.timing_dims_height.setText("1080")
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.timing_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.timing_dims_height)
        area_layout.addLayout(dims_row)
        
        frame_group_layout = QVBoxLayout()
        frame_group_layout.setSpacing(4)
        
        area_layout.addLayout(frame_group_layout)
        area_layout.addStretch()
        main_layout.addWidget(area_group)
        
        # No title group (grouped in QGroupBox)
        no_title_group = QGroupBox()
        no_title_group.setMaximumWidth(600)
        no_title_layout = QVBoxLayout(no_title_group)
        no_title_layout.setContentsMargins(10, 16, 10, 10)
        no_title_layout.setSpacing(12)
        
        # Radio button group (without group border)
        radio_group_layout = QHBoxLayout()
        radio_group_layout.setSpacing(12)
        self.timing_mode_group = QButtonGroup(self)
        
        self.suitable_time_radio = QRadioButton("Suitable time")
        self.suitable_time_radio.setChecked(True)
        self.timing_mode_group.addButton(self.suitable_time_radio, 0)
        self.suitable_time_radio.toggled.connect(self._on_mode_changed)
        radio_group_layout.addWidget(self.suitable_time_radio)
        
        self.count_down_radio = QRadioButton("Count down")
        self.timing_mode_group.addButton(self.count_down_radio, 1)
        self.count_down_radio.toggled.connect(self._on_mode_changed)
        radio_group_layout.addWidget(self.count_down_radio)
        
        self.fixed_time_radio = QRadioButton("Fixed time")
        self.timing_mode_group.addButton(self.fixed_time_radio, 2)
        self.fixed_time_radio.toggled.connect(self._on_mode_changed)
        radio_group_layout.addWidget(self.fixed_time_radio)
        
        radio_group_layout.addStretch()
        no_title_layout.addLayout(radio_group_layout)
        
        # Setting value according to radio button
        self.settings_widget = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_widget)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(8)
        
        # Suitable time settings
        self.suitable_time_widget = QWidget()
        suitable_time_layout = QHBoxLayout(self.suitable_time_widget)
        suitable_time_layout.setContentsMargins(0, 0, 0, 0)
        suitable_time_layout.setSpacing(8)
        suitable_time_layout.addWidget(QLabel("DateTime:"))
        self.suitable_time_datetime = QDateTimeEdit()
        self.suitable_time_datetime.setCalendarPopup(True)
        self.suitable_time_datetime.setDateTime(QDateTime.currentDateTime())
        self.suitable_time_datetime.dateTimeChanged.connect(self._on_suitable_time_changed)
        suitable_time_layout.addWidget(self.suitable_time_datetime, stretch=1)
        suitable_time_layout.addWidget(QLabel("Color:"))
        self.suitable_time_color_btn = QPushButton("")
        self.suitable_time_color_btn.clicked.connect(self._on_suitable_time_color_clicked)
        suitable_time_layout.addWidget(self.suitable_time_color_btn)
        self.settings_layout.addWidget(self.suitable_time_widget)
        
        # Count down settings
        self.count_down_widget = QWidget()
        count_down_layout = QHBoxLayout(self.count_down_widget)
        count_down_layout.setContentsMargins(0, 0, 0, 0)
        count_down_layout.setSpacing(8)
        count_down_layout.addWidget(QLabel("DateTime:"))
        self.count_down_datetime = QDateTimeEdit()
        self.count_down_datetime.setCalendarPopup(True)
        self.count_down_datetime.setDateTime(QDateTime.currentDateTime())
        self.count_down_datetime.dateTimeChanged.connect(self._on_count_down_changed)
        count_down_layout.addWidget(self.count_down_datetime, stretch=1)
        count_down_layout.addWidget(QLabel("Color:"))
        self.count_down_color_btn = QPushButton("")
        self.count_down_color_btn.clicked.connect(self._on_count_down_color_clicked)
        count_down_layout.addWidget(self.count_down_color_btn)
        self.settings_layout.addWidget(self.count_down_widget)
        self.count_down_widget.setVisible(False)
        
        # Fixed time settings
        self.fixed_time_widget = QWidget()
        fixed_time_layout = QVBoxLayout(self.fixed_time_widget)
        fixed_time_layout.setContentsMargins(0, 0, 0, 0)
        fixed_time_layout.setSpacing(8)
        
        day_period_row = QHBoxLayout()
        day_period_row.setSpacing(8)
        day_period_row.addWidget(QLabel("Day Period:"))
        self.fixed_time_day_period = QSpinBox()
        self.fixed_time_day_period.setRange(0, 365)
        self.fixed_time_day_period.setValue(0)
        self.fixed_time_day_period.setSuffix(" days")
        self.fixed_time_day_period.valueChanged.connect(self._on_fixed_time_day_period_changed)
        day_period_row.addWidget(self.fixed_time_day_period, stretch=1)
        fixed_time_layout.addLayout(day_period_row)
        
        time_row = QHBoxLayout()
        time_row.setSpacing(8)
        time_row.addWidget(QLabel("Time:"))
        self.fixed_time_time = QTimeEdit()
        self.fixed_time_time.setTime(QTime.currentTime())
        self.fixed_time_time.timeChanged.connect(self._on_fixed_time_time_changed)
        time_row.addWidget(self.fixed_time_time, stretch=1)
        fixed_time_layout.addLayout(time_row)
        
        self.settings_layout.addWidget(self.fixed_time_widget)
        self.fixed_time_widget.setVisible(False)
        
        no_title_layout.addWidget(self.settings_widget)
        
        # Top Text
        top_text_layout = QHBoxLayout()
        top_text_layout.setSpacing(8)
        top_text_layout.addWidget(QLabel("Top Text:"))
        self.top_text_input = QLineEdit()
        self.top_text_input.setPlaceholderText("Enter top text")
        self.top_text_input.setText("To **")
        self.top_text_input.textChanged.connect(self._on_top_text_changed)
        top_text_layout.addWidget(self.top_text_input, stretch=1)
        top_text_layout.addWidget(QLabel("Color:"))
        self.top_text_color_btn = QPushButton("")
        self.top_text_color_btn.clicked.connect(self._on_top_text_color_clicked)
        top_text_layout.addWidget(self.top_text_color_btn)
        
        multiline_combo = QComboBox()
        multiline_combo.addItems(["Multiline", "Singleline"])
        multiline_combo.setCurrentText("Multiline")
        multiline_combo.currentTextChanged.connect(self._on_multiline_changed)
        top_text_layout.addWidget(multiline_combo)
        self.multiline_combo = multiline_combo
        
        # Space setting
        top_text_layout.addWidget(QLabel("Space:"))
        self.top_text_space = QSpinBox()
        self.top_text_space.setRange(0, 100)
        self.top_text_space.setValue(5)
        self.top_text_space.setSuffix(" px")
        self.top_text_space.valueChanged.connect(self._on_top_text_space_changed)
        top_text_layout.addWidget(self.top_text_space)
        
        no_title_layout.addLayout(top_text_layout)
        
        # Display style
        display_style_label = QLabel("Display style:")
        display_style_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        no_title_layout.addWidget(display_style_label)
        
        # Enable/disable checkboxes
        checkboxes_layout = QHBoxLayout()
        checkboxes_layout.setSpacing(12)
        
        self.year_check = QCheckBox("Year")
        self.year_check.setChecked(True)
        self.year_check.toggled.connect(self._on_display_unit_changed)
        checkboxes_layout.addWidget(self.year_check)
        
        self.day_check = QCheckBox("Day")
        self.day_check.setChecked(True)
        self.day_check.toggled.connect(self._on_display_unit_changed)
        checkboxes_layout.addWidget(self.day_check)
        
        self.hour_check = QCheckBox("Hour")
        self.hour_check.setChecked(True)
        self.hour_check.toggled.connect(self._on_display_unit_changed)
        checkboxes_layout.addWidget(self.hour_check)
        
        self.minute_check = QCheckBox("Minute")
        self.minute_check.setChecked(True)
        self.minute_check.toggled.connect(self._on_display_unit_changed)
        checkboxes_layout.addWidget(self.minute_check)
        
        self.second_check = QCheckBox("Second")
        self.second_check.setChecked(True)
        self.second_check.toggled.connect(self._on_display_unit_changed)
        checkboxes_layout.addWidget(self.second_check)
        
        self.millisecond_check = QCheckBox("Millisecond")
        self.millisecond_check.setChecked(False)
        self.millisecond_check.toggled.connect(self._on_display_unit_changed)
        checkboxes_layout.addWidget(self.millisecond_check)
        
        checkboxes_layout.addStretch()
        no_title_layout.addLayout(checkboxes_layout)
        
        # Display font color and position align
        display_settings_layout = QHBoxLayout()
        display_settings_layout.setSpacing(8)
        display_settings_layout.addWidget(QLabel("Display Color:"))
        self.display_color_btn = QPushButton("")
        self.display_color_btn.clicked.connect(self._on_display_color_clicked)
        display_settings_layout.addWidget(self.display_color_btn)
        
        display_settings_layout.addStretch()
        display_settings_layout.addWidget(QLabel("Position Align:"))
        self.position_align_combo = QComboBox()
        self.position_align_combo.addItems(["Center", "Top", "Bottom"])
        self.position_align_combo.setCurrentText("Center")
        self.position_align_combo.currentTextChanged.connect(self._on_position_align_changed)
        display_settings_layout.addWidget(self.position_align_combo)
        
        no_title_layout.addLayout(display_settings_layout)
        no_title_layout.addStretch()
        
        main_layout.addWidget(no_title_group, stretch=1)
        main_layout.addStretch()
        
        # Connect signals
        self.timing_coords_x.textChanged.connect(self._on_coords_changed)
        self.timing_coords_y.textChanged.connect(self._on_coords_changed)
        self.timing_dims_width.textChanged.connect(self._on_dims_changed)
        self.timing_dims_height.textChanged.connect(self._on_dims_changed)
    
    def _on_mode_changed(self):
        """Handle radio button mode change"""
        if self.suitable_time_radio.isChecked():
            self.suitable_time_widget.setVisible(True)
            self.count_down_widget.setVisible(False)
            self.fixed_time_widget.setVisible(False)
            mode = "suitable_time"
        elif self.count_down_radio.isChecked():
            self.suitable_time_widget.setVisible(False)
            self.count_down_widget.setVisible(True)
            self.fixed_time_widget.setVisible(False)
            mode = "count_down"
        else:  # fixed_time
            self.suitable_time_widget.setVisible(False)
            self.count_down_widget.setVisible(False)
            self.fixed_time_widget.setVisible(True)
            mode = "fixed_time"
        
        if self.current_element and self.current_program:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            self.current_element["properties"]["timing"]["mode"] = mode
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("timing_mode", mode)
            self._trigger_autosave()
    
    def _on_suitable_time_changed(self, dt: QDateTime):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        if "suitable_time" not in self.current_element["properties"]["timing"]:
            self.current_element["properties"]["timing"]["suitable_time"] = {}
        self.current_element["properties"]["timing"]["suitable_time"]["datetime"] = dt.toString(Qt.ISODate)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_suitable_time", dt.toString(Qt.ISODate))
        self._trigger_autosave()
    
    def _on_suitable_time_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            if "suitable_time" not in self.current_element["properties"]["timing"]:
                self.current_element["properties"]["timing"]["suitable_time"] = {}
            self.current_element["properties"]["timing"]["suitable_time"]["color"] = color.name()
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("timing_suitable_time_color", color.name())
            self._trigger_autosave()
            self.suitable_time_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_count_down_changed(self, dt: QDateTime):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        if "count_down" not in self.current_element["properties"]["timing"]:
            self.current_element["properties"]["timing"]["count_down"] = {}
        self.current_element["properties"]["timing"]["count_down"]["datetime"] = dt.toString(Qt.ISODate)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_count_down", dt.toString(Qt.ISODate))
        self._trigger_autosave()
    
    def _on_count_down_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            if "count_down" not in self.current_element["properties"]["timing"]:
                self.current_element["properties"]["timing"]["count_down"] = {}
            self.current_element["properties"]["timing"]["count_down"]["color"] = color.name()
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("timing_count_down_color", color.name())
            self._trigger_autosave()
            self.count_down_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_fixed_time_day_period_changed(self, days: int):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        if "fixed_time" not in self.current_element["properties"]["timing"]:
            self.current_element["properties"]["timing"]["fixed_time"] = {}
        self.current_element["properties"]["timing"]["fixed_time"]["day_period"] = days
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_fixed_time_day_period", days)
        self._trigger_autosave()
    
    def _on_fixed_time_time_changed(self, time: QTime):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        if "fixed_time" not in self.current_element["properties"]["timing"]:
            self.current_element["properties"]["timing"]["fixed_time"] = {}
        self.current_element["properties"]["timing"]["fixed_time"]["time"] = time.toString(Qt.ISODate)
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_fixed_time_time", time.toString(Qt.ISODate))
        self._trigger_autosave()
    
    def _on_top_text_changed(self, text: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        self.current_element["properties"]["timing"]["top_text"] = text
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_top_text", text)
        self._trigger_autosave()
    
    def _on_top_text_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            self.current_element["properties"]["timing"]["top_text_color"] = color.name()
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("timing_top_text_color", color.name())
            self._trigger_autosave()
            self.top_text_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_multiline_changed(self, text: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        multiline = text == "Multiline"
        self.current_element["properties"]["timing"]["multiline"] = multiline
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_multiline", multiline)
        self._trigger_autosave()
    
    def _on_top_text_space_changed(self, space: int):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        self.current_element["properties"]["timing"]["top_text_space"] = space
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_top_text_space", space)
        self._trigger_autosave()
    
    def _on_display_unit_changed(self):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        if "display_style" not in self.current_element["properties"]["timing"]:
            self.current_element["properties"]["timing"]["display_style"] = {}
        
        display_style = self.current_element["properties"]["timing"]["display_style"]
        display_style["year"] = self.year_check.isChecked()
        display_style["day"] = self.day_check.isChecked()
        display_style["hour"] = self.hour_check.isChecked()
        display_style["minute"] = self.minute_check.isChecked()
        display_style["second"] = self.second_check.isChecked()
        display_style["millisecond"] = self.millisecond_check.isChecked()
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_display_units", display_style)
        self._trigger_autosave()
    
    def _on_display_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            if "display_style" not in self.current_element["properties"]["timing"]:
                self.current_element["properties"]["timing"]["display_style"] = {}
            self.current_element["properties"]["timing"]["display_style"]["color"] = color.name()
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("timing_display_color", color.name())
            self._trigger_autosave()
            self.display_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_position_align_changed(self, align: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "timing" not in self.current_element["properties"]:
            self.current_element["properties"]["timing"] = {}
        if "display_style" not in self.current_element["properties"]["timing"]:
            self.current_element["properties"]["timing"]["display_style"] = {}
        self.current_element["properties"]["timing"]["display_style"]["position_align"] = align.lower()
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("timing_position_align", align.lower())
        self._trigger_autosave()
    
    def _on_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            x = int(self.timing_coords_x.text() or "0")
            y = int(self.timing_coords_y.text() or "0")
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
            self.property_changed.emit("timing_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            width = int(self.timing_dims_width.text() or "640")
            height = int(self.timing_dims_height.text() or "480")
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
            self.property_changed.emit("timing_size", (width, height))
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
        self.timing_coords_x.blockSignals(True)
        self.timing_coords_y.blockSignals(True)
        self.timing_coords_x.setText(str(x))
        self.timing_coords_y.setText(str(y))
        self.timing_coords_x.blockSignals(False)
        self.timing_coords_y.blockSignals(False)
        
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        if not width or width <= 0:
            width = default_width
        if not height or height <= 0:
            height = default_height
        
        self.timing_dims_width.blockSignals(True)
        self.timing_dims_height.blockSignals(True)
        self.timing_dims_width.setText(str(width))
        self.timing_dims_height.setText(str(height))
        self.timing_dims_width.blockSignals(False)
        self.timing_dims_height.blockSignals(False)
        
        # Load timing properties
        timing_props = element_props.get("timing", {})
        
        # Load mode
        mode = timing_props.get("mode", "suitable_time")
        if mode == "suitable_time":
            self.suitable_time_radio.setChecked(True)
        elif mode == "count_down":
            self.count_down_radio.setChecked(True)
        else:
            self.fixed_time_radio.setChecked(True)
        
        # Load suitable time
        suitable_time = timing_props.get("suitable_time", {})
        if "datetime" in suitable_time:
            dt = QDateTime.fromString(suitable_time["datetime"], Qt.ISODate)
            if dt.isValid():
                self.suitable_time_datetime.blockSignals(True)
                self.suitable_time_datetime.setDateTime(dt)
                self.suitable_time_datetime.blockSignals(False)
        suitable_time_color = suitable_time.get("color", "#cdcd00")
        if "color" not in suitable_time:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            if "suitable_time" not in self.current_element["properties"]["timing"]:
                self.current_element["properties"]["timing"]["suitable_time"] = {}
            self.current_element["properties"]["timing"]["suitable_time"]["color"] = suitable_time_color
        self.suitable_time_color_btn.setStyleSheet(f"background-color: {suitable_time_color};")
        
        # Load count down
        count_down = timing_props.get("count_down", {})
        if "datetime" in count_down:
            dt = QDateTime.fromString(count_down["datetime"], Qt.ISODate)
            if dt.isValid():
                self.count_down_datetime.blockSignals(True)
                self.count_down_datetime.setDateTime(dt)
                self.count_down_datetime.blockSignals(False)
        count_down_color = count_down.get("color", "#cdcd00")
        if "color" not in count_down:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            if "count_down" not in self.current_element["properties"]["timing"]:
                self.current_element["properties"]["timing"]["count_down"] = {}
            self.current_element["properties"]["timing"]["count_down"]["color"] = count_down_color
        self.count_down_color_btn.setStyleSheet(f"background-color: {count_down_color};")
        
        # Load fixed time
        fixed_time = timing_props.get("fixed_time", {})
        if "day_period" in fixed_time:
            self.fixed_time_day_period.blockSignals(True)
            self.fixed_time_day_period.setValue(fixed_time["day_period"])
            self.fixed_time_day_period.blockSignals(False)
        if "time" in fixed_time:
            time = QTime.fromString(fixed_time["time"], Qt.ISODate)
            if time.isValid():
                self.fixed_time_time.blockSignals(True)
                self.fixed_time_time.setTime(time)
                self.fixed_time_time.blockSignals(False)
        
        top_text = timing_props.get("top_text", "To **")
        if "top_text" not in timing_props:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            self.current_element["properties"]["timing"]["top_text"] = top_text
        self.top_text_input.blockSignals(True)
        self.top_text_input.setText(top_text)
        self.top_text_input.blockSignals(False)
        
        top_text_color = timing_props.get("top_text_color", "#cdcd00")
        if "top_text_color" not in timing_props:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            self.current_element["properties"]["timing"]["top_text_color"] = top_text_color
            self.top_text_color_btn.setStyleSheet(f"background-color: {top_text_color};")
        
        multiline = timing_props.get("multiline", True)
        if hasattr(self, 'multiline_combo'):
            self.multiline_combo.blockSignals(True)
            self.multiline_combo.setCurrentText("Multiline" if multiline else "Singleline")
            self.multiline_combo.blockSignals(False)
        
        top_text_space = timing_props.get("top_text_space", 5)
        self.top_text_space.blockSignals(True)
        self.top_text_space.setValue(top_text_space)
        self.top_text_space.blockSignals(False)
        
        # Load display style
        display_style = timing_props.get("display_style", {})
        self.year_check.blockSignals(True)
        self.year_check.setChecked(display_style.get("year", True))
        self.year_check.blockSignals(False)
        
        self.day_check.blockSignals(True)
        self.day_check.setChecked(display_style.get("day", True))
        self.day_check.blockSignals(False)
        
        self.hour_check.blockSignals(True)
        self.hour_check.setChecked(display_style.get("hour", True))
        self.hour_check.blockSignals(False)
        
        self.minute_check.blockSignals(True)
        self.minute_check.setChecked(display_style.get("minute", True))
        self.minute_check.blockSignals(False)
        
        self.second_check.blockSignals(True)
        self.second_check.setChecked(display_style.get("second", True))
        self.second_check.blockSignals(False)
        
        self.millisecond_check.blockSignals(True)
        self.millisecond_check.setChecked(display_style.get("millisecond", False))
        self.millisecond_check.blockSignals(False)
        
        display_color = display_style.get("color", "#ff9900")
        if "color" not in display_style:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "timing" not in self.current_element["properties"]:
                self.current_element["properties"]["timing"] = {}
            if "display_style" not in self.current_element["properties"]["timing"]:
                self.current_element["properties"]["timing"]["display_style"] = {}
            self.current_element["properties"]["timing"]["display_style"]["color"] = display_color
            self.display_color_btn.setStyleSheet(f"background-color: {display_color};")
        
        position_align = display_style.get("position_align", "center")
        position_align_index = self.position_align_combo.findText(position_align.capitalize())
        if position_align_index >= 0:
            self.position_align_combo.setCurrentIndex(position_align_index)
        else:
            self.position_align_combo.setCurrentIndex(0)
