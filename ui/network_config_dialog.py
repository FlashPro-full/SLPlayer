from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QFormLayout, QLineEdit, QMessageBox, QTabWidget, QWidget, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional, Dict
from controllers.huidu import HuiduController
from utils.logger import get_logger
import socket
import subprocess
import platform
import re
from pathlib import Path

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
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_and_apply)
        button_layout.addWidget(save_btn)
        
        reboot_btn = QPushButton("🔄 Reboot")
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
        self.subnet_mask_edit.setEnabled(False)
        ip_layout.addRow("Subnet Mask:", self.subnet_mask_edit)
        

        self.gateway_edit = QLineEdit()
        self.gateway_edit.setPlaceholderText("192.168.1.1")
        self.gateway_edit.setEnabled(False)
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
        
        self.mode_edit = QLineEdit()
        self.mode_edit.setPlaceholderText("ap or sta")
        wifi_layout.addRow("Mode:", self.mode_edit)
        
        self.channel_edit = QLineEdit()
        self.channel_edit.setPlaceholderText("1-13")
        wifi_layout.addRow("Channel:", self.channel_edit)
        
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
    
    def _get_system_network_settings(self) -> Dict[str, str]:
        subnet = ""
        gateway = ""
        try:
            system = platform.system()
            if system == "Windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
                output = result.stdout
                
                for line in output.split('\n'):
                    if 'Subnet Mask' in line or 'Subnetmask' in line:
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            subnet = match.group(1)
                    if 'Default Gateway' in line or 'Standardgateway' in line:
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            gateway = match.group(1)
            elif system == "Linux":
                result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
                output = result.stdout
                
                default_route = None
                for line in output.split('\n'):
                    if 'default via' in line:
                        default_route = line
                        match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            gateway = match.group(1)
                        break
                
                result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=5)
                output = result.stdout
                for line in output.split('\n'):
                    if '/24' in line or '/16' in line or '/8' in line:
                        parts = line.strip().split()
                        for part in parts:
                            if '/' in part and '.' in part:
                                ip_with_mask = part.split('/')[0]
                                cidr = part.split('/')[1]
                                subnet = self._cidr_to_subnet(int(cidr))
                                break
            elif system == "Darwin":
                result = subprocess.run(['netstat', '-rn'], capture_output=True, text=True, timeout=5)
                output = result.stdout
                for line in output.split('\n'):
                    if 'default' in line and 'UG' in line:
                        parts = line.split()
                        if len(parts) > 1:
                            gateway = parts[1]
                
                result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=5)
                output = result.stdout
                for line in output.split('\n'):
                    if 'netmask' in line:
                        match = re.search(r'netmask\s+0x([0-9a-fA-F]+)', line)
                        if match:
                            hex_mask = match.group(1)
                            subnet = self._hex_to_subnet(hex_mask)
        except Exception as e:
            logger.error(f"Error getting system network settings: {e}")
        
        return {"subnet": subnet, "gateway": gateway}
    
    def _cidr_to_subnet(self, cidr: int) -> str:
        mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"
    
    def _hex_to_subnet(self, hex_str: str) -> str:
        try:
            mask = int(hex_str, 16)
            return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"
        except:
            return ""
    
    def _update_devicehost_config(self, new_ip: str):
        try:
            config_path = Path(__file__).parent.parent / "publish" / "huidu_sdk" / "config" / "devicehost.config"
            if not config_path.exists():
                logger.warning(f"devicehost.config not found at {config_path}")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                logger.warning("devicehost.config is empty")
                return
            
            parts = content.split('\t,')
            if len(parts) != 2:
                logger.warning(f"Invalid devicehost.config format: {content}")
                return
            
            ip_port_part = parts[0].strip()
            device_id = parts[1].strip()
            
            if ':' in ip_port_part:
                old_ip, port = ip_port_part.rsplit(':', 1)
                new_content = f"{new_ip}:{port}\t,{device_id}"
            else:
                new_content = f"{new_ip}\t,{device_id}"
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Updated devicehost.config with new IP: {new_ip}")
        except Exception as e:
            logger.error(f"Error updating devicehost.config: {e}", exc_info=True)
    
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            system_network = self._get_system_network_settings()
            
            response = self.huidu_controller.get_device_property([self.controller_id], ["eth.dhcp", "eth.ip"])
            
            if response.get("message") == "ok" and response.get("data"):
                device_data_list = response.get("data", [])
                if device_data_list and len(device_data_list) > 0:
                    device_data = device_data_list[0].get("data", {})
                    
                    ip = device_data.get("eth.ip", "")
                    subnet = device_data.get("eth.subnet", system_network.get("subnet", ""))
                    gateway = device_data.get("eth.gateway", system_network.get("gateway", ""))
                    dhcp_str = device_data.get("eth.dhcp", "false")
                    dhcp = dhcp_str == "true" or dhcp_str == True if dhcp_str else False
                    
                    self.ip_address_edit.setText(ip)
                    self.subnet_mask_edit.setText(subnet)
                    self.gateway_edit.setText(gateway)
                    self.dhcp_check.setChecked(dhcp)
                    self.on_dhcp_toggled(dhcp)
                    
            response = self.huidu_controller.get_device_property([self.controller_id], ["wifi.enabled", "wifi.mode", "wifi.ap.ssid", "wifi.ap.passwd", "wifi.ap.channel"])
            
            if response.get("message") == "ok" and response.get("data"):
                device_data_list = response.get("data", [])
                if device_data_list and len(device_data_list) > 0:
                    device_data = device_data_list[0].get("data", {})
                    
                    wifi_enabled_str = device_data.get("wifi.enabled", "false")
                    wifi_enabled = wifi_enabled_str == "true"
                    ssid = device_data.get("wifi.ap.ssid", "")
                    mode = device_data.get("wifi.mode", "")
                    channel = device_data.get("wifi.ap.channel", "")
                    self.enable_wifi_check.setChecked(wifi_enabled)
                    self.ssid_edit.setText(ssid)
                    self.mode_edit.setText(mode)
                    self.channel_edit.setText(channel)
                    
                    password = device_data.get("wifi.ap.passwd", "")
                    self.password_edit.setText(password)
                    
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
                subnet = self.subnet_mask_edit.text().strip()
                if subnet and not self.validate_ip(subnet):
                    QMessageBox.warning(self, "Invalid Subnet Mask", "Please enter a valid subnet mask.")
                    return
                gateway = self.gateway_edit.text().strip()
                if gateway and not self.validate_ip(gateway):
                    QMessageBox.warning(self, "Invalid Gateway", "Please enter a valid gateway address.")
                    return
            
            properties = {}
            
            if self.dhcp_check.isChecked():
                properties["eth.dhcp"] = "true"
            else:
                properties["eth.dhcp"] = "false"
                new_ip = self.ip_address_edit.text().strip()
                properties["eth.ip"] = new_ip
                self._update_devicehost_config(new_ip)
                subnet = self.subnet_mask_edit.text().strip()
                if subnet:
                    properties["eth.subnet"] = subnet
                gateway = self.gateway_edit.text().strip()
                if gateway:
                    properties["eth.gateway"] = gateway
            
            if self.enable_wifi_check.isChecked():
                properties["wifi.enabled"] = "true"
                properties["wifi.ap.ssid"] = self.ssid_edit.text().strip()
                mode = self.mode_edit.text().strip()
                if mode:
                    properties["wifi.mode"] = mode
                channel = self.channel_edit.text().strip()
                if channel:
                    properties["wifi.ap.channel"] = channel
                if self.password_edit.text():
                    properties["wifi.ap.passwd"] = self.password_edit.text()
            else:
                properties["wifi.enabled"] = "false"
            
            response = self.huidu_controller.set_device_property([self.controller_id], properties)
            
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

