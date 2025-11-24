from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QGroupBox, QLineEdit, QCheckBox, QSpinBox,
                             QFileDialog, QColorDialog, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
from ui.properties.base_properties_component import BasePropertiesComponent


class ClockPropertiesComponent(BasePropertiesComponent):
    
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
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #000000;
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #000000;
                color: #FFFFFF;
            }
            QSpinBox, QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #FFFFFF;
                font-size: 12px;
            }
            QSpinBox:focus, QComboBox:focus {
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
        """)
        
        # Area attribute group (same as photo)
        area_group = QGroupBox("Area attribute")
        area_group.setMaximumWidth(200)
        area_layout = QVBoxLayout(area_group)
        area_layout.setContentsMargins(10, 16, 10, 10)
        area_layout.setSpacing(8)
        
        coords_row = QHBoxLayout()
        coords_label = QLabel("📍")
        coords_label.setStyleSheet("font-size: 16px;")
        self.clock_coords_x = QLineEdit()
        self.clock_coords_x.setPlaceholderText("0")
        self.clock_coords_x.setMinimumWidth(70)
        coords_comma = QLabel(",")
        self.clock_coords_y = QLineEdit()
        self.clock_coords_y.setPlaceholderText("0")
        self.clock_coords_y.setMinimumWidth(70)
        coords_row.addWidget(coords_label)
        coords_row.addWidget(self.clock_coords_x)
        coords_row.addWidget(coords_comma)
        coords_row.addWidget(self.clock_coords_y)
        area_layout.addLayout(coords_row)
        
        dims_row = QHBoxLayout()
        dims_label = QLabel("📐")
        dims_label.setStyleSheet("font-size: 16px;")
        self.clock_dims_width = QLineEdit()
        self.clock_dims_width.setPlaceholderText("1920")
        self.clock_dims_width.setMinimumWidth(70)
        dims_comma = QLabel(",")
        self.clock_dims_height = QLineEdit()
        self.clock_dims_height.setPlaceholderText("1080")
        self.clock_dims_height.setMinimumWidth(70)
        dims_row.addWidget(dims_label)
        dims_row.addWidget(self.clock_dims_width)
        dims_row.addWidget(dims_comma)
        dims_row.addWidget(self.clock_dims_height)
        area_layout.addLayout(dims_row)
        
        frame_group_layout = QVBoxLayout()
        
        area_layout.addLayout(frame_group_layout)
        area_layout.addStretch()
        main_layout.addWidget(area_group)
        
        # Clock attribute group
        clock_attr_group = QGroupBox("Clock attribute")
        clock_attr_group.setMinimumWidth(200)
        clock_attr_layout = QVBoxLayout(clock_attr_group)
        clock_attr_layout.setContentsMargins(10, 16, 10, 10)
        clock_attr_layout.setSpacing(8)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Clock Type:"))
        self.clock_type_combo = QComboBox()
        self.clock_type_combo.addItems(["System", "Digital", "Analog"])
        self.clock_type_combo.currentTextChanged.connect(self._on_clock_type_changed)
        type_layout.addWidget(self.clock_type_combo, stretch=1)
        clock_attr_layout.addLayout(type_layout)
        
        timezone_layout = QHBoxLayout()
        timezone_layout.addWidget(QLabel("Time Zone:"))
        self.clock_timezone_combo = QComboBox()
        self.clock_timezone_combo.addItems(["UTC", "Local", "GMT+0", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12", "GMT-1", "GMT-2", "GMT-3", "GMT-4", "GMT-5", "GMT-6", "GMT-7", "GMT-8", "GMT-9", "GMT-10", "GMT-11", "GMT-12"])
        self.clock_timezone_combo.currentTextChanged.connect(self._on_timezone_changed)
        timezone_layout.addWidget(self.clock_timezone_combo, stretch=1)
        clock_attr_layout.addLayout(timezone_layout)
        
        correction_layout = QHBoxLayout()
        correction_layout.addWidget(QLabel("Time Correction:"))
        self.clock_correction_spin = QSpinBox()
        self.clock_correction_spin.setRange(-86400, 86400)
        self.clock_correction_spin.setSuffix(" seconds")
        self.clock_correction_spin.valueChanged.connect(self._on_correction_changed)
        correction_layout.addWidget(self.clock_correction_spin, stretch=1)
        clock_attr_layout.addLayout(correction_layout)
        
        clock_attr_layout.addStretch()
        main_layout.addWidget(clock_attr_group)
        
        # Other group (dynamic based on clock type)
        self.other_group = QGroupBox("Other")
        self.other_group.setMinimumWidth(800)
        self.other_layout = QVBoxLayout(self.other_group)
        self.other_layout.setContentsMargins(10, 16, 10, 10)
        self.other_layout.setSpacing(8)
        self._setup_system_clock_options()
        main_layout.addWidget(self.other_group)
        
        main_layout.addStretch()
        
        # Connect signals
        self.clock_coords_x.textChanged.connect(self._on_coords_changed)
        self.clock_coords_y.textChanged.connect(self._on_coords_changed)
        self.clock_dims_width.textChanged.connect(self._on_dims_changed)
        self.clock_dims_height.textChanged.connect(self._on_dims_changed)
        
    def _setup_system_clock_options(self):
        """Setup UI for System clock type"""
        self._clear_other_group()
        
        form_layout = QHBoxLayout()
        form_layout.setSpacing(8)
        
        vLayout_1 = QVBoxLayout()
        vLayout_1.setSpacing(8)
        vLayout_1.setContentsMargins(4, 4, 4, 4)

        title_layout = QHBoxLayout()
        self.system_title_check = QCheckBox("Title")
        self.system_title_check.toggled.connect(self._on_system_title_enabled_changed)
        title_layout.addWidget(self.system_title_check)
        title_layout.addStretch()
        self.system_title_edit = QLineEdit()
        self.system_title_edit.setPlaceholderText("Enter title text")
        self.system_title_edit.setText("LED")  # Default title "LED"
        self.system_title_edit.textChanged.connect(self._on_system_title_value_changed)
        title_layout.addWidget(self.system_title_edit, stretch=1)
        title_layout.addStretch()
        self.system_title_color_btn = QPushButton("")
        self.system_title_color_btn.setStyleSheet("background-color: #0000FF;")
        self.system_title_color_btn.clicked.connect(self._on_system_title_color_clicked)
        title_layout.addWidget(self.system_title_color_btn)
        vLayout_1.addLayout(title_layout)
        
        font_layout = QHBoxLayout()
        font_layout.setSpacing(8)
        self.system_font_family_combo = QComboBox()
        self.system_font_family_combo.addItems(["Arial", "Times New Roman", "Courier New", "Verdana", "Helvetica"])
        self.system_font_family_combo.currentTextChanged.connect(self._on_system_font_family_changed)
        font_layout.addWidget(self.system_font_family_combo, stretch=1)
        font_layout.addStretch()
        self.system_font_size_spin = QSpinBox()
        self.system_font_size_spin.setRange(8, 200)
        self.system_font_size_spin.setValue(24)
        self.system_font_size_spin.valueChanged.connect(self._on_system_font_size_changed)
        font_layout.addWidget(self.system_font_size_spin, stretch=1)
        vLayout_1.addLayout(font_layout)

        hour_scale_layout = QHBoxLayout()
        hour_scale_layout.setSpacing(8)
        self.system_hour_scale_shape_combo = QComboBox()
        self.system_hour_scale_shape_combo.addItems(["straight line", "round", "rectangle", "all numbers", "digital"])
        self.system_hour_scale_shape_combo.currentTextChanged.connect(self._on_system_hour_scale_shape_changed)
        hour_scale_layout.addWidget(self.system_hour_scale_shape_combo, stretch=1)
        hour_scale_layout.addStretch()
        self.system_hour_scale_color_btn = QPushButton("")
        self.system_hour_scale_color_btn.setStyleSheet("background-color: #FF0000;")
        self.system_hour_scale_color_btn.clicked.connect(self._on_system_hour_scale_color_clicked)
        hour_scale_layout.addWidget(self.system_hour_scale_color_btn, stretch=1)
        vLayout_1.addLayout(hour_scale_layout)
        
        minute_scale_layout = QHBoxLayout()
        minute_scale_layout.setSpacing(8)
        self.system_minute_scale_shape_combo = QComboBox()
        self.system_minute_scale_shape_combo.addItems(["round", "rectangle", "straight line", "air"])
        self.system_minute_scale_shape_combo.currentTextChanged.connect(self._on_system_minute_scale_shape_changed)
        minute_scale_layout.addWidget(self.system_minute_scale_shape_combo, stretch=1)
        minute_scale_layout.addStretch()
        self.system_minute_scale_color_btn = QPushButton("")
        self.system_minute_scale_color_btn.setStyleSheet("background-color: #00FF00;")
        self.system_minute_scale_color_btn.clicked.connect(self._on_system_minute_scale_color_clicked)
        minute_scale_layout.addWidget(self.system_minute_scale_color_btn, stretch=1)
        vLayout_1.addLayout(minute_scale_layout)

        form_layout.addLayout(vLayout_1)
        
        vLayout_2 = QVBoxLayout()
        vLayout_2.setSpacing(8)
        vLayout_2.setContentsMargins(4, 4, 4, 4)
        
        hour_hand_layout = QHBoxLayout()
        hour_hand_layout.setSpacing(8)
        self.system_hour_hand_shape_combo = QComboBox()
        self.system_hour_hand_shape_combo.addItems(["rectangle", "polygon", "air"])
        self.system_hour_hand_shape_combo.currentTextChanged.connect(self._on_system_hour_hand_shape_changed)
        hour_hand_layout.addWidget(self.system_hour_hand_shape_combo, stretch=1)
        hour_hand_layout.addStretch()
        self.system_hour_hand_color_btn = QPushButton("")
        self.system_hour_hand_color_btn.setStyleSheet("background-color: #FF0000;")
        self.system_hour_hand_color_btn.clicked.connect(self._on_system_hour_hand_color_clicked)
        hour_hand_layout.addWidget(self.system_hour_hand_color_btn, stretch=1)
        vLayout_2.addLayout(hour_hand_layout)
        
        minute_hand_layout = QHBoxLayout()
        minute_hand_layout.setSpacing(8)
        self.system_minute_hand_shape_combo = QComboBox()
        self.system_minute_hand_shape_combo.addItems(["rectangle", "polygon", "air"])
        self.system_minute_hand_shape_combo.currentTextChanged.connect(self._on_system_minute_hand_shape_changed)
        minute_hand_layout.addWidget(self.system_minute_hand_shape_combo, stretch=1)
        minute_hand_layout.addStretch()
        self.system_minute_hand_color_btn = QPushButton("")
        self.system_minute_hand_color_btn.setStyleSheet("background-color: #00FF00;")
        self.system_minute_hand_color_btn.clicked.connect(self._on_system_minute_hand_color_clicked)
        minute_hand_layout.addWidget(self.system_minute_hand_color_btn, stretch=1)
        vLayout_2.addLayout(minute_hand_layout)
        
        second_hand_layout = QHBoxLayout()
        second_hand_layout.setSpacing(8)
        self.system_second_hand_shape_combo = QComboBox()
        self.system_second_hand_shape_combo.addItems(["rectangle", "polygon", "air"])
        self.system_second_hand_shape_combo.currentTextChanged.connect(self._on_system_second_hand_shape_changed)
        second_hand_layout.addWidget(self.system_second_hand_shape_combo, stretch=1)
        second_hand_layout.addStretch()
        self.system_second_hand_color_btn = QPushButton("")
        self.system_second_hand_color_btn.setStyleSheet("background-color: #0000FF;")
        self.system_second_hand_color_btn.clicked.connect(self._on_system_second_hand_color_clicked)
        second_hand_layout.addWidget(self.system_second_hand_color_btn, stretch=1)
        vLayout_2.addLayout(second_hand_layout)

        form_layout.addLayout(vLayout_2)
        
        vLayout_3 = QVBoxLayout()
        vLayout_3.setSpacing(8)
        vLayout_3.setContentsMargins(4, 4, 4, 4)
        
        date_layout = QHBoxLayout()
        date_layout.setSpacing(8)
        self.system_date_check = QCheckBox("Date")
        self.system_date_check.setChecked(True)  # Default enabled
        self.system_date_check.toggled.connect(self._on_system_date_enabled_changed)
        date_layout.addWidget(self.system_date_check)
        date_layout.addStretch()
        self.system_date_format_combo = QComboBox()
        self.system_date_format_combo.addItems(["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY", "YYYY/MM/DD"])
        self.system_date_format_combo.currentTextChanged.connect(self._on_system_date_format_changed)
        date_layout.addWidget(self.system_date_format_combo, stretch=1)
        date_layout.addStretch()
        self.system_date_color_btn = QPushButton("")
        self.system_date_color_btn.setStyleSheet("background-color: #0000FF;")
        self.system_date_color_btn.clicked.connect(self._on_system_date_color_clicked)
        date_layout.addWidget(self.system_date_color_btn)
        vLayout_3.addLayout(date_layout)
        
        week_layout = QHBoxLayout()
        week_layout.setSpacing(8)
        self.system_week_check = QCheckBox("Week")
        self.system_week_check.setChecked(True)  # Default enabled
        self.system_week_check.toggled.connect(self._on_system_week_enabled_changed)
        week_layout.addWidget(self.system_week_check)
        week_layout.addStretch()
        self.system_week_format_combo = QComboBox()
        self.system_week_format_combo.addItems(["Full Name", "Short Name", "Number"])
        self.system_week_format_combo.currentTextChanged.connect(self._on_system_week_format_changed)
        week_layout.addWidget(self.system_week_format_combo, stretch=1)
        week_layout.addStretch()
        self.system_week_color_btn = QPushButton("")
        self.system_week_color_btn.setStyleSheet("background-color: #00FF00;")
        self.system_week_color_btn.clicked.connect(self._on_system_week_color_clicked)
        week_layout.addWidget(self.system_week_color_btn)
        vLayout_3.addLayout(week_layout)

        noon_layout = QHBoxLayout()
        self.system_noon_check = QCheckBox("AM/PM")
        self.system_noon_check.setChecked(True)  # Default enabled
        self.system_noon_check.toggled.connect(self._on_system_noon_enabled_changed)
        noon_layout.addWidget(self.system_noon_check)
        noon_layout.addStretch()
        self.system_noon_color_btn = QPushButton("")
        self.system_noon_color_btn.clicked.connect(self._on_system_noon_color_clicked)
        noon_layout.addWidget(self.system_noon_color_btn)
        vLayout_3.addLayout(noon_layout)

        form_layout.addLayout(vLayout_3)
        
        self.other_layout.addLayout(form_layout)
        self.other_layout.addStretch()
    
    def _setup_digital_clock_options(self):
        """Setup UI for Digital clock type"""
        self._clear_other_group()
        
        form_layout = QHBoxLayout()
        form_layout.setSpacing(8)
        
        vLayout_1 = QVBoxLayout()
        vLayout_1.setSpacing(8)
        vLayout_1.setContentsMargins(4, 4, 4, 4)
        
        font_family_layout = QHBoxLayout()
        self.digital_font_family_combo = QComboBox()
        self.digital_font_family_combo.addItems(["Arial", "Times New Roman", "Courier New", "Verdana", "Helvetica"])
        self.digital_font_family_combo.currentTextChanged.connect(self._on_digital_font_family_changed)
        font_family_layout.addWidget(self.digital_font_family_combo, stretch=1)
        vLayout_1.addLayout(font_family_layout)
        
        font_size_layout = QHBoxLayout()
        self.digital_font_size_spin = QSpinBox()
        self.digital_font_size_spin.setRange(8, 200)
        self.digital_font_size_spin.setValue(24)
        self.digital_font_size_spin.valueChanged.connect(self._on_digital_font_size_changed)
        font_size_layout.addWidget(self.digital_font_size_spin, stretch=1)
        vLayout_1.addLayout(font_size_layout)

        line_setting_layout = QHBoxLayout()
        self.digital_line_combo = QComboBox()
        self.digital_line_combo.addItems(["Single Line", "Multi Line"])
        self.digital_line_combo.currentTextChanged.connect(self._on_digital_line_changed)
        line_setting_layout.addWidget(self.digital_line_combo, stretch=1)
        vLayout_1.addLayout(line_setting_layout)

        form_layout.addLayout(vLayout_1)
        
        vLayout_2 = QVBoxLayout()
        vLayout_2.setSpacing(8)
        vLayout_2.setContentsMargins(4, 4, 4, 4)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        self.digital_title_check = QCheckBox("Title")
        self.digital_title_check.setChecked(True)  # Default enabled
        self.digital_title_check.toggled.connect(self._on_digital_title_enabled_changed)
        title_layout.addWidget(self.digital_title_check)
        title_layout.addStretch()
        self.digital_title_edit = QLineEdit()
        self.digital_title_edit.setPlaceholderText("Enter title text")
        self.digital_title_edit.textChanged.connect(self._on_digital_title_value_changed)
        title_layout.addWidget(self.digital_title_edit, stretch=1)
        title_layout.addStretch()
        self.digital_title_color_btn = QPushButton("")
        self.digital_title_color_btn.setStyleSheet("background-color: #FF0000;")
        self.digital_title_color_btn.clicked.connect(self._on_digital_title_color_clicked)
        title_layout.addWidget(self.digital_title_color_btn)
        vLayout_2.addLayout(title_layout)

        date_layout = QHBoxLayout()
        date_layout.setSpacing(8)
        self.digital_date_check = QCheckBox("Date")
        self.digital_date_check.setChecked(True)  # Default enabled
        self.digital_date_check.toggled.connect(self._on_digital_date_enabled_changed)
        date_layout.addWidget(self.digital_date_check)
        date_layout.addStretch()
        self.digital_date_format_combo = QComboBox()
        self.digital_date_format_combo.addItems(["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY", "YYYY/MM/DD"])
        self.digital_date_format_combo.currentTextChanged.connect(self._on_digital_date_format_changed)
        date_layout.addWidget(self.digital_date_format_combo, stretch=1)
        date_layout.addStretch()
        self.digital_date_color_btn = QPushButton("")
        self.digital_date_color_btn.setStyleSheet("background-color: #0000FF;")
        self.digital_date_color_btn.clicked.connect(self._on_digital_date_color_clicked)
        date_layout.addWidget(self.digital_date_color_btn)
        vLayout_2.addLayout(date_layout)
        
        time_layout = QHBoxLayout()
        time_layout.setSpacing(8)
        self.digital_time_check = QCheckBox("Time")
        self.digital_time_check.setChecked(True)
        self.digital_time_check.toggled.connect(self._on_digital_time_enabled_changed)
        time_layout.addWidget(self.digital_time_check)
        time_layout.addStretch()
        self.digital_time_format_combo = QComboBox()
        self.digital_time_format_combo.addItems(["HH:MM:SS", "HH:MM"])
        self.digital_time_format_combo.currentTextChanged.connect(self._on_digital_time_format_changed)
        time_layout.addWidget(self.digital_time_format_combo, stretch=1)
        time_layout.addStretch()
        self.digital_time_color_btn = QPushButton("")
        self.digital_time_color_btn.setStyleSheet("background-color: #FF0000;")
        self.digital_time_color_btn.clicked.connect(self._on_digital_time_color_clicked)
        time_layout.addWidget(self.digital_time_color_btn)
        vLayout_2.addLayout(time_layout)
        
        week_layout = QHBoxLayout()
        week_layout.setSpacing(8)
        self.digital_week_check = QCheckBox("Week")
        self.digital_week_check.setChecked(True)  # Default enabled
        self.digital_week_check.toggled.connect(self._on_digital_week_enabled_changed)
        week_layout.addWidget(self.digital_week_check)
        week_layout.addStretch()
        self.digital_week_format_combo = QComboBox()
        self.digital_week_format_combo.addItems(["Full Name", "Short Name", "Number"])
        self.digital_week_format_combo.currentTextChanged.connect(self._on_digital_week_format_changed)
        week_layout.addWidget(self.digital_week_format_combo, stretch=1)
        week_layout.addStretch()
        self.digital_week_color_btn = QPushButton("")
        self.digital_week_color_btn.setStyleSheet("background-color: #00FF00;")
        self.digital_week_color_btn.clicked.connect(self._on_digital_week_color_clicked)
        week_layout.addWidget(self.digital_week_color_btn)
        vLayout_2.addLayout(week_layout)

        form_layout.addLayout(vLayout_2)
        
        self.other_layout.addLayout(form_layout)
        self.other_layout.addStretch()
    
    def _setup_analog_clock_options(self):
        """Setup UI for Analog clock type"""
        self._clear_other_group()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        
        dial_plate_layout = QHBoxLayout()
        self.analog_dial_plate_edit = QLineEdit()
        self.analog_dial_plate_edit.setReadOnly(True)
        self.analog_dial_plate_btn = QPushButton("Browse...")
        self.analog_dial_plate_btn.clicked.connect(lambda: self._on_image_browse("dial_plate"))
        dial_plate_layout.addWidget(self.analog_dial_plate_edit, stretch=1)
        dial_plate_layout.addWidget(self.analog_dial_plate_btn)
        form_layout.addRow("Dial Plate:", dial_plate_layout)
        
        hour_hand_layout = QHBoxLayout()
        self.analog_hour_hand_edit = QLineEdit()
        self.analog_hour_hand_edit.setReadOnly(True)
        self.analog_hour_hand_btn = QPushButton("Browse...")
        self.analog_hour_hand_btn.clicked.connect(lambda: self._on_image_browse("hour_hand"))
        hour_hand_layout.addWidget(self.analog_hour_hand_edit, stretch=1)
        hour_hand_layout.addWidget(self.analog_hour_hand_btn)
        form_layout.addRow("Hour Hand:", hour_hand_layout)
        
        minute_hand_layout = QHBoxLayout()
        self.analog_minute_hand_edit = QLineEdit()
        self.analog_minute_hand_edit.setReadOnly(True)
        self.analog_minute_hand_btn = QPushButton("Browse...")
        self.analog_minute_hand_btn.clicked.connect(lambda: self._on_image_browse("minute_hand"))
        minute_hand_layout.addWidget(self.analog_minute_hand_edit, stretch=1)
        minute_hand_layout.addWidget(self.analog_minute_hand_btn)
        form_layout.addRow("Minute Hand:", minute_hand_layout)
        
        second_hand_layout = QHBoxLayout()
        self.analog_second_hand_edit = QLineEdit()
        self.analog_second_hand_edit.setReadOnly(True)
        self.analog_second_hand_btn = QPushButton("Browse...")
        self.analog_second_hand_btn.clicked.connect(lambda: self._on_image_browse("second_hand"))
        second_hand_layout.addWidget(self.analog_second_hand_edit, stretch=1)
        second_hand_layout.addWidget(self.analog_second_hand_btn)
        form_layout.addRow("Second Hand:", second_hand_layout)
        
        self.other_layout.addLayout(form_layout)
        self.other_layout.addStretch()
    
    def _clear_other_group(self):
        """Clear the Other group layout"""
        while self.other_layout.count():
            child = self.other_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
    
    def _clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
    
    def _on_clock_type_changed(self, clock_type: str):
        if not self.current_element or not self.current_program:
            return
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "clock" not in self.current_element["properties"]:
            self.current_element["properties"]["clock"] = {}
        
        self.current_element["properties"]["clock"]["type"] = clock_type
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("clock_type", clock_type)
        self._trigger_autosave()
        
        if clock_type == "System":
            self._setup_system_clock_options()
        elif clock_type == "Digital":
            self._setup_digital_clock_options()
        elif clock_type == "Analog":
            self._setup_analog_clock_options()
    
    def _on_timezone_changed(self, timezone: str):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "clock" not in self.current_element["properties"]:
            self.current_element["properties"]["clock"] = {}
        self.current_element["properties"]["clock"]["timezone"] = timezone
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("clock_timezone", timezone)
        self._trigger_autosave()
    
    def _on_correction_changed(self, value: int):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "clock" not in self.current_element["properties"]:
            self.current_element["properties"]["clock"] = {}
        self.current_element["properties"]["clock"]["correction"] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("clock_correction", value)
        self._trigger_autosave()
    
    def _on_image_browse(self, image_type: str):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select {image_type.replace('_', ' ').title()} Image",
            "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path and self.current_element and self.current_program:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "clock" not in self.current_element["properties"]:
                self.current_element["properties"]["clock"] = {}
            if "analog" not in self.current_element["properties"]["clock"]:
                self.current_element["properties"]["clock"]["analog"] = {}
            
            self.current_element["properties"]["clock"]["analog"][image_type] = file_path
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit(f"clock_analog_{image_type}", file_path)
            self._trigger_autosave()
            
            if image_type == "dial_plate":
                self.analog_dial_plate_edit.setText(file_path)
            elif image_type == "hour_hand":
                self.analog_hour_hand_edit.setText(file_path)
            elif image_type == "minute_hand":
                self.analog_minute_hand_edit.setText(file_path)
            elif image_type == "second_hand":
                self.analog_second_hand_edit.setText(file_path)
    
    # System clock handlers
    def _on_system_font_family_changed(self, font_family: str):
        self._update_system_property("font_family", font_family)
    
    def _on_system_font_size_changed(self, font_size: int):
        self._update_system_property("font_size", font_size)
    
    def _on_system_hour_scale_shape_changed(self, shape: str):
        self._update_system_property("hour_scale_shape", shape)
    
    def _on_system_hour_scale_color_clicked(self):
        current_color = QColor("#FF0000")  # Default red
        if hasattr(self, 'system_hour_scale_color_btn'):
            current_style = self.system_hour_scale_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("hour_scale_color", color.name())
            self.system_hour_scale_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_minute_scale_shape_changed(self, shape: str):
        self._update_system_property("minute_scale_shape", shape)
    
    def _on_system_minute_scale_color_clicked(self):
        current_color = QColor("#00FF00")  # Default green
        if hasattr(self, 'system_minute_scale_color_btn'):
            current_style = self.system_minute_scale_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("minute_scale_color", color.name())
            self.system_minute_scale_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_hour_hand_shape_changed(self, shape: str):
        self._update_system_property("hour_hand_shape", shape)
    
    def _on_system_hour_hand_color_clicked(self):
        current_color = QColor("#FF0000")  # Default red
        if hasattr(self, 'system_hour_hand_color_btn'):
            current_style = self.system_hour_hand_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("hour_hand_color", color.name())
            self.system_hour_hand_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_minute_hand_shape_changed(self, shape: str):
        self._update_system_property("minute_hand_shape", shape)
    
    def _on_system_minute_hand_color_clicked(self):
        current_color = QColor("#00FF00")  # Default green
        if hasattr(self, 'system_minute_hand_color_btn'):
            current_style = self.system_minute_hand_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("minute_hand_color", color.name())
            self.system_minute_hand_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_second_hand_shape_changed(self, shape: str):
        self._update_system_property("second_hand_shape", shape)
    
    def _on_system_second_hand_color_clicked(self):
        current_color = QColor("#0000FF")  # Default blue
        if hasattr(self, 'system_second_hand_color_btn'):
            current_style = self.system_second_hand_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("second_hand_color", color.name())
            self.system_second_hand_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_title_enabled_changed(self, enabled: bool):
        self._update_system_property("title_enabled", enabled)
    
    def _on_system_title_value_changed(self, value: str):
        self._update_system_property("title_value", value)
    
    def _on_system_title_color_clicked(self):
        current_color = QColor("#0000FF")  # Default blue
        if hasattr(self, 'system_title_color_btn'):
            current_style = self.system_title_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("title_color", color.name())
            self.system_title_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_date_enabled_changed(self, enabled: bool):
        self._update_system_property("date_enabled", enabled)
    
    def _on_system_date_format_changed(self, format_str: str):
        self._update_system_property("date_format", format_str)
    
    def _on_system_date_color_clicked(self):
        current_color = QColor("#0000FF")  # Default blue
        if hasattr(self, 'system_date_color_btn'):
            current_style = self.system_date_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("date_color", color.name())
            self.system_date_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_noon_enabled_changed(self, enabled: bool):
        self._update_system_property("noon_enabled", enabled)
    
    def _on_system_noon_color_clicked(self):
        current_color = QColor("#0000FF")  # Default blue
        if hasattr(self, 'system_noon_color_btn'):
            current_style = self.system_noon_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("noon_color", color.name())
            self.system_noon_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_system_week_enabled_changed(self, enabled: bool):
        self._update_system_property("week_enabled", enabled)
    
    def _on_system_week_format_changed(self, format_str: str):
        self._update_system_property("week_format", format_str)
    
    def _on_system_week_color_clicked(self):
        current_color = QColor("#00FF00")  # Default green
        if hasattr(self, 'system_week_color_btn'):
            current_style = self.system_week_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_system_property("week_color", color.name())
            self.system_week_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _update_system_property(self, key: str, value):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "clock" not in self.current_element["properties"]:
            self.current_element["properties"]["clock"] = {}
        if "system" not in self.current_element["properties"]["clock"]:
            self.current_element["properties"]["clock"]["system"] = {}
        self.current_element["properties"]["clock"]["system"][key] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit(f"clock_system_{key}", value)
        self._trigger_autosave()
    
    # Digital clock handlers
    def _on_digital_font_family_changed(self, font_family: str):
        self._update_digital_property("font_family", font_family)
    
    def _on_digital_font_size_changed(self, font_size: int):
        self._update_digital_property("font_size", font_size)
    
    def _on_digital_title_enabled_changed(self, enabled: bool):
        self._update_digital_property("title_enabled", enabled)
    
    def _on_digital_title_value_changed(self, value: str):
        self._update_digital_property("title_value", value)
    
    def _on_digital_title_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self._update_digital_property("title_color", color.name())
            self.digital_title_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_digital_date_enabled_changed(self, enabled: bool):
        self._update_digital_property("date_enabled", enabled)
    
    def _on_digital_date_format_changed(self, format_str: str):
        self._update_digital_property("date_format", format_str)
    
    def _on_digital_date_color_clicked(self):
        current_color = QColor("#0000FF")  # Default blue
        if hasattr(self, 'digital_date_color_btn'):
            current_style = self.digital_date_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_digital_property("date_color", color.name())
            self.digital_date_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_digital_time_enabled_changed(self, enabled: bool):
        self._update_digital_property("time_enabled", enabled)
    
    def _on_digital_time_format_changed(self, format_str: str):
        self._update_digital_property("time_format", format_str)
    
    def _on_digital_time_color_clicked(self):
        current_color = QColor("#FF0000")  # Default red
        if hasattr(self, 'digital_time_color_btn'):
            current_style = self.digital_time_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_digital_property("time_color", color.name())
            self.digital_time_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_digital_week_enabled_changed(self, enabled: bool):
        self._update_digital_property("week_enabled", enabled)
    
    def _on_digital_week_format_changed(self, format_str: str):
        self._update_digital_property("week_format", format_str)
    
    def _on_digital_week_color_clicked(self):
        current_color = QColor("#00FF00")  # Default green
        if hasattr(self, 'digital_week_color_btn'):
            current_style = self.digital_week_color_btn.styleSheet()
            if "background-color:" in current_style:
                try:
                    color_str = current_style.split("background-color:")[1].split(";")[0].strip()
                    current_color = QColor(color_str)
                except:
                    pass
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self._update_digital_property("week_color", color.name())
            self.digital_week_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_digital_line_changed(self, line_setting: str):
        self._update_digital_property("line_setting", line_setting)
    
    def _update_digital_property(self, key: str, value):
        if not self.current_element or not self.current_program:
            return
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "clock" not in self.current_element["properties"]:
            self.current_element["properties"]["clock"] = {}
        if "digital" not in self.current_element["properties"]["clock"]:
            self.current_element["properties"]["clock"]["digital"] = {}
        self.current_element["properties"]["clock"]["digital"][key] = value
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit(f"clock_digital_{key}", value)
        self._trigger_autosave()
    
    def _on_coords_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            x = int(self.clock_coords_x.text() or "0")
            y = int(self.clock_coords_y.text() or "0")
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
            self.property_changed.emit("clock_position", (x, y))
            self._trigger_autosave()
        except ValueError:
            pass
    
    def _on_dims_changed(self):
        if not self.current_element or not self.current_program:
            return
        try:
            width = int(self.clock_dims_width.text() or "640")
            height = int(self.clock_dims_height.text() or "480")
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
            self.property_changed.emit("clock_size", (width, height))
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
        self.clock_coords_x.blockSignals(True)
        self.clock_coords_y.blockSignals(True)
        self.clock_coords_x.setText(str(x))
        self.clock_coords_y.setText(str(y))
        self.clock_coords_x.blockSignals(False)
        self.clock_coords_y.blockSignals(False)
        
        width = element_props.get("width", self.current_element.get("width", default_width))
        height = element_props.get("height", self.current_element.get("height", default_height))
        
        if not width or width <= 0:
            width = default_width
        if not height or height <= 0:
            height = default_height
        
        self.clock_dims_width.blockSignals(True)
        self.clock_dims_height.blockSignals(True)
        self.clock_dims_width.setText(str(width))
        self.clock_dims_height.setText(str(height))
        self.clock_dims_width.blockSignals(False)
        self.clock_dims_height.blockSignals(False)
        
        clock_props = element_props.get("clock", {})
        clock_type = clock_props.get("type", "System")
        clock_type_index = self.clock_type_combo.findText(clock_type)
        if clock_type_index >= 0:
            self.clock_type_combo.setCurrentIndex(clock_type_index)
        else:
            self.clock_type_combo.setCurrentIndex(0)
        
        timezone = clock_props.get("timezone", "Local")
        timezone_index = self.clock_timezone_combo.findText(timezone)
        if timezone_index >= 0:
            self.clock_timezone_combo.setCurrentIndex(timezone_index)
        else:
            self.clock_timezone_combo.setCurrentIndex(1)
        
        correction = clock_props.get("correction", 0)
        self.clock_correction_spin.blockSignals(True)
        self.clock_correction_spin.setValue(correction)
        self.clock_correction_spin.blockSignals(False)
        
        # Update UI based on clock type
        if clock_type == "System":
            self._setup_system_clock_options()
            system_props = clock_props.get("system", {})
            if hasattr(self, 'system_font_family_combo'):
                font_family = system_props.get("font_family", "Arial")
                self.system_font_family_combo.setCurrentText(font_family)
            if hasattr(self, 'system_font_size_spin'):
                font_size = system_props.get("font_size", 24)
                self.system_font_size_spin.setValue(font_size)
            # Load clock options
            if hasattr(self, 'system_title_check'):
                self.system_title_check.setChecked(system_props.get("title_enabled", True))  # Default enabled
                if hasattr(self, 'system_title_edit'):
                    self.system_title_edit.setText(system_props.get("title_value", "LED"))  # Default "LED"
                if hasattr(self, 'system_title_color_btn'):
                    title_color = system_props.get("title_color", "#0000FF")
                    self.system_title_color_btn.setStyleSheet(f"background-color: {title_color};")
            if hasattr(self, 'system_date_check'):
                self.system_date_check.setChecked(system_props.get("date_enabled", True))  # Default enabled
                if hasattr(self, 'system_date_format_combo'):
                    self.system_date_format_combo.setCurrentText(system_props.get("date_format", "YYYY-MM-DD"))
                if hasattr(self, 'system_date_color_btn'):
                    date_color = system_props.get("date_color", "#0000FF")
                    self.system_date_color_btn.setStyleSheet(f"background-color: {date_color};")
            if hasattr(self, 'system_noon_check'):
                self.system_noon_check.setChecked(system_props.get("noon_enabled", True))  # Default enabled
                if hasattr(self, 'system_noon_color_btn'):
                    noon_color = system_props.get("noon_color", "#0000FF")
                    self.system_noon_color_btn.setStyleSheet(f"background-color: {noon_color};")
            if hasattr(self, 'system_week_check'):
                self.system_week_check.setChecked(system_props.get("week_enabled", True))  # Default enabled
                if hasattr(self, 'system_week_format_combo'):
                    self.system_week_format_combo.setCurrentText(system_props.get("week_format", "Full Name"))
                if hasattr(self, 'system_week_color_btn'):
                    week_color = system_props.get("week_color", "#00FF00")
                    self.system_week_color_btn.setStyleSheet(f"background-color: {week_color};")
        elif clock_type == "Digital":
            self._setup_digital_clock_options()
            digital_props = clock_props.get("digital", {})
            if hasattr(self, 'digital_font_family_combo'):
                font_family = digital_props.get("font_family", "Arial")
                self.digital_font_family_combo.setCurrentText(font_family)
            if hasattr(self, 'digital_font_size_spin'):
                font_size = digital_props.get("font_size", 24)
                self.digital_font_size_spin.setValue(font_size)
            # Load clock options
            if hasattr(self, 'digital_title_check'):
                self.digital_title_check.setChecked(digital_props.get("title_enabled", True))  # Default enabled
                if hasattr(self, 'digital_title_edit'):
                    self.digital_title_edit.setText(digital_props.get("title_value", "Clock"))
                if hasattr(self, 'digital_title_color_btn'):
                    title_color = digital_props.get("title_color", "#FF0000")
                    self.digital_title_color_btn.setStyleSheet(f"background-color: {title_color};")
            if hasattr(self, 'digital_date_check'):
                self.digital_date_check.setChecked(digital_props.get("date_enabled", True))  # Default enabled
                if hasattr(self, 'digital_date_format_combo'):
                    self.digital_date_format_combo.setCurrentText(digital_props.get("date_format", "YYYY-MM-DD"))
                if hasattr(self, 'digital_date_color_btn'):
                    date_color = digital_props.get("date_color", "#0000FF")
                    self.digital_date_color_btn.setStyleSheet(f"background-color: {date_color};")
            if hasattr(self, 'digital_time_check'):
                self.digital_time_check.setChecked(digital_props.get("time_enabled", True))
                if hasattr(self, 'digital_time_format_combo'):
                    self.digital_time_format_combo.setCurrentText(digital_props.get("time_format", "HH:MM:SS"))
                if hasattr(self, 'digital_time_color_btn'):
                    time_color = digital_props.get("time_color", "#FF0000")
                    self.digital_time_color_btn.setStyleSheet(f"background-color: {time_color};")
            if hasattr(self, 'digital_week_check'):
                self.digital_week_check.setChecked(digital_props.get("week_enabled", True))  # Default enabled
                if hasattr(self, 'digital_week_format_combo'):
                    self.digital_week_format_combo.setCurrentText(digital_props.get("week_format", "Full Name"))
                if hasattr(self, 'digital_week_color_btn'):
                    week_color = digital_props.get("week_color", "#00FF00")
                    self.digital_week_color_btn.setStyleSheet(f"background-color: {week_color};")
        elif clock_type == "Analog":
            self._setup_analog_clock_options()
            analog_props = clock_props.get("analog", {})
            if hasattr(self, 'analog_dial_plate_edit'):
                dial_plate = analog_props.get("dial_plate", "")
                self.analog_dial_plate_edit.setText(dial_plate)
            if hasattr(self, 'analog_hour_hand_edit'):
                hour_hand = analog_props.get("hour_hand", "")
                self.analog_hour_hand_edit.setText(hour_hand)
            if hasattr(self, 'analog_minute_hand_edit'):
                minute_hand = analog_props.get("minute_hand", "")
                self.analog_minute_hand_edit.setText(minute_hand)
            if hasattr(self, 'analog_second_hand_edit'):
                second_hand = analog_props.get("second_hand", "")
                self.analog_second_hand_edit.setText(second_hand)
