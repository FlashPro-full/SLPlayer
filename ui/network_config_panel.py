"""
Network configuration panel
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional


class NetworkConfigPanel(QWidget):
    """Panel for network configuration"""
    
    config_changed = pyqtSignal(dict)  # Emits when config changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # IP Configuration Group
        ip_group = QGroupBox("IP Configuration")
        ip_layout = QVBoxLayout()
        
        ip_input_layout = QHBoxLayout()
        ip_input_layout.addWidget(QLabel("IP Address:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.100")
        ip_input_layout.addWidget(self.ip_input)
        ip_layout.addLayout(ip_input_layout)
        
        mask_input_layout = QHBoxLayout()
        mask_input_layout.addWidget(QLabel("Subnet Mask:"))
        self.mask_input = QLineEdit()
        self.mask_input.setPlaceholderText("255.255.255.0")
        mask_input_layout.addWidget(self.mask_input)
        ip_layout.addLayout(mask_input_layout)
        
        gateway_input_layout = QHBoxLayout()
        gateway_input_layout.addWidget(QLabel("Gateway:"))
        self.gateway_input = QLineEdit()
        self.gateway_input.setPlaceholderText("192.168.1.1")
        gateway_input_layout.addWidget(self.gateway_input)
        ip_layout.addLayout(gateway_input_layout)
        
        read_btn = QPushButton("Read from Controller")
        read_btn.clicked.connect(self.read_config)
        ip_layout.addWidget(read_btn)
        
        ip_group.setLayout(ip_layout)
        layout.addWidget(ip_group)
        
        # Wi-Fi Configuration Group
        wifi_group = QGroupBox("Wi-Fi Configuration")
        wifi_layout = QVBoxLayout()
        
        ssid_layout = QHBoxLayout()
        ssid_layout.addWidget(QLabel("SSID:"))
        self.ssid_input = QLineEdit()
        self.ssid_input.setPlaceholderText("Wi-Fi Network Name")
        ssid_layout.addWidget(self.ssid_input)
        wifi_layout.addLayout(ssid_layout)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.wifi_password_input = QLineEdit()
        self.wifi_password_input.setPlaceholderText("Wi-Fi Password")
        self.wifi_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.wifi_password_input)
        wifi_layout.addLayout(password_layout)
        
        wifi_group.setLayout(wifi_layout)
        layout.addWidget(wifi_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        self.apply_btn = QPushButton("Apply Configuration")
        self.apply_btn.clicked.connect(self.apply_config)
        actions_layout.addWidget(self.apply_btn)
        
        self.reboot_btn = QPushButton("Reboot Controller")
        self.reboot_btn.clicked.connect(self.reboot_controller)
        actions_layout.addWidget(self.reboot_btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set current controller"""
        self.controller = controller
        enabled = controller is not None
        self.apply_btn.setEnabled(enabled)
        self.reboot_btn.setEnabled(enabled)
        if controller:
            self.read_config()
    
    def read_config(self):
        """Read network configuration from controller"""
        if not self.controller:
            QMessageBox.warning(self, "No Controller", "Please connect to a controller first")
            return
        
        # Read IP configuration from controller
        # For now, use placeholder values
        # In real implementation, would query controller
        pass
    
    def apply_config(self):
        """Apply network configuration to controller"""
        if not self.controller:
            QMessageBox.warning(self, "No Controller", "Please connect to a controller first")
            return
        
        config = {
            "ip": self.ip_input.text().strip(),
            "mask": self.mask_input.text().strip(),
            "gateway": self.gateway_input.text().strip(),
            "wifi": {
                "ssid": self.ssid_input.text().strip(),
                "password": self.wifi_password_input.text()
            }
        }
        
        # Validate
        if not config["ip"]:
            QMessageBox.warning(self, "Invalid Config", "Please enter an IP address")
            return
        
        # Apply to controller
        self.config_changed.emit(config)
        QMessageBox.information(self, "Success", "Configuration applied successfully")
    
    def reboot_controller(self):
        """Reboot the controller"""
        if not self.controller:
            QMessageBox.warning(self, "No Controller", "Please connect to a controller first")
            return
        
        reply = QMessageBox.question(
            self, "Reboot Controller",
            "Are you sure you want to reboot the controller?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Send reboot command to controller
            self.config_changed.emit({"action": "reboot"})
            QMessageBox.information(self, "Reboot", "Reboot command sent to controller")

