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
from utils.xml_converter import XMLToJSONConverter

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
        timezone_list = [
            "(UTC-11:00) Midway Island",
            "(UTC-10:00) Honolulu",
            "(UTC-09:00) Anchorage",
            "(UTC-08:00) Los Angeles",
            "(UTC-08:00) Tijuana",
            "(UTC-07:00) Phoenix",
            "(UTC-07:00) Chihuahua",
            "(UTC-07:00) Denver",
            "(UTC-06:00) Costa Rica",
            "(UTC-06:00) Regina",
            "(UTC-06:00) Mexico City",
            "(UTC-06:00) Chicago",
            "(UTC-05:00) Bogota",
            "(UTC-05:00) New York",
            "(UTC-04:30) Caracas",
            "(UTC-04:00) Barbados",
            "(UTC-04:00) Manaus",
            "(UTC-04:00) San Diego",
            "(UTC-03:30) Newfoundland",
            "(UTC-03:00) Buenos Aires",
            "(UTC-03:00) Montevideo",
            "(UTC-03:00) Sao Paulo",
            "(UTC-03:00) Gothab",
            "(UTC-02:00) South Georgia",
            "(UTC-01:00) Azores",
            "(UTC-01:00) Cape Verde",
            "(UTC+00:00) London",
            "(UTC+00:00) Casablanca",
            "(UTC+01.00) Brazavi",
            "(UTC+01:00) Amsterdam",
            "(UTC+01:00) Belgrade",
            "(UTC+01:00) Brussels",
            "(UTC+01:00) Sarajevo",
            "(UTC+02:00) Windhoek",
            "(UTC+02:00) Cairo",
            "(UTC+02:00) Athens",
            "(UTC+02:00) Harare, Pretoria",
            "(UTC+02:00) Amman",
            "(UTC+02:00) Athens",
            "(UTC+02:00) Beirut",
            "(UTC+02:00) Helsinki",
            "(UTC+02:00) Jerusalem",
            "(UTC+03:00) Minsk",
            "(UTC+03:00) Baghdad",
            "(UTC+03:00) Kuwait",
            "(UTC+03:00) Nairobi",
            "(UTC+03:00) Moscow",
            "(UTC+03:30) Tehran",
            "(UTC+04:00) Tbilisi",
            "(UTC+04:00) Yerevan",
            "(UTC+04:00) Dubai",
            "(UTC+04:00) Baku",
            "(UTC+04:30) Kabul",
            "(UTC+05:00) Karachi",
            "(UTC+05:00) Ural",
            "(UTC+05:00) Yekaterinburg",
            "(UTC+05:30) Calcutta",
            "(UTC+05:30) Colombo",
            "(UTC+05:45) Kathmandu",
            "(UTC+06:00) Almaty",
            "(UTC+06:30) Yangon",
            "(UTC+07:00) Bangkok",
            "(UTC+07:00) Krasnoyarsk",
            "(UTC+08:00) Beijing",
            "(UTC+08:00) Hong Kong",
            "(UTC+08:00) Kuala Lumpur",
            "(UTC+08:00) Perth",
            "(UTC+08:00) Taipei",
            "(UTC+08:00) Irkutsk",
            "(UTC+09:00) Seoul",
            "(UTC+09:00) Tokyo",
            "(UTC+09:00) Yakutsk",
            "(UTC+09:30) Darwin",
            "(UTC+09:30) Adelaide",
            "(UTC+10:00) Brisbane",
            "(UTC+10:00) Guam",
            "(UTC+10:00) Hobart",
            "(UTC+10:00) Sydney",
            "(UTC+10:00) Vladivostok",
            "(UTC+11:00) Magadan",
            "(UTC+12:00) Majuro",
            "(UTC+12:00) Fiji",
            "(UTC+12:00) Auckland",
            "(UTC+12:00) Fiji",
            "(UTC+13:00) Tongatapu",
        ]

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
    
    def update_time_display(self):
        self.current_time_label.setText("Current PC Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            response = self.huidu_controller.get_time_info([self.controller_id])
            
            if response.get("message") == "ok" and response.get("data"):
                time_info_list = response.get("data", [])
                if time_info_list and len(time_info_list) > 0:
                    xml_string = time_info_list[0].get("data", {})
                    data = XMLToJSONConverter.convert(xml_string)
                    output = data.get("out", {})
                    time_sync = output.get("sync", {})
                    time_sync_value = time_sync.get("value", "none")
                    
                    if time_sync_value == "ntp":
                        self.sync_method_combo.setCurrentIndex(1)
                    else:
                        self.sync_method_combo.setCurrentIndex(0)
                    
                    time_zone = output.get("timezone", {})
                    
                    if time_zone:
                        time_zone_value = time_zone.get("value", "")
                        time_zone_id = time_zone.get("id", "")
                        timeZone = "(" + time_zone_value + ") " + time_zone_id.split("/")[1]
                        for timezone in self.timezone_combo.items():
                            if timezone.text() == timeZone:
                                self.timezone_combo.setCurrentIndex(timezone.get("index"))
                                break
                    else:
                        self._set_default_timezone()
                    
                    logger.info(f"Loaded time settings from device: {time_info}")
        except Exception as e:
            logger.error(f"Error loading time settings from device: {e}", exc_info=True)
    
    def save_and_send(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            use_ntp = self.sync_method_combo.currentIndex() == 1
            
            selected_sync = "ntp" if use_ntp else "none"
            
            selected_timezone = self.timezone_combo.currentText()
            
            response = self.huidu_controller.set_time_info([self.controller_id], selected_sync, selected_timezone)
            
            if response.get("message") == "ok" and response.get("data").get("message") == "ok":
                QMessageBox.information(self, "Success", "Time settings saved and sent to controller.")
                self.accept()
            else:
                error_msg = response.get("data").get("message", "Unknown error")
                QMessageBox.warning(self, "Failed", f"Failed to save time settings: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")
   
    def _set_default_timezone(self):
        utc_index = self.timezone_combo.findText("(UTC+00:00) London")
        if utc_index >= 0:
            self.timezone_combo.setCurrentIndex(utc_index)
        else:
            self.timezone_combo.setCurrentIndex(0)
    
    def closeEvent(self, event):
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        event.accept()

