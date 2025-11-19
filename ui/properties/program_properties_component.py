"""
Program properties component
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox,
                             QCheckBox, QComboBox, QMenu, QAction)
from PyQt5.QtCore import Qt
from datetime import datetime
from ui.properties.base_properties_component import BasePropertiesComponent
from ui.widgets.time_range_multiselector import TimeRangeMultiSelector
from ui.widgets.date_range_multiselector import DateRangeMultiSelector


class ProgramPropertiesComponent(BasePropertiesComponent):
    """Program properties component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating_properties = False  # Flag to prevent recursive updates
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignTop)  # align-items: top
        
        # Set minimum height for the component
        self.setMinimumHeight(100)
        
        # Specified time section
        specified_time_layout = QVBoxLayout()
        specified_time_layout.setContentsMargins(0, 0, 0, 0)
        specified_time_layout.setSpacing(4)
        specified_time_layout.setAlignment(Qt.AlignTop)  # flex-start alignment
        
        self.specified_time_checkbox = QCheckBox("Specified time")
        self.specified_time_checkbox.toggled.connect(self._on_specified_time_enabled_changed)
        specified_time_layout.addWidget(self.specified_time_checkbox, alignment=Qt.AlignTop)
        
        # Use TimeRangeMultiSelector component
        self.time_range_selector = TimeRangeMultiSelector()
        self.time_range_selector.setEnabled(False)
        self.time_range_selector.time_ranges_changed.connect(self._on_time_ranges_changed)
        specified_time_layout.addWidget(self.time_range_selector, alignment=Qt.AlignTop)
        
        # Wrap specified time in a widget for better horizontal layout
        specified_time_widget = QWidget()
        specified_time_widget.setLayout(specified_time_layout)
        layout.addWidget(specified_time_widget, stretch=1, alignment=Qt.AlignTop)
        
        # Specify week section
        specify_week_layout = QVBoxLayout()
        specify_week_layout.setContentsMargins(0, 0, 0, 0)
        specify_week_layout.setSpacing(4)
        specify_week_layout.setAlignment(Qt.AlignTop)
        self.specify_week_checkbox = QCheckBox("Specify the week")
        self.specify_week_checkbox.toggled.connect(self._on_specify_week_enabled_changed)
        specify_week_layout.addWidget(self.specify_week_checkbox, alignment=Qt.AlignTop)
        
        # Single selector for week days
        week_selector_layout = QHBoxLayout()
        week_selector_layout.setContentsMargins(20, 0, 0, 0)
        
        self.week_days_selector = QPushButton("Select days...")
        self.week_days_selector.setEnabled(False)
        self.week_days_selector.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #FFFFFF;
                min-height: 32px;
            }
            QPushButton:hover {
                border: 1px solid #4A90E2;
                background-color: #F5F5F5;
            }
            QPushButton:pressed {
                background-color: #E3F2FD;
            }
            QPushButton:disabled {
                background-color: #F5F5F5;
                color: #999999;
            }
        """)
        self.week_days_selector.clicked.connect(self._show_week_days_menu)
        week_selector_layout.addWidget(self.week_days_selector, stretch=1)
        
        self.week_checkboxes = []
        self.week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.selected_week_days = []
        
        specify_week_layout.addLayout(week_selector_layout)
        
        # Wrap specify week in a widget for better horizontal layout
        specify_week_widget = QWidget()
        specify_week_widget.setLayout(specify_week_layout)
        layout.addWidget(specify_week_widget, stretch=1, alignment=Qt.AlignTop)
        
        # Specify date section
        specify_date_layout = QVBoxLayout()
        specify_date_layout.setContentsMargins(0, 0, 0, 0)
        specify_date_layout.setSpacing(4)
        specify_date_layout.setAlignment(Qt.AlignTop)
        self.specify_date_checkbox = QCheckBox("Specify the date")
        self.specify_date_checkbox.toggled.connect(self._on_specify_date_enabled_changed)
        specify_date_layout.addWidget(self.specify_date_checkbox, alignment=Qt.AlignTop)
        
        # Use DateRangeMultiSelector component
        self.date_range_selector = DateRangeMultiSelector()
        self.date_range_selector.setEnabled(False)
        self.date_range_selector.date_ranges_changed.connect(self._on_date_ranges_changed)
        specify_date_layout.addWidget(self.date_range_selector, alignment=Qt.AlignTop)
        
        # Wrap specify date in a widget for better horizontal layout
        specify_date_widget = QWidget()
        specify_date_widget.setLayout(specify_date_layout)
        layout.addWidget(specify_date_widget, stretch=1, alignment=Qt.AlignTop)
    
    def set_program_data(self, program):
        """Set program data and update properties display"""
        self.current_program = program
        self.update_properties()
    
    def update_properties(self):
        """Update program properties from current program"""
        if not self.current_program or self._updating_properties:
            return
        
        self._updating_properties = True
        try:
            play_control = self.current_program.play_control
        
            # Load specified time ranges
            specified_time = play_control.get("specified_time", {})
            self.specified_time_checkbox.blockSignals(True)
            self.specified_time_checkbox.setChecked(specified_time.get("enabled", False))
            self.specified_time_checkbox.setEnabled(True)  # Ensure checkbox is enabled
            self.specified_time_checkbox.blockSignals(False)
            
            time_ranges = specified_time.get("ranges", [])
            if not time_ranges and specified_time.get("enabled", False):
                # Migrate old single range format to new list format
                start_time_str = specified_time.get("start_time", "00:00:00")
                end_time_str = specified_time.get("end_time", "23:59:59")
                if start_time_str and end_time_str:
                    time_ranges = [{"start": start_time_str, "end": end_time_str}]
            
            # Set all time ranges in the selector (all selected by default for backward compatibility)
            self.time_range_selector.set_time_ranges(time_ranges, selected_indices=list(range(len(time_ranges))))
            
            enabled = specified_time.get("enabled", False)
            self.time_range_selector.set_enabled(enabled)
            
            # Load specify week
            specify_week = play_control.get("specify_week", {})
            self.specify_week_checkbox.blockSignals(True)
            self.specify_week_checkbox.setChecked(specify_week.get("enabled", False))
            self.specify_week_checkbox.setEnabled(True)  # Ensure checkbox is enabled
            self.specify_week_checkbox.blockSignals(False)
            week_enabled = specify_week.get("enabled", False)
            week_days_list = specify_week.get("days", [])
            self.selected_week_days = week_days_list
            self._update_week_selector_text()
            self.week_days_selector.setEnabled(week_enabled)
            
            # Load specify date ranges
            specify_date = play_control.get("specify_date", {})
            self.specify_date_checkbox.blockSignals(True)
            self.specify_date_checkbox.setChecked(specify_date.get("enabled", False))
            self.specify_date_checkbox.setEnabled(True)  # Ensure checkbox is enabled
            self.specify_date_checkbox.blockSignals(False)
            
            date_ranges = specify_date.get("ranges", [])
            if not date_ranges and specify_date.get("enabled", False):
                # Migrate old single range format to new list format
                start_date_str = specify_date.get("start_date", "")
                end_date_str = specify_date.get("end_date", "")
                if start_date_str and end_date_str:
                    date_ranges = [{"start": start_date_str, "end": end_date_str}]
            
            # Set all date ranges in the selector (all selected by default for backward compatibility)
            self.date_range_selector.set_date_ranges(date_ranges, selected_indices=list(range(len(date_ranges))))
            
            enabled = specify_date.get("enabled", False)
            self.date_range_selector.set_enabled(enabled)
        finally:
            self._updating_properties = False
    
    def _on_specified_time_enabled_changed(self, checked):
        """Handle specified time checkbox toggle"""
        if not self.current_program:
            # Disable checkbox if no program
            self.specified_time_checkbox.blockSignals(True)
            self.specified_time_checkbox.setEnabled(False)
            self.specified_time_checkbox.setChecked(False)
            self.specified_time_checkbox.blockSignals(False)
            return
        
        # Ensure checkbox is enabled when we have program
        self.specified_time_checkbox.setEnabled(True)
        self.time_range_selector.set_enabled(checked)
        
        if self.current_program:
            if "specified_time" not in self.current_program.play_control:
                self.current_program.play_control["specified_time"] = {}
            self.current_program.play_control["specified_time"]["enabled"] = checked
            if not checked:
                # Clear ranges when disabled
                self.current_program.play_control["specified_time"]["ranges"] = []
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specified_time_enabled", checked)
            self._trigger_autosave()
    
    def _on_time_ranges_changed(self, selected_ranges):
        """Handle time ranges change from TimeRangeMultiSelector"""
        if not self.current_program or self._updating_properties:
            return
        
            if "specified_time" not in self.current_program.play_control:
                self.current_program.play_control["specified_time"] = {}
        
        # Save all time ranges (not just selected ones)
        all_ranges = self.time_range_selector.get_all_time_ranges()
        
        # Only update if values actually changed to prevent feedback loops
        current_ranges = self.current_program.play_control["specified_time"].get("ranges", [])
        if all_ranges != current_ranges:
            self.current_program.play_control["specified_time"]["ranges"] = all_ranges
        
        # Also save selected ranges separately if needed
        self.current_program.play_control["specified_time"]["selected_ranges"] = selected_ranges
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("specified_time_ranges", all_ranges)
        self._trigger_autosave()
    
    def _on_specify_week_enabled_changed(self, checked):
        """Handle specify week checkbox toggle"""
        if not self.current_program:
            # Disable checkbox if no program
            self.specify_week_checkbox.blockSignals(True)
            self.specify_week_checkbox.setEnabled(False)
            self.specify_week_checkbox.setChecked(False)
            self.specify_week_checkbox.blockSignals(False)
            return
        
        # Ensure checkbox is enabled when we have program
        self.specify_week_checkbox.setEnabled(True)
        self.week_days_selector.setEnabled(checked)
        if self.current_program:
            if "specify_week" not in self.current_program.play_control:
                self.current_program.play_control["specify_week"] = {}
            self.current_program.play_control["specify_week"]["enabled"] = checked
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specify_week_enabled", checked)
            self._trigger_autosave()
    
    def _show_week_days_menu(self):
        """Show menu for selecting week days"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px 6px 30px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
            }
        """)
        
        for i, day in enumerate(self.week_days):
            action = QAction(day, menu)
            action.setCheckable(True)
            action.setChecked(i in self.selected_week_days)
            action.triggered.connect(lambda checked, idx=i: self._on_week_day_toggled(idx, checked))
            menu.addAction(action)
        
        # Show menu below the button
        button_pos = self.week_days_selector.mapToGlobal(self.week_days_selector.rect().bottomLeft())
        menu.exec_(button_pos)
    
    def _on_week_day_toggled(self, day_index, checked):
        """Handle week day toggle in menu"""
        if checked:
            if day_index not in self.selected_week_days:
                self.selected_week_days.append(day_index)
        else:
            if day_index in self.selected_week_days:
                self.selected_week_days.remove(day_index)
        
        self._update_week_selector_text()
        self._save_week_days()
    
    def _update_week_selector_text(self):
        """Update the selector button text based on selected days"""
        if not self.selected_week_days:
            self.week_days_selector.setText("Select days...")
        else:
            selected_names = [self.week_days[i] for i in sorted(self.selected_week_days)]
            if len(selected_names) <= 3:
                text = ", ".join(selected_names)
            else:
                text = f"{len(selected_names)} days selected"
            self.week_days_selector.setText(text)
    
    def _save_week_days(self):
        """Save selected week days to program"""
        if self.current_program:
            if "specify_week" not in self.current_program.play_control:
                self.current_program.play_control["specify_week"] = {}
            self.current_program.play_control["specify_week"]["days"] = sorted(self.selected_week_days)
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specify_week_days", sorted(self.selected_week_days))
            self._trigger_autosave()
    
    def _on_specify_date_enabled_changed(self, checked):
        """Handle specify date checkbox toggle"""
        if not self.current_program:
            # Disable checkbox if no program
            self.specify_date_checkbox.blockSignals(True)
            self.specify_date_checkbox.setEnabled(False)
            self.specify_date_checkbox.setChecked(False)
            self.specify_date_checkbox.blockSignals(False)
            return
        
        # Ensure checkbox is enabled when we have program
        self.specify_date_checkbox.setEnabled(True)
        self.date_range_selector.set_enabled(checked)
        
        if self.current_program:
            if "specify_date" not in self.current_program.play_control:
                self.current_program.play_control["specify_date"] = {}
            self.current_program.play_control["specify_date"]["enabled"] = checked
            if not checked:
                # Clear ranges when disabled
                self.current_program.play_control["specify_date"]["ranges"] = []
            self.current_program.modified = datetime.now().isoformat()
            self.property_changed.emit("specify_date_enabled", checked)
            self._trigger_autosave()
    
    def _on_date_ranges_changed(self, selected_ranges):
        """Handle date ranges change from DateRangeMultiSelector"""
        if not self.current_program or self._updating_properties:
            return
        
            if "specify_date" not in self.current_program.play_control:
                self.current_program.play_control["specify_date"] = {}
        
        # Save all date ranges (not just selected ones)
        all_ranges = self.date_range_selector.get_all_date_ranges()
        
        # Only update if values actually changed to prevent feedback loops
        current_ranges = self.current_program.play_control["specify_date"].get("ranges", [])
        if all_ranges != current_ranges:
            self.current_program.play_control["specify_date"]["ranges"] = all_ranges
        
        # Also save selected ranges separately if needed
        self.current_program.play_control["specify_date"]["selected_ranges"] = selected_ranges
        
        self.current_program.modified = datetime.now().isoformat()
        self.property_changed.emit("specify_date_ranges", all_ranges)
        self._trigger_autosave()
