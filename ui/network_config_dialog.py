from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QFormLayout, QLineEdit, QMessageBox, QTabWidget, QWidget, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkConfigDialog(QDialog):
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Network Configuration")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.init_ui()
        self.read_from_controller()
    
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
        
        read_btn = QPushButton("📥 Read from Controller")
        read_btn.clicked.connect(self.read_from_controller)
        button_layout.addWidget(read_btn)
        
        save_btn = QPushButton("💾 Save & Apply")
        save_btn.clicked.connect(self.save_and_apply)
        button_layout.addWidget(save_btn)
        
        reboot_btn = QPushButton("🔄 Reboot Controller")
        reboot_btn.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; }")
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
        info_label.setStyleSheet("color: #666; font-style: italic;")
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
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        return widget
    
    def on_dhcp_toggled(self, checked: bool):
        enabled = not checked
        self.ip_address_edit.setEnabled(enabled)
        self.subnet_mask_edit.setEnabled(enabled)
        self.gateway_edit.setEnabled(enabled)
    
    def read_from_controller(self):
        try:
            if not self.controller:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            

            if hasattr(self.controller, 'get_network_config'):
                config = self.controller.get_network_config()
                if config:
                    self.ip_address_edit.setText(config.get("ip_address", ""))
                    self.subnet_mask_edit.setText(config.get("subnet_mask", ""))
                    self.gateway_edit.setText(config.get("gateway", ""))
                    self.dhcp_check.setChecked(config.get("dhcp", False))
            

            if hasattr(self.controller, 'get_wifi_config'):
                wifi_config = self.controller.get_wifi_config()
                if wifi_config:
                    self.enable_wifi_check.setChecked(wifi_config.get("enabled", False))
                    self.ssid_edit.setText(wifi_config.get("ssid", ""))


            
            QMessageBox.information(self, "Success", "Network settings read from controller.")
            
        except Exception as e:
            logger.error(f"Error reading network config: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Could not read all network settings: {str(e)}")
    
    def save_and_apply(self):
        try:
            if not self.controller:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            

            if not self.dhcp_check.isChecked():
                ip = self.ip_address_edit.text().strip()
                mask = self.subnet_mask_edit.text().strip()
                gateway = self.gateway_edit.text().strip()
                
                if not ip or not self.validate_ip(ip):
                    QMessageBox.warning(self, "Invalid IP", "Please enter a valid IP address.")
                    return
                
                if not mask or not self.validate_ip(mask):
                    QMessageBox.warning(self, "Invalid Mask", "Please enter a valid subnet mask.")
                    return
                
                if gateway and not self.validate_ip(gateway):
                    QMessageBox.warning(self, "Invalid Gateway", "Please enter a valid gateway address.")
                    return
            

            settings = {
                "ip_config": {
                    "ip_address": self.ip_address_edit.text().strip() if not self.dhcp_check.isChecked() else "",
                    "subnet_mask": self.subnet_mask_edit.text().strip() if not self.dhcp_check.isChecked() else "",
                    "gateway": self.gateway_edit.text().strip() if not self.dhcp_check.isChecked() else "",
                    "dhcp": self.dhcp_check.isChecked()
                },
                "wifi_config": {
                    "enabled": self.enable_wifi_check.isChecked(),
                    "ssid": self.ssid_edit.text().strip(),
                    "password": self.password_edit.text()
                }
            }
            

            if hasattr(self.controller, 'set_network_config'):
                if not self.controller.set_network_config(settings["ip_config"]):
                    QMessageBox.warning(self, "Failed", "Failed to apply IP settings.")
                    return
            

            if hasattr(self.controller, 'set_wifi_config'):
                if not self.controller.set_wifi_config(settings["wifi_config"]):
                    QMessageBox.warning(self, "Failed", "Failed to apply Wi-Fi settings.")
                    return
            
            QMessageBox.information(self, "Success", 
                                  "Network settings saved. Controller may need to be rebooted for changes to take effect.")
            self.settings_changed.emit(settings)
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving network config: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving network settings: {str(e)}")
    
    def reboot_controller(self):
        try:
            if not self.controller:
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
                if hasattr(self.controller, 'reboot'):
                    if self.controller.reboot():
                        QMessageBox.information(self, "Success", 
                                              "Reboot command sent to controller. It will restart shortly.")
                        self.accept()
                    else:
                        QMessageBox.warning(self, "Failed", "Failed to send reboot command.")
                else:
                    QMessageBox.warning(self, "Not Supported", "Controller does not support reboot command.")
                    
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

