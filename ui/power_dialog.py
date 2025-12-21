from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QTimeEdit,
    QMessageBox
)
from PyQt5.QtCore import Qt, QTime, pyqtSignal
from typing import Optional, Dict, Any, List
from controllers.huidu import HuiduController
from utils.logger import get_logger

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
    QTimeEdit {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QTimeEdit:hover {
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


class PowerDialog(QDialog):
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, controller=None, screen_name: Optional[str] = None):
        super().__init__(parent)
        self.controller = controller
        self.screen_name = screen_name
        self.controller_id = None
        if controller:
            try:
                self.controller_id = controller.get('controller_id') if isinstance(controller, dict) else (controller.get_controller_id() if hasattr(controller, 'get_controller_id') else None)
            except:
                pass
        
        self.setWindowTitle(f"⚡ Power Schedule" + (f" - {screen_name}" if screen_name else ""))
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.power_schedules: List[Dict[str, Any]] = []
        self.huidu_controller = HuiduController()
        
        self.init_ui()
        self.load_from_device()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        schedule_group = QGroupBox("On/Off Schedule")
        schedule_layout = QVBoxLayout(schedule_group)
        
        self.enable_schedule_check = QCheckBox("Enable Power Schedule")
        self.enable_schedule_check.setChecked(True)
        schedule_layout.addWidget(self.enable_schedule_check)
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["Day", "On Time", "Off Time", "Enabled"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.schedule_table.verticalHeader().setVisible(False)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.schedule_table.setRowCount(len(days))
        
        for i, day in enumerate(days):
            day_item = QTableWidgetItem(day)
            day_item.setFlags(day_item.flags() & ~Qt.ItemIsEditable)
            self.schedule_table.setItem(i, 0, day_item)
            
            on_time = QTimeEdit()
            on_time.setTime(QTime(8, 0))
            on_time.setDisplayFormat("HH:mm")
            self.schedule_table.setCellWidget(i, 1, on_time)
            
            off_time = QTimeEdit()
            off_time.setTime(QTime(22, 0))
            off_time.setDisplayFormat("HH:mm")
            self.schedule_table.setCellWidget(i, 2, off_time)
            
            enabled_check = QCheckBox()
            enabled_check.setChecked(True)
            self.schedule_table.setCellWidget(i, 3, enabled_check)
        
        schedule_layout.addWidget(self.schedule_table)
        
        layout.addWidget(schedule_group)
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save & Send")
        save_btn.clicked.connect(self.save_and_send)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_power_schedule(self) -> List[Dict]:
        schedule = []
        for i in range(self.schedule_table.rowCount()):
            day_item = self.schedule_table.item(i, 0)
            if not day_item:
                continue
            
            day = day_item.text()
            on_time_widget = self.schedule_table.cellWidget(i, 1)
            off_time_widget = self.schedule_table.cellWidget(i, 2)
            enabled_widget = self.schedule_table.cellWidget(i, 3)
            
            if on_time_widget and off_time_widget and enabled_widget:
                on_time = on_time_widget.time().toString("HH:mm")
                off_time = off_time_widget.time().toString("HH:mm")
                enabled = enabled_widget.isChecked()
                
                schedule.append({
                    "day": day,
                    "on_time": on_time,
                    "off_time": off_time,
                    "enabled": enabled
                })
        
        return schedule
    
    def load_power_schedule(self, schedule):
        try:
            if not schedule:
                return
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_map = {day.lower(): day for day in days}
            
            if isinstance(schedule, list):
                for day_schedule in schedule:
                    day_name = day_schedule.get("day", "")
                    day_key = day_name.lower()
                    
                    if day_key in day_map:
                        day_index = days.index(day_map[day_key])
                        if day_index < self.schedule_table.rowCount():
                            on_time_str = day_schedule.get("on_time", "08:00")
                            off_time_str = day_schedule.get("off_time", "22:00")
                            enabled = day_schedule.get("enabled", True)
                            
                            on_hour, on_min = map(int, on_time_str.split(':'))
                            off_hour, off_min = map(int, off_time_str.split(':'))
                            
                            on_time_widget = self.schedule_table.cellWidget(day_index, 1)
                            off_time_widget = self.schedule_table.cellWidget(day_index, 2)
                            enabled_widget = self.schedule_table.cellWidget(day_index, 3)
                            
                            if on_time_widget:
                                on_time_widget.setTime(QTime(on_hour, on_min))
                            if off_time_widget:
                                off_time_widget.setTime(QTime(off_hour, off_min))
                            if enabled_widget:
                                enabled_widget.setChecked(enabled)
        except Exception as e:
            logger.error(f"Error loading power schedule: {e}", exc_info=True)
    
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            response = self.huidu_controller.get_period_task([self.controller_id])
            
            if response.get("message") == "ok" and response.get("data"):
                period_tasks = response.get("data", [])
                if period_tasks and len(period_tasks) > 0:
                    task_data = period_tasks[0].get("data", [])
                    if task_data:
                        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        for task in task_data:
                            day_index = task.get("day", 0)
                            if 0 <= day_index < len(days):
                                on_time_str = task.get("onTime", "08:00")
                                off_time_str = task.get("offTime", "22:00")
                                enabled = task.get("enabled", True)
                                
                                on_hour, on_min = map(int, on_time_str.split(':'))
                                off_hour, off_min = map(int, off_time_str.split(':'))
                                
                                on_time_widget = self.schedule_table.cellWidget(day_index, 1)
                                off_time_widget = self.schedule_table.cellWidget(day_index, 2)
                                enabled_widget = self.schedule_table.cellWidget(day_index, 3)
                                
                                if on_time_widget:
                                    on_time_widget.setTime(QTime(on_hour, on_min))
                                if off_time_widget:
                                    off_time_widget.setTime(QTime(off_hour, off_min))
                                if enabled_widget:
                                    enabled_widget.setChecked(enabled)
                        
                        logger.info(f"Loaded power schedule from device")
        except Exception as e:
            logger.error(f"Error loading power schedule from device: {e}", exc_info=True)
    
    def save_and_send(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            schedule = self.get_power_schedule()
            
            period_tasks = []
            days_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
            
            for day_schedule in schedule:
                if day_schedule.get("enabled", False):
                    day_name = day_schedule.get("day", "")
                    day_index = days_map.get(day_name, -1)
                    if day_index >= 0:
                        period_tasks.append({
                            "day": day_index,
                            "onTime": day_schedule.get("on_time", "08:00"),
                            "offTime": day_schedule.get("off_time", "22:00"),
                            "enabled": True
                        })
            
            response = self.huidu_controller.set_period_task([self.controller_id], period_tasks)
            
            if response.get("message") == "ok":
                QMessageBox.information(self, "Success", "Power schedule saved and sent to controller.")
                self.settings_changed.emit({"power_schedule": schedule})
                self.accept()
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Failed", f"Failed to save power schedule: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")

