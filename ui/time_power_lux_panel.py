"""
Time, Power, and Lux management panel
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QTimeEdit, QSpinBox,
                             QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from typing import Optional, Dict


class TimePowerLuxPanel(QWidget):
    """Panel for managing time sync, power schedule, and brightness"""
    
    settings_changed = pyqtSignal(dict)  # Emits when settings change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Time Sync Group
        time_group = QGroupBox("Time Synchronization")
        time_layout = QVBoxLayout()
        
        sync_layout = QHBoxLayout()
        self.sync_pc_btn = QPushButton("Sync with PC Time")
        self.sync_pc_btn.clicked.connect(self.sync_pc_time)
        sync_layout.addWidget(self.sync_pc_btn)
        
        self.sync_ntp_btn = QPushButton("Sync with NTP")
        self.sync_ntp_btn.clicked.connect(self.sync_ntp_time)
        sync_layout.addWidget(self.sync_ntp_btn)
        time_layout.addLayout(sync_layout)
        
        self.current_time_label = QLabel("Current Time: --:--:--")
        time_layout.addWidget(self.current_time_label)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # Power Schedule Group
        power_group = QGroupBox("Power Schedule")
        power_layout = QVBoxLayout()
        
        self.power_schedule_enabled = QCheckBox("Enable Power Schedule")
        self.power_schedule_enabled.stateChanged.connect(self.on_power_schedule_changed)
        power_layout.addWidget(self.power_schedule_enabled)
        
        on_off_layout = QHBoxLayout()
        on_off_layout.addWidget(QLabel("Power On:"))
        self.power_on_time = QTimeEdit()
        self.power_on_time.setTime(QTime(8, 0, 0))
        self.power_on_time.timeChanged.connect(self.on_power_time_changed)
        on_off_layout.addWidget(self.power_on_time)
        
        on_off_layout.addWidget(QLabel("Power Off:"))
        self.power_off_time = QTimeEdit()
        self.power_off_time.setTime(QTime(22, 0, 0))
        self.power_off_time.timeChanged.connect(self.on_power_time_changed)
        on_off_layout.addWidget(self.power_off_time)
        power_layout.addLayout(on_off_layout)
        
        power_group.setLayout(power_layout)
        layout.addWidget(power_group)
        
        # Brightness (Lux) Group
        lux_group = QGroupBox("Brightness Control")
        lux_layout = QVBoxLayout()
        
        read_layout = QHBoxLayout()
        self.read_brightness_btn = QPushButton("Read from Controller")
        self.read_brightness_btn.clicked.connect(self.read_brightness)
        read_layout.addWidget(self.read_brightness_btn)
        lux_layout.addLayout(read_layout)
        
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        self.brightness_spin = QSpinBox()
        self.brightness_spin.setRange(0, 100)
        self.brightness_spin.setValue(80)
        self.brightness_spin.setSuffix("%")
        self.brightness_spin.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_spin)
        lux_layout.addLayout(brightness_layout)
        
        self.current_brightness_label = QLabel("Current: --%")
        lux_layout.addWidget(self.current_brightness_label)
        
        send_layout = QHBoxLayout()
        send_layout.addStretch()
        self.send_params_btn = QPushButton("Send Parameters")
        self.send_params_btn.clicked.connect(self.send_parameters)
        send_layout.addWidget(self.send_params_btn)
        lux_layout.addLayout(send_layout)
        
        lux_group.setLayout(lux_layout)
        layout.addWidget(lux_group)
        
        layout.addStretch()
        
        # Update time display
        self.update_time_display()
    
    def set_controller(self, controller):
        """Set current controller"""
        self.controller = controller
        enabled = controller is not None
        self.read_brightness_btn.setEnabled(enabled)
        self.send_params_btn.setEnabled(enabled)
        self.sync_pc_btn.setEnabled(enabled)
        self.sync_ntp_btn.setEnabled(enabled)
        if controller:
            # Read brightness at startup (as per spec requirement)
            self.read_brightness()
    
    def update_time_display(self):
        """Update current time display"""
        now = datetime.now()
        self.current_time_label.setText(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def sync_pc_time(self):
        """Sync controller time with PC time"""
        if not self.controller:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Controller", "Please connect to a controller first")
            return
        
        # Send PC time to controller
        from utils.ntp_sync import NTPSync
        now = datetime.now()
        success = NTPSync.sync_controller_time(self.controller, use_ntp=False)
        
        if success:
            self.update_time_display()
            self.settings_changed.emit({"time_sync": "pc", "time": now.isoformat()})
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", "Time synchronized with PC")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Failed", "Could not sync time with controller")
    
    def sync_ntp_time(self):
        """Sync controller time with NTP server"""
        if not self.controller:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Controller", "Please connect to a controller first")
            return
        
        # Check if we have internet (try to sync with NTP)
        from utils.ntp_sync import NTPSync
        success = NTPSync.sync_controller_time(self.controller, use_ntp=True)
        
        if success:
            self.update_time_display()
            self.settings_changed.emit({"time_sync": "ntp"})
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", "Time synchronized with NTP server")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Failed", "Could not sync time with NTP server. Check internet connection.")
    
    def on_power_schedule_changed(self, state):
        """Handle power schedule enable/disable"""
        enabled = state == Qt.CheckState.Checked.value
        self.power_on_time.setEnabled(enabled)
        self.power_off_time.setEnabled(enabled)
        self.settings_changed.emit({
            "power_schedule": {
                "enabled": enabled,
                "on_time": self.power_on_time.time().toString("HH:mm:ss"),
                "off_time": self.power_off_time.time().toString("HH:mm:ss")
            }
        })
    
    def on_power_time_changed(self):
        """Handle power time change"""
        if self.power_schedule_enabled.isChecked():
            self.settings_changed.emit({
                "power_schedule": {
                    "enabled": True,
                    "on_time": self.power_on_time.time().toString("HH:mm:ss"),
                    "off_time": self.power_off_time.time().toString("HH:mm:ss")
                }
            })
    
    def read_brightness(self):
        """Read brightness from controller"""
        if not self.controller:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Controller", "Please connect to a controller first")
            return
        
        # Read brightness from controller
        try:
            if hasattr(self.controller, 'get_brightness'):
                brightness = self.controller.get_brightness()
                if brightness is not None:
                    self.brightness_spin.setValue(brightness)
                    self.current_brightness_label.setText(f"Current: {brightness}%")
                    return
            
            # Fallback: try to get from device info
            device_info = self.controller.get_device_info()
            if device_info and "brightness" in device_info:
                brightness = device_info["brightness"]
                self.brightness_spin.setValue(brightness)
                self.current_brightness_label.setText(f"Current: {brightness}%")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Not Supported", "Controller does not support brightness reading")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error reading brightness: {e}")
            QMessageBox.warning(self, "Error", f"Could not read brightness: {e}")
    
    def on_brightness_changed(self, value):
        """Handle brightness change"""
        self.current_brightness_label.setText(f"Current: {value}%")
    
    def send_parameters(self):
        """Send all parameters to controller"""
        if not self.controller:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Controller", "Please connect to a controller first")
            return
        
        try:
            # Send brightness
            brightness = self.brightness_spin.value()
            if hasattr(self.controller, 'set_brightness'):
                if not self.controller.set_brightness(brightness):
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Failed", "Could not set brightness")
                    return
            
            # Send power schedule
            if self.power_schedule_enabled.isChecked():
                on_time = self.power_on_time.time().toString("HH:mm:ss")
                off_time = self.power_off_time.time().toString("HH:mm:ss")
                if hasattr(self.controller, 'set_power_schedule'):
                    if not self.controller.set_power_schedule(on_time, off_time, True):
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "Failed", "Could not set power schedule")
                        return
            
            params = {
                "brightness": brightness,
                "power_schedule": {
                    "enabled": self.power_schedule_enabled.isChecked(),
                    "on_time": on_time if self.power_schedule_enabled.isChecked() else "",
                    "off_time": off_time if self.power_schedule_enabled.isChecked() else ""
                }
            }
            
            # Emit signal
            self.settings_changed.emit(params)
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", "Parameters sent to controller successfully")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error sending parameters: {e}")
            QMessageBox.warning(self, "Error", f"Could not send parameters: {e}")

