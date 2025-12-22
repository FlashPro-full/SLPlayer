from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from datetime import datetime
from typing import Optional, Dict, Any, List
from controllers.huidu import HuiduController
from utils.logger import get_logger
import zoneinfo
import sys

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
        timezone_list = self._get_timezone_list()
        self.timezone_combo.addItems(timezone_list)
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
    
    def _get_windows_timezone(self) -> str:
        try:
            if sys.platform == "win32":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation")
                try:
                    timezone_key = winreg.QueryValueEx(key, "TimeZoneKeyName")[0]
                    winreg.CloseKey(key)
                    return timezone_key
                except:
                    winreg.CloseKey(key)
            return ""
        except Exception:
            return ""
    
    def _get_timezone_list(self) -> List[str]:
        timezones = [
            "Midway Island (UTC-11:00)",
            "Honolulu (UTC-10:00)",
            "Anchorage (UTC-09:00)",
            "Los Angeles (UTC-08:00)",
            "Tijuana (UTC-08:00)",
            "Phoenix (UTC-07:00)",
            "Chihuahua (UTC-07:00)",
            "Denver (UTC-07:00)",
            "Costa Rica (UTC-06:00)",
            "Regina (UTC-06:00)",
            "Mexico City (UTC-06:00)",
            "Chicago (UTC-06:00)",
            "Bogota (UTC-05:00)",
            "New York (UTC-05:00)",
            "Caracas (UTC-04:30)",
            "Barbados (UTC-04:00)",
            "Manaus (UTC-04:00)",
            "San Diego (UTC-04:00)",
            "Newfoundland (UTC-03:30)",
            "Buenos Aires (UTC-03:00)",
            "Montevideo (UTC-03:00)",
            "Sao Paulo (UTC-03:00)",
            "Gothab (UTC-03:00)",
            "South Georgia (UTC-02:00)",
            "Azores (UTC-01:00)",
            "Cape Verde (UTC-01:00)",
            "London (UTC+00:00)",
            "Casablanca (UTC+00:00)",
            "Brazavi (UTC+01.00)",
            "Amsterdam (UTC+01:00)",
            "Belgrade (UTC+01:00)",
            "Brussels (UTC+01:00)",
            "Sarajevo (UTC+01:00)",
            "Windhoek (UTC+02:00)",
            "Cairo (UTC+02:00)",
            "Athens (UTC+02:00)",
            "Harare, Pretoria (UTC+02:00)",
            "Amman (UTC+02:00)",
            "Athens (UTC+02:00)",
            "Beirut (UTC+02:00)",
            "Helsinki (UTC+02:00)",
            "Jerusalem (UTC+02:00)",
            "Minsk (UTC+03:00)",
            "Baghdad (UTC+03:00)",
            "Kuwait (UTC+03:00)",
            "Nairobi (UTC+03:00)",
            "Moscow (UTC+03:00)",
            "Tehran (UTC+03:30)",
            "Tbilisi (UTC+04:00)",
            "Yerevan (UTC+04:00)",
            "Dubai (UTC+04:00)",
            "Baku (UTC+04:00)",
            "Kabul (UTC+04:30)",
            "Karachi (UTC+05:00)",
            "Ural (UTC+05:00)",
            "Yekaterinburg (UTC+05:00)",
            "Calcutta (UTC+05:30)",
            "Colombo (UTC+05:30)",
            "Kathmandu (UTC+05:45)",
            "Almaty (UTC+06:00)",
            "Yangon (UTC+06:30)",
            "Bangkok (UTC+07:00)",
            "Krasnoyarsk (UTC+07:00)",
            "Beijing (UTC+08:00)",
            "Hong Kong (UTC+08:00)",
            "Kuala Lumpur (UTC+08:00)",
            "Perth (UTC+08:00)",
            "Taipei (UTC+08:00)",
            "Irkutsk (UTC+08:00)",
            "Seoul (UTC+09:00)",
            "Tokyo (UTC+09:00)",
            "Yakutsk (UTC+09:00)",
            "Darwin (UTC+09:30)",
            "Adelaide (UTC+09:30)",
            "Brisbane (UTC+10:00)",
            "Guam (UTC+10:00)",
            "Hobart (UTC+10:00)",
            "Sydney (UTC+10:00)",
            "Vladivostok (UTC+10:00)",
            "Magadan (UTC+11:00)",
            "Majuro (UTC+12:00)",
            "Fiji (UTC+12:00)",
            "Auckland (UTC+12:00)",
            "Fiji (UTC+12:00)",
            "Tongatapu (UTC+13:00)",
        ]
        
        windows_tz = self._get_windows_timezone()
        if windows_tz:
            try:
                tz = zoneinfo.ZoneInfo(windows_tz)
                now = datetime.now(tz)
                utc_offset = now.utcoffset()
                if utc_offset:
                    offset = utc_offset.total_seconds() / 3600
                    offset_str = f"UTC{int(offset):+d}:00" if offset == int(offset) else f"UTC{offset:+.2f}"
                    windows_display = f"{windows_tz} ({offset_str})"
                    if windows_display not in timezones:
                        timezones.insert(0, f"System: {windows_display}")
            except:
                pass
        
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
                        parsed_tz = self._parse_device_timezone(time_zone)
                        timezone_index = self._find_timezone_index(parsed_tz)
                        if timezone_index >= 0:
                            self.timezone_combo.setCurrentIndex(timezone_index)
                        else:
                            self._set_default_timezone()
                    else:
                        self._set_default_timezone()
                    
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
                timezone_value = self._format_device_timezone(selected_timezone)
                if timezone_value:
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
    
    def _parse_device_timezone(self, timezone_str: str) -> str:
        if not timezone_str:
            return ""
        parts = timezone_str.split(";")
        if len(parts) >= 2:
            utc_offset = parts[1].strip()
            return utc_offset
        return timezone_str
    
    def _format_device_timezone(self, timezone_display: str) -> str:
        if not timezone_display:
            return ""
        tz_name = timezone_display.split("(")[0].strip()
        utc_offset = self._extract_utc_offset(timezone_display)
        if utc_offset:
            return f"{tz_name};{utc_offset};{utc_offset}"
        return timezone_display
    
    def _extract_utc_offset(self, timezone_display: str) -> str:
        if "UTC" in timezone_display:
            utc_part = timezone_display.split("(")[-1].replace(")", "").strip()
            if utc_part.startswith("UTC"):
                offset = utc_part.replace("UTC", "").strip()
                if offset.startswith("+") or offset.startswith("-"):
                    offset_str = offset.replace(".", ":")
                    if ":" not in offset_str:
                        offset_str = f"{offset_str}:00"
                    return f"UTC{offset_str}"
        return ""
    
    def _normalize_timezone_value(self, value: str) -> str:
        if not value:
            return ""
        value = value.strip()
        if ";" in value:
            parts = value.split(";")
            if len(parts) >= 2:
                value = parts[1].strip()
        if value.startswith("UTC+"):
            offset = value[4:]
            try:
                offset_str = offset.replace(".", ":")
                if ":" not in offset_str:
                    offset_str = f"{offset_str}:00"
                return f"UTC+{offset_str}"
            except (ValueError, IndexError):
                return value
        elif value.startswith("UTC-"):
            offset = value[4:]
            try:
                offset_str = offset.replace(".", ":")
                if ":" not in offset_str:
                    offset_str = f"{offset_str}:00"
                return f"UTC-{offset_str}"
            except (ValueError, IndexError):
                return value
        return value
    
    def _find_timezone_index(self, timezone_value: str) -> int:
        timezone_list = [self.timezone_combo.itemText(i) for i in range(self.timezone_combo.count())]
        
        normalized_value = self._normalize_timezone_value(timezone_value)
        
        for i, tz_display in enumerate(timezone_list):
            extracted = self._extract_timezone_value(tz_display)
            normalized_extracted = self._normalize_timezone_value(extracted)
            if normalized_value == normalized_extracted or timezone_value in tz_display:
                return i
        return -1
    
    def _extract_timezone_value(self, timezone_display: str) -> str:
        if timezone_display.startswith("System:"):
            parts = timezone_display.split("(")
            if len(parts) > 1:
                tz_name = parts[0].replace("System:", "").strip()
                return tz_name
        
        if "UTC" in timezone_display:
            utc_part = timezone_display.split("(")[-1].replace(")", "").strip()
            if utc_part.startswith("UTC"):
                offset = utc_part.replace("UTC", "").strip()
                if offset.startswith("+") or offset.startswith("-"):
                    offset_str = offset.replace(".", ":")
                    if ":" not in offset_str:
                        offset_str = f"{offset_str}:00"
                    return f"UTC{offset_str}"
        
        return timezone_display.split("(")[0].strip()
    
    def _set_default_timezone(self):
        windows_tz = self._get_windows_timezone()
        if windows_tz:
            try:
                tz = zoneinfo.ZoneInfo(windows_tz)
                now = datetime.now(tz)
                utc_offset = now.utcoffset()
                if utc_offset:
                    offset = utc_offset.total_seconds() / 3600
                    offset_str = f"UTC{int(offset):+d}:00" if offset == int(offset) else f"UTC{offset:+.2f}"
                    windows_display = f"System: {windows_tz} ({offset_str})"
                    timezone_index = self.timezone_combo.findText(windows_display)
                    if timezone_index >= 0:
                        self.timezone_combo.setCurrentIndex(timezone_index)
                        return
            except:
                pass
        
        utc_index = self.timezone_combo.findText("UTC (UTC+00:00)")
        if utc_index >= 0:
            self.timezone_combo.setCurrentIndex(utc_index)
        else:
            self.timezone_combo.setCurrentIndex(0)
    
    def closeEvent(self, event):
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        event.accept()

