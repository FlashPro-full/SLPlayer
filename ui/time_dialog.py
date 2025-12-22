from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from datetime import datetime
from typing import Optional, Dict, Any, List
from controllers.huidu import HuiduController
from utils.logger import get_logger

try:
    from zoneinfo import ZoneInfo
    import zoneinfo
    ZONEINFO_AVAILABLE = True
    PYTZ_AVAILABLE = False
except ImportError:
    ZONEINFO_AVAILABLE = False
    try:
        import pytz  # type: ignore
        PYTZ_AVAILABLE = True
    except ImportError:
        PYTZ_AVAILABLE = False

logger = get_logger(__name__)

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
"""


class TimeDialog(QDialog):
    
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
        
        self.setWindowTitle(f"Time Settings" + (f" - {screen_name}" if screen_name else ""))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.time_settings: Dict[str, Any] = {}
        self.huidu_controller = HuiduController()
        self.timezone_list = self._get_system_timezones()
        
        self.init_ui()
        self.load_from_device()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        self.sync_method_combo.addItems(["PC", "NTP"])
        method_layout.addWidget(self.sync_method_combo)
        sync_layout.addLayout(method_layout)
        
        timezone_layout = QHBoxLayout()
        timezone_layout.addWidget(QLabel("Time Zone:"))
        
        self.timezone_combo = QComboBox()
        if self.timezone_list:
            self.timezone_combo.addItems(self.timezone_list)
        else:
            self.timezone_combo.addItems(["UTC", "Local", "GMT+0", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12", "GMT-1", "GMT-2", "GMT-3", "GMT-4", "GMT-5", "GMT-6", "GMT-7", "GMT-8", "GMT-9", "GMT-10", "GMT-11", "GMT-12"])
        timezone_layout.addWidget(self.timezone_combo, stretch=1)
        sync_layout.addLayout(timezone_layout)
        
        layout.addWidget(sync_group)
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
    
    def _get_system_timezones(self) -> List[str]:
        timezones = []
        try:
            if ZONEINFO_AVAILABLE:
                all_zones = sorted(zoneinfo.available_timezones())
                for tz_name in all_zones:
                    try:
                        tz = ZoneInfo(tz_name)
                        now = datetime.now(tz)
                        offset = now.strftime("%z")
                        offset_str = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC+00:00"
                        city = tz_name.split("/")[-1].replace("_", " ")
                        display_name = f"{tz_name} ({offset_str}) - {city}"
                        timezones.append(display_name)
                    except Exception:
                        timezones.append(tz_name)
            elif PYTZ_AVAILABLE:
                import pytz
                all_zones = sorted(pytz.all_timezones)
                for tz_name in all_zones:
                    try:
                        tz = pytz.timezone(tz_name)
                        now = datetime.now(tz)
                        offset = now.strftime("%z")
                        offset_str = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC+00:00"
                        city = tz_name.split("/")[-1].replace("_", " ")
                        display_name = f"{tz_name} ({offset_str}) - {city}"
                        timezones.append(display_name)
                    except Exception:
                        timezones.append(tz_name)
            else:
                timezones = ["UTC", "Local", "GMT+0", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12", "GMT-1", "GMT-2", "GMT-3", "GMT-4", "GMT-5", "GMT-6", "GMT-7", "GMT-8", "GMT-9", "GMT-10", "GMT-11", "GMT-12"]
        except Exception as e:
            logger.error(f"Error getting system timezones: {e}")
            timezones = ["UTC", "Local", "GMT+0", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12", "GMT-1", "GMT-2", "GMT-3", "GMT-4", "GMT-5", "GMT-6", "GMT-7", "GMT-8", "GMT-9", "GMT-10", "GMT-11", "GMT-12"]
        return timezones
    
    def update_time_display(self):
        self.current_time_label.setText("Current PC Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def sync_time(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
                return
            
            use_ntp = self.sync_method_combo.currentIndex() == 1
            
            if use_ntp:
                QMessageBox.information(self, "NTP Sync", 
                                      "NTP sync will be configured when you save the settings.")
            else:
                QMessageBox.information(self, "PC Time", 
                                      "PC time sync will be configured when you save the settings.")
                
        except Exception as e:
            logger.error(f"Error syncing time: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error syncing time: {str(e)}")
    
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            property_keys = ["time", "time.timeZone", "time.sync"]
            response = self.huidu_controller.get_device_property([self.controller_id], property_keys)
            
            if response.get("message") == "ok" and response.get("data"):
                device_data_list = response.get("data", [])
                if device_data_list and len(device_data_list) > 0:
                    device_data = device_data_list[0].get("data", {})
                    
                    time_sync = device_data.get("time.sync", "pc")
                    if time_sync == "ntp":
                        self.sync_method_combo.setCurrentIndex(1)
                    else:
                        self.sync_method_combo.setCurrentIndex(0)
                    
                    time_zone = device_data.get("time.timeZone", "")
                    if time_zone:
                        self.time_settings["time.timeZone"] = time_zone
                        timezone_found = False
                        for i, tz_display in enumerate(self.timezone_list):
                            if tz_display.startswith(time_zone) or time_zone in tz_display:
                                self.timezone_combo.setCurrentIndex(i)
                                timezone_found = True
                                break
                        if not timezone_found:
                            timezone_index = self.timezone_combo.findText(time_zone)
                            if timezone_index >= 0:
                                self.timezone_combo.setCurrentIndex(timezone_index)
                            else:
                                if "Local" in self.timezone_list:
                                    local_index = self.timezone_list.index("Local")
                                    self.timezone_combo.setCurrentIndex(local_index)
                    else:
                        if "Local" in self.timezone_list:
                            local_index = self.timezone_list.index("Local")
                            self.timezone_combo.setCurrentIndex(local_index)
                    
                    logger.info(f"Loaded time settings from device: {device_data}")
        except Exception as e:
            logger.error(f"Error loading time settings from device: {e}", exc_info=True)
    
    def save_and_send(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            use_ntp = self.sync_method_combo.currentIndex() == 1
            
            properties = {
                "time.sync": "ntp" if use_ntp else "pc"
            }
            
            if use_ntp:
                properties["time.ntp"] = "ntp.huidu.cn"
            
            selected_timezone = self.timezone_combo.currentText()
            if selected_timezone:
                if "(" in selected_timezone:
                    timezone_value = selected_timezone.split(" (")[0]
                else:
                    timezone_value = selected_timezone
                properties["time.timeZone"] = timezone_value
            
            response = self.huidu_controller.set_device_property(properties, [self.controller_id])
            
            if response.get("message") == "ok":
                QMessageBox.information(self, "Success", "Time settings saved and sent to controller.")
                self.settings_changed.emit(properties)
                self.accept()
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Failed", f"Failed to save time settings: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")
    
    def closeEvent(self, event):
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        event.accept()

