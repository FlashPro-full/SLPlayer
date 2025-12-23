from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QTimeEdit,
    QMessageBox, QDateEdit, QLineEdit, QWidget
)
from PyQt5.QtCore import Qt, QTime, QDate, pyqtSignal
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
    QPushButton:checked {
        background-color: #2A7A2A;
    }
    QPushButton:checked:hover {
        background-color: #3A8A3A;
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
    QDateEdit {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QDateEdit:hover {
        border: 1px solid #4A90E2;
    }
    QLineEdit {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QLineEdit:hover {
        border: 1px solid #4A90E2;
    }
    QCheckBox {
        color: #FFFFFF;
    }
""" + TABLE_STYLE


class PowerDialog(QDialog):
    
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
        
        self.setWindowTitle(f"Power Schedule" + (f" - {screen_name}" if screen_name else ""))
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
        
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.power_toggle_btn = QPushButton("Turn On")
        self.power_toggle_btn.setFixedWidth(100)
        self.power_toggle_btn.setCheckable(True)
        self.power_toggle_btn.toggled.connect(self.toggle_power)
        header_layout.addWidget(self.power_toggle_btn)
        layout.addLayout(header_layout)
        
        schedule_group = QGroupBox("On/Off Schedule")
        schedule_layout = QVBoxLayout(schedule_group)
        
        self.enable_schedule_check = QCheckBox("Enable Power Schedule")
        self.enable_schedule_check.setChecked(True)
        schedule_layout.addWidget(self.enable_schedule_check)
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["Date Range", "Time Range", "Week Filter", "Enabled"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setRowCount(0)
        
        add_row_btn = QPushButton("+ Add Schedule")
        add_row_btn.clicked.connect(lambda: self.add_schedule_row())
        schedule_layout.addWidget(add_row_btn)
        
        schedule_layout.addWidget(self.schedule_table)
        
        layout.addWidget(schedule_group)
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("OK")
        save_btn.clicked.connect(self.save_and_send)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_schedule_row(self, date_range="", time_range="", week_filter="", enabled=True):
        row = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row)
        
        date_range_widget = QWidget()
        date_layout = QHBoxLayout(date_range_widget)
        date_layout.setContentsMargins(2, 2, 2, 2)
        date_layout.setSpacing(4)
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate())
        start_date.setDisplayFormat("yyyy-MM-dd")
        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate())
        end_date.setDisplayFormat("yyyy-MM-dd")
        if date_range:
            try:
                start_str, end_str = date_range.split("~")
                start_date.setDate(QDate.fromString(start_str.strip(), "yyyy-MM-dd"))
                end_date.setDate(QDate.fromString(end_str.strip(), "yyyy-MM-dd"))
            except:
                pass
        date_layout.addWidget(start_date)
        date_layout.addWidget(QLabel("~"))
        date_layout.addWidget(end_date)
        self.schedule_table.setCellWidget(row, 0, date_range_widget)
        
        time_range_widget = QWidget()
        time_layout = QHBoxLayout(time_range_widget)
        time_layout.setContentsMargins(2, 2, 2, 2)
        time_layout.setSpacing(4)
        start_time = QTimeEdit()
        start_time.setTime(QTime(0, 0))
        start_time.setDisplayFormat("HH:mm:ss")
        end_time = QTimeEdit()
        end_time.setTime(QTime(23, 59, 59))
        end_time.setDisplayFormat("HH:mm:ss")
        if time_range:
            try:
                start_str, end_str = time_range.split("~")
                start_parts = start_str.strip().split(":")
                end_parts = end_str.strip().split(":")
                if len(start_parts) >= 3:
                    start_time.setTime(QTime(int(start_parts[0]), int(start_parts[1]), int(start_parts[2])))
                if len(end_parts) >= 3:
                    end_time.setTime(QTime(int(end_parts[0]), int(end_parts[1]), int(end_parts[2])))
            except:
                pass
        time_layout.addWidget(start_time)
        time_layout.addWidget(QLabel("~"))
        time_layout.addWidget(end_time)
        self.schedule_table.setCellWidget(row, 1, time_range_widget)
        
        week_filter_edit = QLineEdit()
        week_filter_edit.setPlaceholderText("Mon, Tue, Wed, Thu, Fri, Sat, Sun")
        week_filter_edit.setText(week_filter)
        self.schedule_table.setCellWidget(row, 2, week_filter_edit)
        
        enabled_check = QCheckBox()
        enabled_check.setChecked(enabled)
        self.schedule_table.setCellWidget(row, 3, enabled_check)
        
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(lambda: self.remove_schedule_row(row))
        
        delete_layout = QHBoxLayout()
        delete_layout.setContentsMargins(2, 2, 2, 2)
        delete_layout.addWidget(enabled_check)
        delete_layout.addWidget(delete_btn)
        delete_widget = QWidget()
        delete_widget.setLayout(delete_layout)
        self.schedule_table.setCellWidget(row, 3, delete_widget)
    
    def remove_schedule_row(self, row: int):
        if row >= 0 and row < self.schedule_table.rowCount():
            self.schedule_table.removeRow(row)
    
    def get_power_schedule(self) -> List[Dict]:
        schedule = []
        for i in range(self.schedule_table.rowCount()):
            date_range_widget = self.schedule_table.cellWidget(i, 0)
            time_range_widget = self.schedule_table.cellWidget(i, 1)
            week_filter_widget = self.schedule_table.cellWidget(i, 2)
            enabled_widget = self.schedule_table.cellWidget(i, 3)
            
            if not (date_range_widget and time_range_widget and week_filter_widget and enabled_widget):
                continue
            
            start_date = date_range_widget.layout().itemAt(0).widget()
            end_date = date_range_widget.layout().itemAt(2).widget()
            start_time = time_range_widget.layout().itemAt(0).widget()
            end_time = time_range_widget.layout().itemAt(2).widget()
            
            if start_date and end_date and start_time and end_time:
                date_range = f"{start_date.date().toString('yyyy-MM-dd')}~{end_date.date().toString('yyyy-MM-dd')}"
                time_range = f"{start_time.time().toString('HH:mm:ss')}~{end_time.time().toString('HH:mm:ss')}"
                week_filter = week_filter_widget.text().strip()
                
                enabled_layout = enabled_widget.layout()
                enabled_check = enabled_layout.itemAt(0).widget() if enabled_layout else None
                enabled = enabled_check.isChecked() if enabled_check else False
                
                schedule.append({
                    "timeRange": time_range,
                    "dateRange": date_range,
                    "WeekFilter": week_filter,
                    "data": "true" if enabled else "false"
                })
        
        return schedule
     
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            response = self.huidu_controller.get_device_status([self.controller_id])
            if response.get("message") == "ok" and response.get("data"):
                data = response.get("data", [])[0]
                if data.get("message") == "ok":
                    power_status = data.get("data", {}).get("screen.openStatus", "false")
                    is_on = power_status == "true"
                    self.power_toggle_btn.blockSignals(True)
                    self.power_toggle_btn.setChecked(is_on)
                    self.power_toggle_btn.setText("Turn Off" if is_on else "Turn On")
                    self.power_toggle_btn.blockSignals(False)
            
            response = self.huidu_controller.get_schedule_task([self.controller_id], ["screen"])
            
            if response.get("message") == "ok" and response.get("data"):
                schedule_tasks = response.get("data", {})
                if schedule_tasks:
                    power_schedule = schedule_tasks.get("screen", [])
                    if power_schedule:
                        for task in power_schedule:
                            date_range = task.get("dateRange", "")
                            time_range = task.get("timeRange", "")
                            week_filter = task.get("WeekFilter", "")
                            data = task.get("data", "false")
                            enabled = data.lower() == "true"
                            
                            self.add_schedule_row(date_range, time_range, week_filter, enabled)
                        
                        logger.info(f"Loaded power schedule from device")
        except Exception as e:
            logger.error(f"Error loading power schedule from device: {e}", exc_info=True)
    
    def toggle_power(self, checked):
        try:
            if not self.controller_id:
                self.power_toggle_btn.blockSignals(True)
                self.power_toggle_btn.setChecked(not checked)
                self.power_toggle_btn.blockSignals(False)
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            if checked:
                response = self.huidu_controller.turn_on_screen([self.controller_id])
                if response.get("message") == "ok":
                    self.power_toggle_btn.setText("Turn Off")
                    QMessageBox.information(self, "Success", "Device turned on.")
                else:
                    error_msg = response.get("data", "Unknown error")
                    self.power_toggle_btn.blockSignals(True)
                    self.power_toggle_btn.setChecked(False)
                    self.power_toggle_btn.setText("Turn On")
                    self.power_toggle_btn.blockSignals(False)
                    QMessageBox.warning(self, "Failed", f"Failed to turn device on: {error_msg}.")
            else:
                response = self.huidu_controller.turn_off_screen([self.controller_id])
                if response.get("message") == "ok":
                    self.power_toggle_btn.setText("Turn On")
                    QMessageBox.information(self, "Success", "Device turned off.")
                else:
                    error_msg = response.get("data", "Unknown error")
                    self.power_toggle_btn.blockSignals(True)
                    self.power_toggle_btn.setChecked(True)
                    self.power_toggle_btn.setText("Turn Off")
                    self.power_toggle_btn.blockSignals(False)
                    QMessageBox.warning(self, "Failed", f"Failed to turn device off: {error_msg}.")
            
        except Exception as e:
            logger.error(f"Error toggling power: {e}", exc_info=True)
            self.power_toggle_btn.blockSignals(True)
            self.power_toggle_btn.setChecked(not checked)
            self.power_toggle_btn.blockSignals(False)
            QMessageBox.critical(self, "Error", f"Error toggling power: {str(e)}")
    
    def save_and_send(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            schedule = self.get_power_schedule()
            
            schedule_data = {
                "screen": schedule
            }
            
            response = self.huidu_controller.set_schedule_task([self.controller_id], schedule_data)
            
            if response.get("message") == "ok" and response.get("data")[0].get("message") == "ok":
                QMessageBox.information(self, "Success", "Power schedule saved and sent to controller.")
                self.accept()
            else:
                error_msg = response.get("data")[0].get("message", "Unknown error")
                QMessageBox.warning(self, "Failed", f"Failed to save power schedule: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")

