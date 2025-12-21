from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from datetime import datetime
from typing import Optional, Dict, Any, List
from controllers.huidu import HuiduController
from utils.logger import get_logger

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
        
        self.setWindowTitle(f"⏰ Time Settings" + (f" - {screen_name}" if screen_name else ""))
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
        self.sync_method_combo.addItems(["PC Time", "NTP Server (it.pool.ntp.org)"])
        method_layout.addWidget(self.sync_method_combo)
        sync_layout.addLayout(method_layout)
        
        sync_btn = QPushButton("🔄 Sync Time Now")
        sync_btn.clicked.connect(self.sync_time)
        sync_layout.addWidget(sync_btn)
        
        layout.addWidget(sync_group)
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
            response = self.huidu_controller.get_device_property([self.controller_id])
            
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
            
            if "time.timeZone" in self.time_settings:
                properties["time.timeZone"] = self.time_settings["time.timeZone"]
            
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

