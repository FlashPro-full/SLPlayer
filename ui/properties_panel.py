"""
Properties panel that shows different properties based on selection
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QSpinBox, QPushButton, QFileDialog, QListWidget, QListWidgetItem,
                             QGroupBox, QFormLayout, QTimeEdit, QDateEdit, QCheckBox, QSlider,
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton,
                             QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal, QTime, QDate
from PyQt5.QtGui import QIcon
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from core.program_manager import ProgramManager
from core.program_manager import Program
from config.i18n import tr


class PropertiesPanel(QWidget):
    """Properties panel showing properties based on selection"""
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.current_element: Optional[Dict] = None
        self.current_screen_name: Optional[str] = None
        self.current_screen_programs: List[Program] = []
        self.main_window = parent
        self.init_ui()
    
    def _trigger_autosave(self):
        """Trigger autosave and refresh UI if main window exists"""
        if self.main_window and self.current_program:
            # Use main window's save_and_refresh to ensure UI is updated
            if hasattr(self.main_window, '_save_and_refresh'):
                self.main_window._save_and_refresh(self.current_program)
            elif hasattr(self.main_window, 'auto_save_manager'):
                self.main_window.auto_save_manager.save_current_program()
                # Trigger UI refresh
                if hasattr(self.main_window, 'program_list_panel'):
                    self.main_window.program_list_panel.refresh_programs()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
        """)
        
        self.program_properties_widget = self._create_program_properties()
        self.video_properties_widget = self._create_video_properties()
        self.screen_properties_widget = self._create_screen_properties()
        self.empty_widget = QWidget()
        
        self._load_frame_borders()
        
        layout.addWidget(self.program_properties_widget)
        layout.addWidget(self.video_properties_widget)
        layout.addWidget(self.screen_properties_widget)
        layout.addWidget(self.empty_widget)
        
        self.show_empty()
    
    def _create_program_properties(self) -> QWidget:
        """Create program properties widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        program_props_group = QGroupBox("Program properties")
        program_props_layout = QVBoxLayout(program_props_group)
        program_props_layout.setContentsMargins(8, 8, 8, 8)
        program_props_layout.setSpacing(8)
        
        frame_layout = QHBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_checkbox = QCheckBox("Frame")
        self.frame_checkbox.toggled.connect(self._on_frame_enabled_changed)
        frame_layout.addWidget(self.frame_checkbox)
        self.frame_combo = QComboBox()
        self.frame_combo.setEnabled(False)
        self.frame_combo.currentTextChanged.connect(self._on_frame_changed)
        frame_layout.addWidget(self.frame_combo, stretch=1)
        program_props_layout.addLayout(frame_layout)
        
        bg_music_layout = QHBoxLayout()
        bg_music_layout.setContentsMargins(0, 0, 0, 0)
        self.bg_music_checkbox = QCheckBox("Background Music")
        self.bg_music_checkbox.toggled.connect(self._on_bg_music_enabled_changed)
        bg_music_layout.addWidget(self.bg_music_checkbox)
        self.bg_music_combo = QComboBox()
        self.bg_music_combo.setEnabled(False)
        self.bg_music_combo.setEditable(True)
        self.bg_music_combo.currentTextChanged.connect(self._on_bg_music_changed)
        self.bg_music_browse_btn = QPushButton("Browse...")
        self.bg_music_browse_btn.setEnabled(False)
        self.bg_music_browse_btn.clicked.connect(self._on_browse_bg_music)
        bg_music_layout.addWidget(self.bg_music_combo, stretch=1)
        bg_music_layout.addWidget(self.bg_music_browse_btn)
        program_props_layout.addLayout(bg_music_layout)
        
        play_mode_group = QGroupBox("Play mode")
        play_mode_layout = QVBoxLayout(play_mode_group)
        play_mode_layout.setContentsMargins(8, 8, 8, 8)
        play_mode_layout.setSpacing(8)
        
        self.play_mode_button_group = QButtonGroup()
        play_times_layout = QHBoxLayout()
        play_times_layout.setContentsMargins(0, 0, 0, 0)
        self.play_times_radio = QRadioButton("Play times")
        self.play_times_radio.toggled.connect(self._on_play_mode_changed)
        self.play_mode_button_group.addButton(self.play_times_radio, 0)
        play_times_layout.addWidget(self.play_times_radio)
        self.play_times_spin = QSpinBox()
        self.play_times_spin.setMinimum(1)
        self.play_times_spin.setMaximum(9999)
        self.play_times_spin.setValue(1)
        self.play_times_spin.setEnabled(True)
        self.play_times_spin.valueChanged.connect(self._on_play_times_changed)
        play_times_layout.addWidget(self.play_times_spin)
        play_times_layout.addStretch()
        play_mode_layout.addLayout(play_times_layout)
        
        fixed_length_layout = QHBoxLayout()
        fixed_length_layout.setContentsMargins(0, 0, 0, 0)
        self.fixed_length_radio = QRadioButton("Fixed length")
        self.fixed_length_radio.toggled.connect(self._on_play_mode_changed)
        self.play_mode_button_group.addButton(self.fixed_length_radio, 1)
        fixed_length_layout.addWidget(self.fixed_length_radio)
        self.fixed_length_time = QTimeEdit()
        self.fixed_length_time.setDisplayFormat("HH:mm:ss")
        self.fixed_length_time.setTime(QTime(0, 0, 30))
        self.fixed_length_time.setEnabled(False)
        self.fixed_length_time.timeChanged.connect(self._on_fixed_length_changed)
        fixed_length_layout.addWidget(self.fixed_length_time)
        fixed_length_layout.addStretch()
        play_mode_layout.addLayout(fixed_length_layout)
        
        play_control_group = QGroupBox("Play control")
        play_control_layout = QVBoxLayout(play_control_group)
        play_control_layout.setContentsMargins(8, 8, 8, 8)
        play_control_layout.setSpacing(8)
        
        specified_time_layout = QVBoxLayout()
        specified_time_layout.setContentsMargins(0, 0, 0, 0)
        self.specified_time_checkbox = QCheckBox("Specified time")
        self.specified_time_checkbox.toggled.connect(self._on_specified_time_enabled_changed)
        specified_time_layout.addWidget(self.specified_time_checkbox)
        time_range_layout = QHBoxLayout()
        time_range_layout.setContentsMargins(20, 0, 0, 0)
        time_range_layout.addWidget(QLabel("Start:"))
        self.specified_start_time = QTimeEdit()
        self.specified_start_time.setDisplayFormat("HH:mm:ss")
        self.specified_start_time.setTime(QTime(0, 0, 0))
        self.specified_start_time.setEnabled(False)
        self.specified_start_time.timeChanged.connect(self._on_specified_time_changed)
        time_range_layout.addWidget(self.specified_start_time)
        time_range_layout.addWidget(QLabel("End:"))
        self.specified_end_time = QTimeEdit()
        self.specified_end_time.setDisplayFormat("HH:mm:ss")
        self.specified_end_time.setTime(QTime(23, 59, 59))
        self.specified_end_time.setEnabled(False)
        self.specified_end_time.timeChanged.connect(self._on_specified_time_changed)
        time_range_layout.addWidget(self.specified_end_time)
        time_range_layout.addStretch()
        specified_time_layout.addLayout(time_range_layout)
        play_control_layout.addLayout(specified_time_layout)
        
        specify_week_layout = QVBoxLayout()
        specify_week_layout.setContentsMargins(0, 0, 0, 0)
        self.specify_week_checkbox = QCheckBox("Specify the week")
        self.specify_week_checkbox.toggled.connect(self._on_specify_week_enabled_changed)
        specify_week_layout.addWidget(self.specify_week_checkbox)
        week_days_layout = QHBoxLayout()
        week_days_layout.setContentsMargins(20, 0, 0, 0)
        self.week_checkboxes = []
        week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in week_days:
            cb = QCheckBox(day)
            cb.setEnabled(False)
            cb.toggled.connect(self._on_week_day_changed)
            self.week_checkboxes.append(cb)
            week_days_layout.addWidget(cb)
        week_days_layout.addStretch()
        specify_week_layout.addLayout(week_days_layout)
        play_control_layout.addLayout(specify_week_layout)
        
        specify_date_layout = QVBoxLayout()
        specify_date_layout.setContentsMargins(0, 0, 0, 0)
        self.specify_date_checkbox = QCheckBox("Specify the date")
        self.specify_date_checkbox.toggled.connect(self._on_specify_date_enabled_changed)
        specify_date_layout.addWidget(self.specify_date_checkbox)
        date_range_layout = QHBoxLayout()
        date_range_layout.setContentsMargins(20, 0, 0, 0)
        date_range_layout.addWidget(QLabel("Start:"))
        self.specified_start_date = QDateEdit()
        self.specified_start_date.setCalendarPopup(True)
        self.specified_start_date.setDate(QDate.currentDate())
        self.specified_start_date.setEnabled(False)
        self.specified_start_date.dateChanged.connect(self._on_specified_date_changed)
        date_range_layout.addWidget(self.specified_start_date)
        date_range_layout.addWidget(QLabel("End:"))
        self.specified_end_date = QDateEdit()
        self.specified_end_date.setCalendarPopup(True)
        self.specified_end_date.setDate(QDate.currentDate())
        self.specified_end_date.setEnabled(False)
        self.specified_end_date.dateChanged.connect(self._on_specified_date_changed)
        date_range_layout.addWidget(self.specified_end_date)
        date_range_layout.addStretch()
        specify_date_layout.addLayout(date_range_layout)
        play_control_layout.addLayout(specify_date_layout)
        
        main_row_layout = QHBoxLayout()
        main_row_layout.setContentsMargins(0, 0, 0, 0)
        main_row_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        main_row_layout.addWidget(program_props_group)
        main_row_layout.addWidget(play_mode_group)
        main_row_layout.addWidget(play_control_group)
        main_row_layout.addStretch()
        
        layout.insertLayout(0, main_row_layout)
        layout.addStretch()
        return widget
    
    def _create_video_properties(self) -> QWidget:
        """Create video properties widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        area_group = QGroupBox("Area Attribute")
        area_layout = QFormLayout(area_group)
        
        self.video_x_spin = QSpinBox()
        self.video_x_spin.setMinimum(0)
        self.video_x_spin.setMaximum(99999)
        self.video_x_spin.valueChanged.connect(self._on_video_position_changed)
        area_layout.addRow("X (Top Left):", self.video_x_spin)
        
        self.video_y_spin = QSpinBox()
        self.video_y_spin.setMinimum(0)
        self.video_y_spin.setMaximum(99999)
        self.video_y_spin.valueChanged.connect(self._on_video_position_changed)
        area_layout.addRow("Y (Top Left):", self.video_y_spin)
        
        self.video_width_spin = QSpinBox()
        self.video_width_spin.setMinimum(1)
        self.video_width_spin.setMaximum(99999)
        self.video_width_spin.valueChanged.connect(self._on_video_size_changed)
        area_layout.addRow("Width:", self.video_width_spin)
        
        self.video_height_spin = QSpinBox()
        self.video_height_spin.setMinimum(1)
        self.video_height_spin.setMaximum(99999)
        self.video_height_spin.valueChanged.connect(self._on_video_size_changed)
        area_layout.addRow("Height:", self.video_height_spin)
        
        self.video_frame_combo = QComboBox()
        self.video_frame_combo.currentTextChanged.connect(self._on_video_frame_changed)
        area_layout.addRow("Frame:", self.video_frame_combo)
        
        self.video_transparency_slider = QSlider(Qt.Horizontal)
        self.video_transparency_slider.setMinimum(0)
        self.video_transparency_slider.setMaximum(100)
        self.video_transparency_slider.setValue(100)
        self.video_transparency_slider.valueChanged.connect(self._on_video_transparency_changed)
        self.video_transparency_label = QLabel("100%")
        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(self.video_transparency_slider)
        transparency_layout.addWidget(self.video_transparency_label)
        area_layout.addRow("Transparency:", transparency_layout)
        
        layout.addWidget(area_group)
        
        video_list_group = QGroupBox("Video List")
        video_list_layout = QVBoxLayout(video_list_group)
        
        self.video_list = QListWidget()
        video_list_layout.addWidget(self.video_list)
        
        video_list_buttons = QHBoxLayout()
        self.video_add_btn = QPushButton("+")
        self.video_add_btn.clicked.connect(self._on_video_add)
        self.video_delete_btn = QPushButton("🗑")
        self.video_delete_btn.clicked.connect(self._on_video_delete)
        self.video_up_btn = QPushButton("🔼")
        self.video_up_btn.clicked.connect(self._on_video_up)
        self.video_down_btn = QPushButton("🔽")
        self.video_down_btn.clicked.connect(self._on_video_down)
        video_list_buttons.addWidget(self.video_add_btn)
        video_list_buttons.addWidget(self.video_delete_btn)
        video_list_buttons.addWidget(self.video_up_btn)
        video_list_buttons.addWidget(self.video_down_btn)
        video_list_buttons.addStretch()
        video_list_layout.addLayout(video_list_buttons)
        
        layout.addWidget(video_list_group)
        
        video_shot_group = QGroupBox("Video Shot")
        video_shot_layout = QFormLayout(video_shot_group)
        
        self.video_shot_width_spin = QSpinBox()
        self.video_shot_width_spin.setMinimum(1)
        self.video_shot_width_spin.setMaximum(99999)
        self.video_shot_width_spin.valueChanged.connect(self._on_video_shot_size_changed)
        video_shot_layout.addRow("Width:", self.video_shot_width_spin)
        
        self.video_shot_height_spin = QSpinBox()
        self.video_shot_height_spin.setMinimum(1)
        self.video_shot_height_spin.setMaximum(99999)
        self.video_shot_height_spin.valueChanged.connect(self._on_video_shot_size_changed)
        video_shot_layout.addRow("Height:", self.video_shot_height_spin)
        
        self.video_shot_start_time = QTimeEdit()
        self.video_shot_start_time.setDisplayFormat("HH:mm:ss")
        self.video_shot_start_time.setTime(QTime(0, 0, 0))
        self.video_shot_start_time.timeChanged.connect(self._on_video_shot_time_changed)
        video_shot_layout.addRow("Start time:", self.video_shot_start_time)
        
        self.video_shot_end_time = QTimeEdit()
        self.video_shot_end_time.setDisplayFormat("HH:mm:ss")
        self.video_shot_end_time.setTime(QTime(0, 0, 30))
        self.video_shot_end_time.timeChanged.connect(self._on_video_shot_time_changed)
        video_shot_layout.addRow("End time:", self.video_shot_end_time)
        
        self.video_shot_duration_label = QLabel("00:00:30")
        video_shot_layout.addRow("Duration:", self.video_shot_duration_label)
        
        layout.addWidget(video_shot_group)
        
        layout.addStretch()
        return widget
    
    def _create_screen_properties(self) -> QWidget:
        """Create screen properties widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        display_props_group = QGroupBox("Display properties")
        display_props_group.setMinimumWidth(300)
        display_props_layout = QFormLayout(display_props_group)
        display_props_layout.setContentsMargins(8, 8, 8, 8)
        display_props_layout.setSpacing(8)
        
        self.screen_controller_type_input = QLineEdit()
        self.screen_controller_type_input.setReadOnly(True)
        self.screen_controller_type_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #CCCCCC;
                background-color: transparent;
                padding: 2px 0px;
            }
        """)
        display_props_layout.addRow("Controller Type:", self.screen_controller_type_input)
        
        self.screen_size_input = QLineEdit()
        self.screen_size_input.setReadOnly(True)
        self.screen_size_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #CCCCCC;
                background-color: transparent;
                padding: 2px 0px;
            }
        """)
        display_props_layout.addRow("Screen Size:", self.screen_size_input)
        
        self.screen_path_input = QLineEdit()
        self.screen_path_input.setReadOnly(True)
        self.screen_path_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #CCCCCC;
                background-color: transparent;
                padding: 2px 0px;
            }
        """)
        display_props_layout.addRow("Path:", self.screen_path_input)
        
        related_equipment_group = QGroupBox("Related equipment")
        related_equipment_layout = QVBoxLayout(related_equipment_group)
        related_equipment_layout.setContentsMargins(8, 8, 8, 8)
        related_equipment_layout.setSpacing(8)
        
        self.related_equipment_table = QTableWidget()
        self.related_equipment_table.setColumnCount(2)
        self.related_equipment_table.setHorizontalHeaderLabels(["Name", "Type"])
        self.related_equipment_table.horizontalHeader().setVisible(False)
        self.related_equipment_table.verticalHeader().setVisible(False)
        self.related_equipment_table.setShowGrid(False)
        self.related_equipment_table.setAlternatingRowColors(True)
        self.related_equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.related_equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        related_equipment_layout.addWidget(self.related_equipment_table)
        
        layout.addWidget(display_props_group)
        layout.addWidget(related_equipment_group)
        layout.addStretch()
        
        return widget
    
    def _load_frame_borders(self):
        """Load frame borders from resources"""
        resources_path = Path(__file__).parent.parent / "resources" / "Reference" / "images" / "Border"
        if resources_path.exists():
            border_files = sorted(resources_path.glob("*.png"))
            for border_file in border_files:
                self.video_frame_combo.addItem(border_file.stem, str(border_file))
                self.frame_combo.addItem(border_file.stem, str(border_file))
        else:
            self.video_frame_combo.addItem("None", "")
            self.frame_combo.addItem("None", "")
    
    def set_program(self, program: Optional[Program]):
        """Set the current program"""
        self.current_program = program
        self.current_element = None
        if program:
            self.show_program_properties()
            self._update_program_properties()
        else:
            self.show_empty()
    
    def set_element(self, element: Optional[Dict], program: Optional[Program]):
        """Set the current element"""
        self.current_element = element
        self.current_program = program
        if element and element.get("type") == "video":
            self.show_video_properties()
            self._update_video_properties()
        elif program:
            self.show_program_properties()
            self._update_program_properties()
        else:
            self.show_empty()
    
    def set_screen(self, screen_name: str, programs: List[Program], program_manager: Optional[ProgramManager] = None):
        """Set the current screen"""
        self.current_screen_name = screen_name
        self.current_screen_programs = programs
        self.current_program = None
        self.current_element = None
        if screen_name and programs:
            self.show_screen_properties()
            self._update_screen_properties(program_manager)
        else:
            self.show_empty()
    
    def show_program_properties(self):
        """Show program properties"""
        self.program_properties_widget.setVisible(True)
        self.video_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(False)
    
    def show_video_properties(self):
        """Show video properties"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(True)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(False)
    
    def show_screen_properties(self):
        """Show screen properties"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(True)
        self.empty_widget.setVisible(False)
    
    def show_empty(self):
        """Show empty state"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(True)
    
    def _update_program_properties(self):
        """Update program properties from current program"""
        if not self.current_program:
            return
        
        props = self.current_program.properties
        
        frame_props = props.get("frame", {})
        frame_enabled = frame_props.get("enabled", False)
        frame_style = frame_props.get("style", "---")
        self.frame_checkbox.blockSignals(True)
        self.frame_checkbox.setChecked(frame_enabled)
        self.frame_checkbox.blockSignals(False)
        self.frame_combo.setEnabled(frame_enabled)
        frame_index = self.frame_combo.findText(frame_style)
        if frame_index >= 0:
            self.frame_combo.setCurrentIndex(frame_index)
        else:
            self.frame_combo.setCurrentIndex(0)
        
        bg_music_props = props.get("background_music", {})
        bg_music_enabled = bg_music_props.get("enabled", False)
        bg_music_file = bg_music_props.get("file", "")
        self.bg_music_checkbox.blockSignals(True)
        self.bg_music_checkbox.setChecked(bg_music_enabled)
        self.bg_music_checkbox.blockSignals(False)
        self.bg_music_combo.setEnabled(bg_music_enabled)
        self.bg_music_browse_btn.setEnabled(bg_music_enabled)
        if bg_music_file:
            self.bg_music_combo.setCurrentText(bg_music_file)
        else:
            self.bg_music_combo.setCurrentText("")
        
        play_mode = self.current_program.play_mode
        mode = play_mode.get("mode", "play_times")
        if mode == "play_times":
            self.play_times_radio.setChecked(True)
            self.play_times_spin.setValue(play_mode.get("play_times", 1))
            self.play_times_spin.setEnabled(True)
            self.fixed_length_time.setEnabled(False)
        else:
            self.fixed_length_radio.setChecked(True)
            fixed_length_str = play_mode.get("fixed_length", "0:00:30")
            time_parts = fixed_length_str.split(":")
            if len(time_parts) == 3:
                self.fixed_length_time.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2])))
            self.play_times_spin.setEnabled(False)
            self.fixed_length_time.setEnabled(True)
        
        play_control = self.current_program.play_control
        specified_time = play_control.get("specified_time", {})
        self.specified_time_checkbox.blockSignals(True)
        self.specified_time_checkbox.setChecked(specified_time.get("enabled", False))
        self.specified_time_checkbox.blockSignals(False)
        self.specified_start_time.setEnabled(specified_time.get("enabled", False))
        self.specified_end_time.setEnabled(specified_time.get("enabled", False))
        start_time_str = specified_time.get("start_time", "00:00:00")
        end_time_str = specified_time.get("end_time", "23:59:59")
        start_parts = start_time_str.split(":")
        end_parts = end_time_str.split(":")
        if len(start_parts) == 3:
            self.specified_start_time.setTime(QTime(int(start_parts[0]), int(start_parts[1]), int(start_parts[2])))
        if len(end_parts) == 3:
            self.specified_end_time.setTime(QTime(int(end_parts[0]), int(end_parts[1]), int(end_parts[2])))
        
        specify_week = play_control.get("specify_week", {})
        self.specify_week_checkbox.blockSignals(True)
        self.specify_week_checkbox.setChecked(specify_week.get("enabled", False))
        self.specify_week_checkbox.blockSignals(False)
        week_enabled = specify_week.get("enabled", False)
        week_days_list = specify_week.get("days", [])
        for i, cb in enumerate(self.week_checkboxes):
            cb.setEnabled(week_enabled)
            cb.blockSignals(True)
            cb.setChecked(i in week_days_list)
            cb.blockSignals(False)
        
        specify_date = play_control.get("specify_date", {})
        self.specify_date_checkbox.blockSignals(True)
        self.specify_date_checkbox.setChecked(specify_date.get("enabled", False))
        self.specify_date_checkbox.blockSignals(False)
        self.specified_start_date.setEnabled(specify_date.get("enabled", False))
        self.specified_end_date.setEnabled(specify_date.get("enabled", False))
        start_date_str = specify_date.get("start_date", "")
        end_date_str = specify_date.get("end_date", "")
        if start_date_str:
            start_date = QDate.fromString(start_date_str, "yyyy-MM-dd")
            if start_date.isValid():
                self.specified_start_date.setDate(start_date)
        if end_date_str:
            end_date = QDate.fromString(end_date_str, "yyyy-MM-dd")
            if end_date.isValid():
                self.specified_end_date.setDate(end_date)
    
    def _update_video_properties(self):
        """Update video properties from current element"""
        if not self.current_element:
            return
        
        self.video_x_spin.setValue(self.current_element.get("x", 0))
        self.video_y_spin.setValue(self.current_element.get("y", 0))
        self.video_width_spin.setValue(self.current_element.get("width", 100))
        self.video_height_spin.setValue(self.current_element.get("height", 100))
        
        element_props = self.current_element.get("properties", {})
        frame_style = element_props.get("frame", "---")
        frame_index = self.video_frame_combo.findText(frame_style)
        if frame_index >= 0:
            self.video_frame_combo.setCurrentIndex(frame_index)
        
        transparency = element_props.get("transparency", 100)
        self.video_transparency_slider.setValue(transparency)
        self.video_transparency_label.setText(f"{transparency}%")
        
        video_list = element_props.get("video_list", [])
        self.video_list.clear()
        for video in video_list:
            item = QListWidgetItem(video.get("path", "Unknown"))
            self.video_list.addItem(item)
        
        video_shot = element_props.get("video_shot", {})
        self.video_shot_width_spin.setValue(video_shot.get("width", 100))
        self.video_shot_height_spin.setValue(video_shot.get("height", 100))
        
        start_time_str = video_shot.get("start_time", "00:00:00")
        time_parts = start_time_str.split(":")
        if len(time_parts) == 3:
            self.video_shot_start_time.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2])))
        
        end_time_str = video_shot.get("end_time", "00:00:30")
        time_parts = end_time_str.split(":")
        if len(time_parts) == 3:
            self.video_shot_end_time.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2])))
        
        self._update_duration()
    
    def _update_duration(self):
        """Update duration label based on start and end time"""
        start = self.video_shot_start_time.time()
        end = self.video_shot_end_time.time()
        start_secs = start.hour() * 3600 + start.minute() * 60 + start.second()
        end_secs = end.hour() * 3600 + end.minute() * 60 + end.second()
        duration_secs = max(0, end_secs - start_secs)
        hours = duration_secs // 3600
        minutes = (duration_secs % 3600) // 60
        seconds = duration_secs % 60
        self.video_shot_duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def _on_frame_enabled_changed(self, checked):
        """Handle frame checkbox toggle"""
        self.frame_combo.setEnabled(checked)
        if self.current_program:
            if "frame" not in self.current_program.properties:
                self.current_program.properties["frame"] = {}
            self.current_program.properties["frame"]["enabled"] = checked
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("frame_enabled", checked)
            self._trigger_autosave()
    
    def _on_frame_changed(self, text):
        """Handle frame selection change"""
        if self.current_program:
            if "frame" not in self.current_program.properties:
                self.current_program.properties["frame"] = {}
            self.current_program.properties["frame"]["style"] = text
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("frame_style", text)
            self._trigger_autosave()
    
    def _on_bg_music_enabled_changed(self, checked):
        """Handle background music checkbox toggle"""
        self.bg_music_combo.setEnabled(checked)
        self.bg_music_browse_btn.setEnabled(checked)
        if self.current_program:
            if "background_music" not in self.current_program.properties:
                self.current_program.properties["background_music"] = {}
            self.current_program.properties["background_music"]["enabled"] = checked
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("background_music_enabled", checked)
            self._trigger_autosave()
    
    def _on_bg_music_changed(self, text):
        """Handle background music file change"""
        if self.current_program:
            if "background_music" not in self.current_program.properties:
                self.current_program.properties["background_music"] = {}
            self.current_program.properties["background_music"]["file"] = text
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("background_music_file", text)
            self._trigger_autosave()
    
    def _on_browse_bg_music(self):
        """Handle browse music button"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Music", "",
            "Audio Files (*.mp3 *.wav *.ogg *.m4a *.aac);;All Files (*)"
        )
        if file_path:
            self.bg_music_combo.setCurrentText(file_path)
            if self.current_program:
                if "background_music" not in self.current_program.properties:
                    self.current_program.properties["background_music"] = {}
                self.current_program.properties["background_music"]["file"] = file_path
                self.current_program.modified = datetime.now().isoformat()
                self.property_changed.emit("background_music_file", file_path)
                self._trigger_autosave()
    
    def _on_play_mode_changed(self, checked):
        """Handle play mode radio button change"""
        if not checked:
            return
        
        if self.play_times_radio.isChecked():
            self.play_times_spin.setEnabled(True)
            self.fixed_length_time.setEnabled(False)
        elif self.fixed_length_radio.isChecked():
            self.play_times_spin.setEnabled(False)
            self.fixed_length_time.setEnabled(True)
        
        if self.current_program:
            if self.play_times_radio.isChecked():
                self.current_program.play_mode["mode"] = "play_times"
            elif self.fixed_length_radio.isChecked():
                self.current_program.play_mode["mode"] = "fixed_length"
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("play_mode", self.current_program.play_mode["mode"])
            self._trigger_autosave()
    
    def _on_play_times_changed(self, value):
        """Handle play times change"""
        if self.current_program:
            self.current_program.play_mode["play_times"] = value
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("play_times", value)
            self._trigger_autosave()
    
    def _on_fixed_length_changed(self, time):
        """Handle fixed length change"""
        if self.current_program:
            time_str = time.toString("HH:mm:ss")
            self.current_program.play_mode["fixed_length"] = time_str
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("fixed_length", time_str)
            self._trigger_autosave()
    
    def _on_specified_time_enabled_changed(self, checked):
        """Handle specified time checkbox toggle"""
        self.specified_start_time.setEnabled(checked)
        self.specified_end_time.setEnabled(checked)
        if self.current_program:
            if "specified_time" not in self.current_program.play_control:
                self.current_program.play_control["specified_time"] = {}
            self.current_program.play_control["specified_time"]["enabled"] = checked
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specified_time_enabled", checked)
            self._trigger_autosave()
    
    def _on_specified_time_changed(self, time):
        """Handle specified time change"""
        if self.current_program:
            if "specified_time" not in self.current_program.play_control:
                self.current_program.play_control["specified_time"] = {}
            start_time_str = self.specified_start_time.time().toString("HH:mm:ss")
            end_time_str = self.specified_end_time.time().toString("HH:mm:ss")
            self.current_program.play_control["specified_time"]["start_time"] = start_time_str
            self.current_program.play_control["specified_time"]["end_time"] = end_time_str
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specified_time_range", {"start": start_time_str, "end": end_time_str})
            self._trigger_autosave()
    
    def _on_specify_week_enabled_changed(self, checked):
        """Handle specify week checkbox toggle"""
        for cb in self.week_checkboxes:
            cb.setEnabled(checked)
        if self.current_program:
            if "specify_week" not in self.current_program.play_control:
                self.current_program.play_control["specify_week"] = {}
            self.current_program.play_control["specify_week"]["enabled"] = checked
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specify_week_enabled", checked)
            self._trigger_autosave()
    
    def _on_week_day_changed(self, checked):
        """Handle week day checkbox change"""
        if self.current_program:
            days = [i for i, cb in enumerate(self.week_checkboxes) if cb.isChecked()]
            if "specify_week" not in self.current_program.play_control:
                self.current_program.play_control["specify_week"] = {}
            self.current_program.play_control["specify_week"]["days"] = days
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specify_week_days", days)
            self._trigger_autosave()
    
    def _on_specify_date_enabled_changed(self, checked):
        """Handle specify date checkbox toggle"""
        self.specified_start_date.setEnabled(checked)
        self.specified_end_date.setEnabled(checked)
        if self.current_program:
            if "specify_date" not in self.current_program.play_control:
                self.current_program.play_control["specify_date"] = {}
            self.current_program.play_control["specify_date"]["enabled"] = checked
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specify_date_enabled", checked)
            self._trigger_autosave()
    
    def _on_specified_date_changed(self, date):
        """Handle specified date change"""
        if self.current_program:
            if "specify_date" not in self.current_program.play_control:
                self.current_program.play_control["specify_date"] = {}
            start_date_str = self.specified_start_date.date().toString("yyyy-MM-dd")
            end_date_str = self.specified_end_date.date().toString("yyyy-MM-dd")
            self.current_program.play_control["specify_date"]["start_date"] = start_date_str
            self.current_program.play_control["specify_date"]["end_date"] = end_date_str
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specify_date_range", {"start": start_date_str, "end": end_date_str})
            self._trigger_autosave()
    
    def _on_video_position_changed(self):
        """Handle video position change"""
        if self.current_element:
            self.current_element["x"] = self.video_x_spin.value()
            self.current_element["y"] = self.video_y_spin.value()
            self.property_changed.emit("video_position", (self.video_x_spin.value(), self.video_y_spin.value()))
    
    def _on_video_size_changed(self):
        """Handle video size change"""
        if self.current_element:
            self.current_element["width"] = self.video_width_spin.value()
            self.current_element["height"] = self.video_height_spin.value()
            self.property_changed.emit("video_size", (self.video_width_spin.value(), self.video_height_spin.value()))
    
    def _on_video_frame_changed(self, text):
        """Handle video frame change"""
        if self.current_element:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["frame"] = text
            self.property_changed.emit("video_frame", text)
    
    def _on_video_transparency_changed(self, value):
        """Handle video transparency change"""
        self.video_transparency_label.setText(f"{value}%")
        if self.current_element:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            self.current_element["properties"]["transparency"] = value
            self.property_changed.emit("video_transparency", value)
    
    def _on_video_add(self):
        """Handle video add button"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        if file_path:
            if self.current_element:
                if "properties" not in self.current_element:
                    self.current_element["properties"] = {}
                if "video_list" not in self.current_element["properties"]:
                    self.current_element["properties"]["video_list"] = []
                self.current_element["properties"]["video_list"].append({"path": file_path})
                item = QListWidgetItem(Path(file_path).name)
                self.video_list.addItem(item)
                self.property_changed.emit("video_list", self.current_element["properties"]["video_list"])
    
    def _on_video_delete(self):
        """Handle video delete button"""
        current_row = self.video_list.currentRow()
        if current_row >= 0 and self.current_element:
            if "properties" in self.current_element and "video_list" in self.current_element["properties"]:
                self.current_element["properties"]["video_list"].pop(current_row)
                self.video_list.takeItem(current_row)
                self.property_changed.emit("video_list", self.current_element["properties"]["video_list"])
    
    def _on_video_up(self):
        """Handle video up button"""
        current_row = self.video_list.currentRow()
        if current_row > 0 and self.current_element:
            if "properties" in self.current_element and "video_list" in self.current_element["properties"]:
                video_list = self.current_element["properties"]["video_list"]
                video_list[current_row], video_list[current_row - 1] = video_list[current_row - 1], video_list[current_row]
                item = self.video_list.takeItem(current_row)
                self.video_list.insertItem(current_row - 1, item)
                self.video_list.setCurrentRow(current_row - 1)
                self.property_changed.emit("video_list", video_list)
    
    def _on_video_down(self):
        """Handle video down button"""
        current_row = self.video_list.currentRow()
        if self.current_element and "properties" in self.current_element and "video_list" in self.current_element["properties"]:
            video_list = self.current_element["properties"]["video_list"]
            if 0 <= current_row < len(video_list) - 1:
                video_list[current_row], video_list[current_row + 1] = video_list[current_row + 1], video_list[current_row]
                item = self.video_list.takeItem(current_row)
                self.video_list.insertItem(current_row + 1, item)
                self.video_list.setCurrentRow(current_row + 1)
                self.property_changed.emit("video_list", video_list)
    
    def _on_video_shot_size_changed(self):
        """Handle video shot size change with aspect ratio"""
        if not self.current_element:
            return
        
        width = self.video_shot_width_spin.value()
        height = self.video_shot_height_spin.value()
        
        if "properties" not in self.current_element:
            self.current_element["properties"] = {}
        if "video_shot" not in self.current_element["properties"]:
            self.current_element["properties"]["video_shot"] = {}
        
        self.current_element["properties"]["video_shot"]["width"] = width
        self.current_element["properties"]["video_shot"]["height"] = height
        self.property_changed.emit("video_shot_size", (width, height))
    
    def _on_video_shot_time_changed(self):
        """Handle video shot time change"""
        if self.current_element:
            if "properties" not in self.current_element:
                self.current_element["properties"] = {}
            if "video_shot" not in self.current_element["properties"]:
                self.current_element["properties"]["video_shot"] = {}
            
            start_str = self.video_shot_start_time.time().toString("HH:mm:ss")
            end_str = self.video_shot_end_time.time().toString("HH:mm:ss")
            
            self.current_element["properties"]["video_shot"]["start_time"] = start_str
            self.current_element["properties"]["video_shot"]["end_time"] = end_str
            
            self._update_duration()
    
    def _update_screen_properties(self, program_manager: Optional[ProgramManager] = None):
        """Update screen properties from current screen"""
        if not self.current_screen_name or not self.current_screen_programs:
            return
        
        first_program = self.current_screen_programs[0] if self.current_screen_programs else None
        if not first_program:
            return
        
        screen_props = first_program.properties.get("screen", {})
        
        controller_type = screen_props.get("controller_type", "")
        if not controller_type:
            brand = screen_props.get("brand", "")
            model = screen_props.get("model", "")
            if brand and model:
                controller_type = f"{brand} {model}"
            elif model:
                controller_type = model
        self.screen_controller_type_input.setText(controller_type if controller_type else "N/A")
        
        # NEVER use program.width/height (PC canvas) - only use screen_properties (controller screen)
        screen_props = first_program.properties.get("screen", {})
        width = screen_props.get("width")
        height = screen_props.get("height")
        if width and height:
            self.screen_size_input.setText(f"{width} x {height}")
        else:
            self.screen_size_input.setText("Not set")
        
        working_file_path = first_program.properties.get("working_file_path", "")
        if working_file_path:
            self.screen_path_input.setText(working_file_path)
        else:
            if program_manager:
                from utils.app_data import get_app_data_dir
                work_dir = get_app_data_dir() / "work"
                safe_name = self.current_screen_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
                soo_file = work_dir / f"{safe_name}.soo"
                if soo_file.exists():
                    self.screen_path_input.setText(str(soo_file))
                else:
                    self.screen_path_input.setText(str(soo_file))
            else:
                self.screen_path_input.setText("N/A")
        
        self.related_equipment_table.setRowCount(0)
