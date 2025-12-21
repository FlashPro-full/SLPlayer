from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QTimeEdit, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTime, QDate, pyqtSignal
from PyQt5.QtGui import QColor
from typing import Optional, Dict, Any, List
from core.screen_manager import ScreenManager
from utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

TABLE_STYLE = """
    QTableWidget {
        background-color: #2B2B2B;
        border: 1px solid #555555;
        color: #FFFFFF;
        gridline-color: #555555;
    }
    QTableWidget::item {
        color: #FFFFFF;
        border-bottom: 1px solid #555555;
    }
    QTableWidget::item:hover {
        background-color: #2A60B2;
        border: 1px solid #4A90E2;
        outline: none;
    }
    QTableWidget::item:selected {
        background-color: #2A60B2;
        border: 1px solid #4A90E2;
        outline: none;
    }
    QTableWidget::item:selected:hover {
        background-color: #2A60B2;
        border: 1px solid #4A90E2;
        outline: none;
    }
    QHeaderView {
        background-color: #3B3B3B;
    }
    QHeaderView::section {
        background-color: #3B3B3B;
        color: #FFFFFF;
        padding: 8px;
        border: 1px solid #555555;
    }
    QTableWidget QHeaderView::section:horizontal {
        background-color: #3B3B3B;
        color: #FFFFFF;
        padding: 8px;
        border: 1px solid #555555;
        border-top: none;
    }
    QTableCornerButton::section {
        background-color: #3B3B3B;
        border: 1px solid #555555;
    }
"""

DIALOG_STYLE = """
    QDialog {
        background-color: #2B2B2B;
    }
    QLabel {
        color: #FFFFFF;
    }
    QPushButton {
        padding: 8px 20px;
        border: none;
        border-radius: 4px;
        font-size: 11pt;
        background-color: #4A90E2;
        color: #FFFFFF;
    }
    QPushButton:hover {
        background-color: #5AA0F2;
    }
    QPushButton:pressed {
        background-color: #3A80D2;
    }
    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }
    QGroupBox {
        border: 1px solid #555555;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        color: #FFFFFF;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: #FFFFFF;
    }
    QComboBox {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QComboBox:hover {
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
        border-top: 6px solid #FFFFFF;
        margin-right: 5px;
    }
    QComboBox QAbstractItemView {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        color: #FFFFFF;
        selection-background-color: #2A60B2;
    }
    QTimeEdit, QDateEdit {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QTimeEdit:hover, QDateEdit:hover {
        border: 1px solid #4A90E2;
    }
    QCheckBox {
        color: #FFFFFF;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #555555;
        background-color: #3B3B3B;
        border-radius: 3px;
    }
    QCheckBox::indicator:checked {
        background-color: #4A90E2;
        border: 1px solid #4A90E2;
    }
""" + TABLE_STYLE


class ScheduleDialog(QDialog):
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None, screen_manager: Optional[ScreenManager] = None):
        super().__init__(parent)
        self.screen_manager = screen_manager
        self.setWindowTitle("📅 Program Schedule")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.init_ui()
        self.load_programs()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        info_label = QLabel("Configure scheduling for each program. Programs will play according to their schedule settings.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.programs_table = QTableWidget()
        self.programs_table.setColumnCount(6)
        self.programs_table.setHorizontalHeaderLabels([
            "Screen", "Program", "Specified Time", "Week Days", "Specific Date", "Enabled"
        ])
        self.programs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.programs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.programs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.programs_table.verticalHeader().setVisible(False)
        self.programs_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        layout.addWidget(self.programs_table)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_schedules)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_programs(self):
        if not self.screen_manager:
            return
        
        programs_data = []
        for screen in self.screen_manager.screens:
            for program in screen.programs:
                programs_data.append({
                    'screen': screen,
                    'program': program,
                    'screen_name': screen.name,
                    'program_name': program.name,
                    'program_id': program.id
                })
        
        self.programs_table.setRowCount(len(programs_data))
        
        for row, data in enumerate(programs_data):
            program = data['program']
            play_control = program.play_control
            
            screen_item = QTableWidgetItem(data['screen_name'])
            screen_item.setFlags(screen_item.flags() & ~Qt.ItemIsEditable)
            self.programs_table.setItem(row, 0, screen_item)
            
            program_item = QTableWidgetItem(data['program_name'])
            program_item.setFlags(program_item.flags() & ~Qt.ItemIsEditable)
            self.programs_table.setItem(row, 1, program_item)
            
            specified_time = play_control.get("specified_time", {})
            time_enabled = specified_time.get("enabled", False)
            time_ranges = specified_time.get("ranges", [])
            time_text = ""
            if time_enabled and time_ranges:
                time_text = f"{len(time_ranges)} range(s)"
            elif time_enabled:
                start = specified_time.get("start_time", "")
                end = specified_time.get("end_time", "")
                if start and end:
                    time_text = f"{start} - {end}"
            time_item = QTableWidgetItem(time_text)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
            if time_enabled:
                time_item.setForeground(QColor(0, 255, 0))
            self.programs_table.setItem(row, 2, time_item)
            
            specify_week = play_control.get("specify_week", {})
            week_enabled = specify_week.get("enabled", False)
            week_days = specify_week.get("days", [])
            week_text = ""
            if week_enabled:
                day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                week_text = ", ".join([day_names[d] for d in week_days if 0 <= d < 7])
            week_item = QTableWidgetItem(week_text)
            week_item.setFlags(week_item.flags() & ~Qt.ItemIsEditable)
            if week_enabled:
                week_item.setForeground(QColor(0, 255, 0))
            self.programs_table.setItem(row, 3, week_item)
            
            specify_date = play_control.get("specify_date", {})
            date_enabled = specify_date.get("enabled", False)
            date_text = specify_date.get("date", "") if date_enabled else ""
            date_item = QTableWidgetItem(date_text)
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            if date_enabled:
                date_item.setForeground(QColor(0, 255, 0))
            self.programs_table.setItem(row, 4, date_item)
            
            enabled = (time_enabled or week_enabled or date_enabled)
            enabled_item = QTableWidgetItem("Yes" if enabled else "No")
            enabled_item.setFlags(enabled_item.flags() & ~Qt.ItemIsEditable)
            if enabled:
                enabled_item.setForeground(QColor(0, 255, 0))
            else:
                enabled_item.setForeground(QColor(255, 0, 0))
            self.programs_table.setItem(row, 5, enabled_item)
            
            self.programs_table.setRowHeight(row, 30)
    
    def on_cell_double_clicked(self, row: int, col: int):
        if not self.screen_manager:
            return
        
        screen_item = self.programs_table.item(row, 0)
        program_item = self.programs_table.item(row, 1)
        if not screen_item or not program_item:
            return
        
        screen_name = screen_item.text()
        program_name = program_item.text()
        
        screen = self.screen_manager.get_screen_by_name(screen_name)
        if not screen:
            return
        
        program = None
        for p in screen.programs:
            if p.name == program_name:
                program = p
                break
        
        if not program:
            return
        
        from ui.properties.program_properties_component import ProgramPropertiesComponent
        from PyQt5.QtWidgets import QDialog, QVBoxLayout
        
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle(f"Edit Schedule - {program_name}")
        edit_dialog.setMinimumWidth(600)
        edit_dialog.setMinimumHeight(500)
        edit_dialog.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout(edit_dialog)
        
        props_component = ProgramPropertiesComponent()
        props_component.set_program_data(program)
        props_component.set_screen_manager(self.screen_manager)
        layout.addWidget(props_component)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(edit_dialog.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
        
        if edit_dialog.exec():
            program.modified = datetime.now().isoformat()
            self.load_programs()
            self.settings_changed.emit()
    
    def save_schedules(self):
        if not self.screen_manager:
            return
        
        try:
            for screen in self.screen_manager.screens:
                for program in screen.programs:
                    program.modified = datetime.now().isoformat()
            
            QMessageBox.information(self, "Success", "Program schedules saved.")
            self.settings_changed.emit()
            self.accept()
        except Exception as e:
            logger.error(f"Error saving schedules: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving schedules: {str(e)}")

