"""
Controller connection dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox,
                             QGroupBox, QFormLayout, QListWidget, QListWidgetItem,
                             QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIntValidator
from controllers.base_controller import ConnectionStatus
from controllers.novastar import NovaStarController
from controllers.huidu import HuiduController


class DiscoveryThread(QThread):
    """Thread for network scanning"""
    discovery_complete = pyqtSignal(list)
    
    def __init__(self, discovery):
        super().__init__()
        self.discovery = discovery
    
    def run(self):
        """Run network scan"""
        controllers = self.discovery.scan_network()
        self.discovery_complete.emit(controllers)


class ControllerDialog(QDialog):
    """Dialog for connecting to controllers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.setWindowTitle("Connect to Controller")
        self.setMinimumSize(450, 500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Discovery section
        discovery_label = QLabel("Auto-Discover Controllers:")
        layout.addWidget(discovery_label)
        
        discovery_btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Scan Network")
        self.scan_btn.clicked.connect(self.start_discovery)
        discovery_btn_layout.addWidget(self.scan_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        discovery_btn_layout.addWidget(self.progress_bar)
        layout.addLayout(discovery_btn_layout)
        
        # Discovered controllers list
        self.discovered_list = QListWidget()
        self.discovered_list.setMaximumHeight(150)
        self.discovered_list.itemDoubleClicked.connect(self.on_discovered_item_selected)
        layout.addWidget(QLabel("Discovered Controllers:"))
        layout.addWidget(self.discovered_list)
        
        layout.addWidget(QLabel("Or enter manually:"))
        
        # Controller type selection
        type_group = QGroupBox("Controller Type")
        type_layout = QFormLayout()
        
        self.controller_type_combo = QComboBox()
        self.controller_type_combo.addItems(["NovaStar", "Huidu"])
        self.controller_type_combo.currentIndexChanged.connect(self.on_controller_type_changed)
        type_layout.addRow("Type:", self.controller_type_combo)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Connection settings
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QFormLayout()
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.100")
        conn_layout.addRow("IP Address:", self.ip_input)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("5200")
        self.port_input.setValidator(QIntValidator(1, 65535))
        conn_layout.addRow("Port:", self.port_input)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.connect_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def on_controller_type_changed(self, index: int):
        """Update default port based on selected controller type"""
        if self.controller_type_combo.currentText() == "NovaStar":
            self.port_input.setText("5200")
        elif self.controller_type_combo.currentText() == "Huidu":
            self.port_input.setText("5000")
    
    def start_discovery(self):
        """Start network discovery"""
        from controllers.controller_discovery import ControllerDiscovery
        
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.discovery = ControllerDiscovery()
        self.discovery_thread = DiscoveryThread(self.discovery)
        self.discovery_thread.discovery_complete.connect(self.on_discovery_complete)
        self.discovery_thread.start()
    
    def on_discovery_complete(self, controllers: list):
        """Handle discovery completion"""
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.discovered_list.clear()
        for controller in controllers:
            item_text = f"{controller['type']} - {controller['ip']}:{controller['port']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, controller)
            self.discovered_list.addItem(item)
        
        if controllers:
            QMessageBox.information(self, "Discovery Complete", 
                                  f"Found {len(controllers)} controller(s)")
        else:
            QMessageBox.information(self, "Discovery Complete", 
                                  "No controllers found on network")
    
    def on_discovered_item_selected(self, item: QListWidgetItem):
        """Handle selection of discovered controller"""
        controller_data = item.data(Qt.ItemDataRole.UserRole)
        if controller_data:
            self.controller_type_combo.setCurrentText(controller_data["type"])
            self.ip_input.setText(controller_data["ip"])
            self.port_input.setText(str(controller_data["port"]))
    
    def test_connection(self):
        """Test connection to controller"""
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Error", "Please enter an IP address")
            return
        
        try:
            port = int(self.port_input.text() or "5200")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid port number")
            return
        
        controller_type = self.controller_type_combo.currentText()
        
        # Create temporary controller for testing
        if controller_type == "NovaStar":
            test_controller = NovaStarController(ip, port)
        else:
            test_controller = HuiduController(ip, port)
        
        if test_controller.test_connection():
            QMessageBox.information(self, "Success", "Connection test successful!")
        else:
            QMessageBox.warning(self, "Failed", "Could not connect to controller. Please check IP address and port.")
    
    def get_controller(self):
        """Get the configured controller"""
        ip = self.ip_input.text().strip()
        if not ip:
            return None
        
        try:
            port = int(self.port_input.text() or "5200")
        except ValueError:
            return None
        
        controller_type = self.controller_type_combo.currentText()
        
        if controller_type == "NovaStar":
            return NovaStarController(ip, port)
        else:
            return HuiduController(ip, port)

