from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QFormLayout, QLineEdit, QMessageBox, QTabWidget, QWidget, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional, Dict
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
    QLineEdit:focus {
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
    QTabWidget::pane {
        background-color: #2B2B2B;
        border: 1px solid #555555;
    }
    QTabBar::tab {
        background-color: #3B3B3B;
        color: #FFFFFF;
        padding: 8px 16px;
        border: 1px solid #555555;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background-color: #2B2B2B;
        border-bottom: 1px solid #2B2B2B;
    }
    QTabBar::tab:hover {
        background-color: #4B4B4B;
    }
"""


class NetworkConfigDialog(QDialog):
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.controller_id = None
        if controller:
            try:
                self.controller_id = controller.get('controller_id') if isinstance(controller, dict) else (controller.get_controller_id() if hasattr(controller, 'get_controller_id') else None)
            except:
                pass
        
        self.setWindowTitle("🌐 Network Configuration")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.huidu_controller = HuiduController()
        
        self.init_ui()
        self.load_from_device()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        

        tabs = QTabWidget()
        

        ip_tab = self.create_ip_tab()
        tabs.addTab(ip_tab, "🌐 IP Configuration")
        

        wifi_tab = self.create_wifi_tab()
        tabs.addTab(wifi_tab, "📶 Wi-Fi Configuration")
        
        layout.addWidget(tabs)
        

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save & Apply")
        save_btn.clicked.connect(self.save_and_apply)
        button_layout.addWidget(save_btn)
        
        reboot_btn = QPushButton("🔄 Reboot Controller")
        reboot_btn.setStyleSheet("QPushButton { background-color: #F44336; color: white; font-weight: bold; } QPushButton:hover { background-color: #E53935; }")
        reboot_btn.clicked.connect(self.reboot_controller)
        button_layout.addWidget(reboot_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_ip_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        

        ip_group = QGroupBox("IP Address Configuration")
        ip_layout = QFormLayout(ip_group)
        

        self.ip_address_edit = QLineEdit()
        self.ip_address_edit.setPlaceholderText("192.168.1.100")
        ip_layout.addRow("IP Address:", self.ip_address_edit)
        

        self.subnet_mask_edit = QLineEdit()
        self.subnet_mask_edit.setPlaceholderText("255.255.255.0")
        ip_layout.addRow("Subnet Mask:", self.subnet_mask_edit)
        

        self.gateway_edit = QLineEdit()
        self.gateway_edit.setPlaceholderText("192.168.1.1")
        ip_layout.addRow("Gateway:", self.gateway_edit)
        

        self.dhcp_check = QCheckBox("Use DHCP (Automatic IP)")
        self.dhcp_check.toggled.connect(self.on_dhcp_toggled)
        ip_layout.addRow("", self.dhcp_check)
        
        layout.addWidget(ip_group)
        layout.addStretch()
        

        info_label = QLabel("Note: Changes to IP settings may require a controller reboot to take effect.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #AAAAAA; font-style: italic;")
        layout.addWidget(info_label)
        
        return widget
    
    def create_wifi_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        

        wifi_group = QGroupBox("Wi-Fi Settings")
        wifi_layout = QFormLayout(wifi_group)
        

        self.enable_wifi_check = QCheckBox("Enable Wi-Fi")
        wifi_layout.addRow("", self.enable_wifi_check)
        

        self.ssid_edit = QLineEdit()
        self.ssid_edit.setPlaceholderText("Enter Wi-Fi network name")
        wifi_layout.addRow("SSID (Network Name):", self.ssid_edit)
        

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter Wi-Fi password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        wifi_layout.addRow("Password:", self.password_edit)
        

        self.show_password_check = QCheckBox("Show Password")
        self.show_password_check.toggled.connect(
            lambda checked: self.password_edit.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        )
        wifi_layout.addRow("", self.show_password_check)
        
        layout.addWidget(wifi_group)
        layout.addStretch()
        

        info_label = QLabel("Note: Wi-Fi configuration may require a controller reboot to take effect.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #AAAAAA; font-style: italic;")
        layout.addWidget(info_label)
        
        return widget
    
    def on_dhcp_toggled(self, checked: bool):
        enabled = not checked
        self.ip_address_edit.setEnabled(enabled)
        self.subnet_mask_edit.setEnabled(enabled)
        self.gateway_edit.setEnabled(enabled)
    
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            response = self.huidu_controller.get_device_property([self.controller_id])
            
            if response.get("message") == "ok" and response.get("data"):
                device_data_list = response.get("data", [])
                if device_data_list and len(device_data_list) > 0:
                    device_data = device_data_list[0].get("data", {})
                    
                    ip = device_data.get("eth.ip", "")
                    dhcp_str = device_data.get("eth.dhcp", "false")
                    dhcp = dhcp_str == "true" or dhcp_str == True if dhcp_str else False
                    
                    self.ip_address_edit.setText(ip)
                    self.dhcp_check.setChecked(dhcp)
                    self.on_dhcp_toggled(dhcp)
                    
                    wifi_enabled_str = device_data.get("wifi.enabled", "false")
                    wifi_enabled = wifi_enabled_str == "true" or wifi_enabled_str == True if wifi_enabled_str else False
                    ssid = device_data.get("wifi.ap.ssid", "")
                    
                    self.enable_wifi_check.setChecked(wifi_enabled)
                    self.ssid_edit.setText(ssid)
                    
                    logger.info(f"Loaded network settings from device")
        except Exception as e:
            logger.error(f"Error loading network settings from device: {e}", exc_info=True)
    
    def save_and_apply(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            if not self.dhcp_check.isChecked():
                ip = self.ip_address_edit.text().strip()
                if not ip or not self.validate_ip(ip):
                    QMessageBox.warning(self, "Invalid IP", "Please enter a valid IP address.")
                    return
            
            properties = {}
            
            if self.dhcp_check.isChecked():
                properties["eth.dhcp"] = "true"
            else:
                properties["eth.dhcp"] = "false"
                properties["eth.ip"] = self.ip_address_edit.text().strip()
            
            if self.enable_wifi_check.isChecked():
                properties["wifi.enabled"] = "true"
                properties["wifi.ap.ssid"] = self.ssid_edit.text().strip()
                if self.password_edit.text():
                    properties["wifi.ap.passwd"] = self.password_edit.text()
            else:
                properties["wifi.enabled"] = "false"
            
            response = self.huidu_controller.set_device_property(properties, [self.controller_id])
            
            if response.get("message") == "ok":
                reply = QMessageBox.question(
                    self, "Network Changes Applied",
                    "Network settings have been saved.\n\n"
                    "Would you like to reboot the controller now for changes to take effect?\n\n"
                    "Note: You can reboot later using the 'Reboot Controller' button.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.reboot_controller_silent()
                else:
                    QMessageBox.information(self, "Success", 
                                          "Network settings saved. Controller may need to be rebooted for changes to take effect.")
                    self.settings_changed.emit(properties)
                    self.accept()
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Failed", f"Failed to save network settings: {error_msg}")
            
        except Exception as e:
            logger.error(f"Error saving network config: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving network settings: {str(e)}")
    
    def reboot_controller(self):
        """Reboot controller with confirmation dialog"""
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            reply = QMessageBox.question(
                self, "Reboot Controller",
                "Are you sure you want to reboot the controller?\n\n"
                "This will disconnect the current session and the controller will restart.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.reboot_controller_silent()
                    
        except Exception as e:
            logger.error(f"Error rebooting controller: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error rebooting controller: {str(e)}")
    
    def reboot_controller_silent(self):
        """Reboot controller without confirmation (called after network changes)"""
        try:
            if not self.controller_id:
                return
            
            response = self.huidu_controller.reboot_device([self.controller_id])
            
            if response.get("message") == "ok":
                QMessageBox.information(self, "Success", 
                                      "Reboot command sent to controller. It will restart shortly.\n\n"
                                      "You will be disconnected from the controller.")
                self._reboot_triggered = True
                self.accept()
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Failed", f"Failed to send reboot command: {error_msg}")
                    
        except Exception as e:
            logger.error(f"Error rebooting controller: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error rebooting controller: {str(e)}")
    
    def validate_ip(self, ip: str) -> bool:
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except ValueError:
            return False

