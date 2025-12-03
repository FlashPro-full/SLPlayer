from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QCheckBox, QTimeEdit, QSpinBox, QSlider, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget, QWidget,
    QFormLayout, QDateTimeEdit
)
from PyQt5.QtCore import Qt, QTime, pyqtSignal, QTimer
from datetime import datetime, time
from typing import Optional, Dict, List
from utils.ntp_sync import NTPSync
from utils.logger import get_logger

logger = get_logger(__name__)


class TimePowerBrightnessDialog(QDialog):
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, controller=None, screen_name: Optional[str] = None):
        super().__init__(parent)
        self.controller = controller
        self.screen_name = screen_name
        self.controller_id = None
        if controller:
            try:
                self.controller_id = controller.get_controller_id()
            except:
                pass
        
        self.setWindowTitle(f"Time / Power / Brightness Settings" + (f" - {screen_name}" if screen_name else ""))
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        

        self.time_settings = {}
        self.power_schedules = []
        self.brightness_settings = {}
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        

        tabs = QTabWidget()
        

        time_tab = self.create_time_tab()
        tabs.addTab(time_tab, "⏰ Time Sync")
        

        power_tab = self.create_power_tab()
        tabs.addTab(power_tab, "⚡ Power Schedule")
        

        brightness_tab = self.create_brightness_tab()
        tabs.addTab(brightness_tab, "💡 Brightness")
        
        layout.addWidget(tabs)
        

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        read_btn = QPushButton("📥 Read from Controller")
        read_btn.clicked.connect(self.read_from_controller)
        button_layout.addWidget(read_btn)
        
        save_btn = QPushButton("💾 Save & Send")
        save_btn.clicked.connect(self.save_and_send)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_time_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        

        sync_group = QGroupBox("Time Synchronization")
        sync_layout = QVBoxLayout(sync_group)
        

        self.current_time_label = QLabel("Current PC Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sync_layout.addWidget(self.current_time_label)
        

        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time_display)
        self.time_timer.start(1000)
        

        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Sync Method:"))
        
        self.sync_method_combo = QComboBox()
        self.sync_method_combo.addItems(["PC Time", "NTP Server (it.pool.ntp.org)"])
        method_layout.addWidget(self.sync_method_combo)
        sync_layout.addLayout(method_layout)
        

        sync_btn = QPushButton("🔄 Sync Time Now")
        sync_btn.clicked.connect(self.sync_time)
        sync_layout.addWidget(sync_btn)
        
        layout.addWidget(sync_group)
        layout.addStretch()
        
        return widget
    
    def create_power_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        

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
        

        schedule_btn_layout = QHBoxLayout()
        add_schedule_btn = QPushButton("➕ Add Schedule")
        add_schedule_btn.clicked.connect(self.add_schedule)
        schedule_btn_layout.addWidget(add_schedule_btn)
        
        remove_schedule_btn = QPushButton("➖ Remove Schedule")
        remove_schedule_btn.clicked.connect(self.remove_schedule)
        schedule_btn_layout.addWidget(remove_schedule_btn)
        
        schedule_btn_layout.addStretch()
        schedule_layout.addLayout(schedule_btn_layout)
        
        layout.addWidget(schedule_group)
        layout.addStretch()
        
        return widget
    
    def create_brightness_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        

        current_group = QGroupBox("Current Brightness")
        current_layout = QFormLayout(current_group)
        
        self.current_brightness_label = QLabel("Reading...")
        current_layout.addRow("Brightness Level:", self.current_brightness_label)
        
        read_brightness_btn = QPushButton("📥 Read from Controller")
        read_brightness_btn.clicked.connect(self.read_brightness)
        current_layout.addRow(read_brightness_btn)
        
        layout.addWidget(current_group)
        

        control_group = QGroupBox("Brightness Control")
        control_layout = QVBoxLayout(control_group)
        

        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)
        
        self.brightness_value_label = QLabel("100%")
        self.brightness_value_label.setMinimumWidth(50)
        brightness_layout.addWidget(self.brightness_value_label)
        
        control_layout.addLayout(brightness_layout)
        

        time_range_group = QGroupBox("Brightness by Time Range")
        time_range_layout = QVBoxLayout(time_range_group)
        
        self.enable_time_brightness_check = QCheckBox("Enable Time-Based Brightness")
        time_range_layout.addWidget(self.enable_time_brightness_check)
        

        self.brightness_table = QTableWidget()
        self.brightness_table.setColumnCount(4)
        self.brightness_table.setHorizontalHeaderLabels(["From Time", "To Time", "Brightness %", "Enabled"])
        self.brightness_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        

        self.brightness_table.setRowCount(1)
        self.add_brightness_row(0, QTime(0, 0), QTime(23, 59), 100)
        
        time_range_layout.addWidget(self.brightness_table)
        

        brightness_btn_layout = QHBoxLayout()
        add_brightness_btn = QPushButton("➕ Add Time Range")
        add_brightness_btn.clicked.connect(self.add_brightness_range)
        brightness_btn_layout.addWidget(add_brightness_btn)
        
        remove_brightness_btn = QPushButton("➖ Remove Time Range")
        remove_brightness_btn.clicked.connect(self.remove_brightness_range)
        brightness_btn_layout.addWidget(remove_brightness_btn)
        
        brightness_btn_layout.addStretch()
        time_range_layout.addLayout(brightness_btn_layout)
        
        control_layout.addWidget(time_range_group)
        
        sensor_group = QGroupBox("Brightness by Sensor")
        sensor_layout = QVBoxLayout(sensor_group)
        
        self.enable_sensor_brightness_check = QCheckBox("Enable Sensor-Based Brightness")
        sensor_layout.addWidget(self.enable_sensor_brightness_check)
        
        sensor_info_layout = QHBoxLayout()
        sensor_info_layout.addWidget(QLabel("Sensor Value:"))
        self.sensor_value_label = QLabel("--")
        sensor_info_layout.addWidget(self.sensor_value_label)
        
        read_sensor_btn = QPushButton("📥 Read Sensor")
        read_sensor_btn.clicked.connect(self.read_sensor_value)
        sensor_info_layout.addWidget(read_sensor_btn)
        sensor_info_layout.addStretch()
        sensor_layout.addLayout(sensor_info_layout)
        
        sensor_config_layout = QFormLayout()
        self.sensor_min_brightness = QSpinBox()
        self.sensor_min_brightness.setMinimum(0)
        self.sensor_min_brightness.setMaximum(100)
        self.sensor_min_brightness.setValue(20)
        self.sensor_min_brightness.setSuffix("%")
        sensor_config_layout.addRow("Min Brightness:", self.sensor_min_brightness)
        
        self.sensor_max_brightness = QSpinBox()
        self.sensor_max_brightness.setMinimum(0)
        self.sensor_max_brightness.setMaximum(100)
        self.sensor_max_brightness.setValue(100)
        self.sensor_max_brightness.setSuffix("%")
        sensor_config_layout.addRow("Max Brightness:", self.sensor_max_brightness)
        
        sensor_layout.addLayout(sensor_config_layout)
        control_layout.addWidget(sensor_group)
        
        layout.addWidget(control_group)
        layout.addStretch()
        
        return widget
    
    def add_brightness_row(self, row: int, from_time: QTime, to_time: QTime, brightness: int):

        from_time_edit = QTimeEdit()
        from_time_edit.setTime(from_time)
        from_time_edit.setDisplayFormat("HH:mm")
        self.brightness_table.setCellWidget(row, 0, from_time_edit)
        

        to_time_edit = QTimeEdit()
        to_time_edit.setTime(to_time)
        to_time_edit.setDisplayFormat("HH:mm")
        self.brightness_table.setCellWidget(row, 1, to_time_edit)
        

        brightness_spin = QSpinBox()
        brightness_spin.setMinimum(0)
        brightness_spin.setMaximum(100)
        brightness_spin.setValue(brightness)
        brightness_spin.setSuffix("%")
        self.brightness_table.setCellWidget(row, 2, brightness_spin)
        

        enabled_check = QCheckBox()
        enabled_check.setChecked(True)
        self.brightness_table.setCellWidget(row, 3, enabled_check)
    
    def add_brightness_range(self):
        row = self.brightness_table.rowCount()
        self.brightness_table.insertRow(row)
        self.add_brightness_row(row, QTime(0, 0), QTime(23, 59), 100)
    
    def remove_brightness_range(self):
        current_row = self.brightness_table.currentRow()
        if current_row >= 0 and self.brightness_table.rowCount() > 1:
            self.brightness_table.removeRow(current_row)
        elif current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a row to remove.")
    
    def add_schedule(self):


        QMessageBox.information(self, "Info", "Use the weekly schedule table above to set daily schedules.")
    
    def remove_schedule(self):

        QMessageBox.information(self, "Info", "Weekly schedule cannot be removed. Disable individual days if needed.")
    
    def update_time_display(self):
        self.current_time_label.setText("Current PC Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def sync_time(self):
        try:
            if not self.controller:
                QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
                return
            
            use_ntp = self.sync_method_combo.currentIndex() == 1
            
            if use_ntp:
                # Check internet connectivity before attempting NTP sync
                if not NTPSync.has_internet_connectivity():
                    QMessageBox.warning(self, "No Internet", 
                                       "No internet connectivity detected. NTP sync requires internet connection.\nFalling back to PC time.")
                    sync_time = datetime.now()
                else:
                    # Get time from NTP server
                    ntp_time = NTPSync.get_ntp_time()
                    if ntp_time is None:
                        QMessageBox.warning(self, "NTP Sync Failed", 
                                           "Failed to sync with NTP server. Falling back to PC time.")
                        sync_time = datetime.now()
                    else:
                        sync_time = ntp_time
                        QMessageBox.information(self, "NTP Sync Success", 
                                              f"Time synchronized from NTP: {sync_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                sync_time = datetime.now()
            

            if hasattr(self.controller, 'set_time'):
                if self.controller.set_time(sync_time):
                    QMessageBox.information(self, "Success", 
                                           f"Time synchronized to controller: {sync_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    QMessageBox.warning(self, "Failed", "Failed to send time to controller.")
            else:
                QMessageBox.warning(self, "Not Supported", "Controller does not support time synchronization.")
                
        except Exception as e:
            logger.error(f"Error syncing time: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error syncing time: {str(e)}")
    
    def read_brightness(self):
        try:
            if not self.controller:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            if hasattr(self.controller, 'get_brightness'):
                brightness = self.controller.get_brightness()
                if brightness is not None:
                    self.brightness_slider.setValue(brightness)
                    self.brightness_value_label.setText(f"{brightness}%")
                    self.current_brightness_label.setText(f"{brightness}%")
                    
                    if hasattr(self.controller, 'set_brightness'):
                        self.controller.set_brightness(brightness)
                    
                    QMessageBox.information(self, "Success", f"Brightness read from controller and applied: {brightness}%")
                else:
                    QMessageBox.warning(self, "Failed", "Could not read brightness from controller.")
            else:
                QMessageBox.warning(self, "Not Supported", "Controller does not support brightness reading.")
                
        except Exception as e:
            logger.error(f"Error reading brightness: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error reading brightness: {str(e)}")
    
    def read_sensor_value(self):
        try:
            if not self.controller:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            device_info = self.controller.get_device_info() if hasattr(self.controller, 'get_device_info') else None
            if device_info:
                sensor_value = device_info.get("sensor_value") or device_info.get("brightness_sensor") or device_info.get("light_sensor")
                if sensor_value is not None:
                    self.sensor_value_label.setText(str(sensor_value))
                    QMessageBox.information(self, "Success", f"Sensor value read: {sensor_value}")
                else:
                    QMessageBox.warning(self, "No Sensor", "No sensor value available from controller.")
            else:
                QMessageBox.warning(self, "Failed", "Could not read device info.")
                
        except Exception as e:
            logger.error(f"Error reading sensor value: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error reading sensor value: {str(e)}")
    
    def on_brightness_changed(self, value: int):
        self.brightness_value_label.setText(f"{value}%")
    
    def read_from_controller(self):
        try:
            if not self.controller:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            

            self.read_brightness()
            

            if hasattr(self.controller, 'get_power_schedule'):
                schedule = self.controller.get_power_schedule()
                if schedule:
                    self.load_power_schedule(schedule)
            
            QMessageBox.information(self, "Success", "Settings read from controller.")
            
        except Exception as e:
            logger.error(f"Error reading from controller: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error reading from controller: {str(e)}")
    
    def load_power_schedule(self, schedule):
        """Load power schedule into the UI table"""
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
            elif isinstance(schedule, dict):
                on_time_str = schedule.get("on_time", "08:00")
                off_time_str = schedule.get("off_time", "22:00")
                enabled = schedule.get("enabled", True)
                
                on_hour, on_min = map(int, on_time_str.split(':'))
                off_hour, off_min = map(int, off_time_str.split(':'))
                
                for i in range(self.schedule_table.rowCount()):
                    on_time_widget = self.schedule_table.cellWidget(i, 1)
                    off_time_widget = self.schedule_table.cellWidget(i, 2)
                    enabled_widget = self.schedule_table.cellWidget(i, 3)
                    
                    if on_time_widget:
                        on_time_widget.setTime(QTime(on_hour, on_min))
                    if off_time_widget:
                        off_time_widget.setTime(QTime(off_hour, off_min))
                    if enabled_widget:
                        enabled_widget.setChecked(enabled)
        except Exception as e:
            logger.error(f"Error loading power schedule: {e}", exc_info=True)
    
    def save_and_send(self):
        try:
            if not self.controller or not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            

            settings = {
                "time_sync": {
                    "method": "ntp" if self.sync_method_combo.currentIndex() == 1 else "pc"
                },
                "power_schedule": self.get_power_schedule(),
                "brightness": self.brightness_slider.value(),
                "brightness_settings": self.get_brightness_settings(),
                "time_last_synced": datetime.now().isoformat() if self.sync_method_combo.currentIndex() == 1 else None
            }
            

            success = True
            

            if hasattr(self.controller, 'set_brightness'):
                brightness = self.brightness_slider.value()
                brightness_settings = self.get_brightness_settings()
                if not self.controller.set_brightness(brightness, brightness_settings):
                    success = False
            

            if hasattr(self.controller, 'set_power_schedule'):
                schedule = self.get_power_schedule()
                if schedule:
                    if not self.controller.set_power_schedule(schedule):
                        success = False
            
            # Save settings to database per controller/screen
            from core.controller_database import get_controller_database
            db = get_controller_database()
            db.save_controller_settings(self.controller_id, settings, self.screen_name)
            
            if success:
                QMessageBox.information(self, "Success", "Settings saved and sent to controller.")
                self.settings_changed.emit(settings)
                self.accept()
            else:
                QMessageBox.warning(self, "Partial Success", "Some settings may not have been sent successfully.")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")
    
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
    
    def get_brightness_settings(self) -> Dict:
        settings = {
            "current": self.brightness_slider.value(),
            "time_ranges": [],
            "sensor": {
                "enabled": self.enable_sensor_brightness_check.isChecked(),
                "min_brightness": self.sensor_min_brightness.value(),
                "max_brightness": self.sensor_max_brightness.value()
            }
        }
        
        if self.enable_time_brightness_check.isChecked():
            for i in range(self.brightness_table.rowCount()):
                from_widget = self.brightness_table.cellWidget(i, 0)
                to_widget = self.brightness_table.cellWidget(i, 1)
                brightness_widget = self.brightness_table.cellWidget(i, 2)
                enabled_widget = self.brightness_table.cellWidget(i, 3)
                
                if from_widget and to_widget and brightness_widget and enabled_widget:
                    if enabled_widget.isChecked():
                        settings["time_ranges"].append({
                            "from": from_widget.time().toString("HH:mm"),
                            "to": to_widget.time().toString("HH:mm"),
                            "brightness": brightness_widget.value()
                        })
        
        return settings
    
    def load_settings(self):
        """Load settings from database first, then from controller if not in database"""
        from core.controller_database import get_controller_database
        
        if not self.controller_id:
            return
        
        db = get_controller_database()
        
        # Try to load from database first
        saved_settings = db.get_controller_settings(self.controller_id, self.screen_name)
        
        if saved_settings:
            brightness = saved_settings.get("brightness")
            if brightness is not None:
                self.brightness_slider.setValue(brightness)
                self.brightness_value_label.setText(f"{brightness}%")
                self.current_brightness_label.setText(f"{brightness}%")
            
            brightness_settings = saved_settings.get("brightness_settings", {})
            if brightness_settings.get("time_ranges"):
                self.enable_time_brightness_check.setChecked(True)
                time_ranges = brightness_settings.get("time_ranges", [])
                self.brightness_table.setRowCount(0)
                for time_range in time_ranges:
                    row = self.brightness_table.rowCount()
                    self.brightness_table.insertRow(row)
                    from_time = QTime.fromString(time_range.get("from", "00:00"), "HH:mm")
                    to_time = QTime.fromString(time_range.get("to", "23:59"), "HH:mm")
                    brightness_val = time_range.get("brightness", 100)
                    self.add_brightness_row(row, from_time, to_time, brightness_val)
            
            power_schedule = saved_settings.get("power_schedule")
            if power_schedule:
                self.load_power_schedule(power_schedule)
            
            time_sync_method = saved_settings.get("time_sync", {}).get("method", "pc")
            if time_sync_method == "ntp":
                self.sync_method_combo.setCurrentIndex(1)
            
            logger.info(f"Loaded settings from database for controller {self.controller_id}")
            return
        
        # Fallback: load from controller if not in database
        if self.controller:
            try:
                if hasattr(self.controller, 'get_brightness'):
                    brightness = self.controller.get_brightness()
                    if brightness is not None:
                        self.brightness_slider.setValue(brightness)
                        self.brightness_value_label.setText(f"{brightness}%")
                        self.current_brightness_label.setText(f"{brightness}%")
                
                if hasattr(self.controller, 'get_power_schedule'):
                    schedule = self.controller.get_power_schedule()
                    if schedule:
                        self.load_power_schedule(schedule)
            except Exception as e:
                logger.debug(f"Error loading settings from controller: {e}")
    
    def closeEvent(self, event):
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        event.accept()

