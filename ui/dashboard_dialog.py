"""
Dashboard Dialog - Shows all detected displays/controllers
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from typing import List, Optional
from core.controller_discovery import ControllerDiscovery, ControllerInfo
from controllers.base_controller import BaseController, ControllerType
from controllers.novastar import NovaStarController
from controllers.huidu import HuiduController
from utils.logger import get_logger

logger = get_logger(__name__)


class DashboardDialog(QDialog):
    """Dashboard showing all detected displays"""
    
    controller_selected = pyqtSignal(str, int, str)  # ip, port, controller_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Controller Dashboard - Detected Displays")
        self.setModal(False)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.discovery = ControllerDiscovery(self)
        self.controllers: List[ControllerInfo] = []
        self.current_controller: Optional[BaseController] = None
        
        self.init_ui()
        self.connect_signals()
        self.start_discovery()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Detected LED Display Controllers")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Discovery status
        status_group = QGroupBox("Discovery Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Scanning network...")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # Controllers table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "IP Address", "Port", "Type", "Name", "Model", "Firmware", "Resolution", "Display Name", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_table_double_click)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Scan")
        refresh_btn.clicked.connect(self.start_discovery)
        button_layout.addWidget(refresh_btn)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.on_connect)
        button_layout.addWidget(connect_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def connect_signals(self):
        """Connect signals"""
        self.discovery.controller_found.connect(self.on_controller_found)
        self.discovery.discovery_finished.connect(self.on_discovery_finished)
    
    def start_discovery(self):
        """Start controller discovery"""
        self.controllers.clear()
        self.table.setRowCount(0)
        self.status_label.setText("Scanning network for controllers...")
        self.progress_bar.setRange(0, 0)
        self.discovery.start_scan()
    
    def on_controller_found(self, controller_info: ControllerInfo):
        """Handle controller found signal"""
        self.controllers.append(controller_info)
        self.update_table()
    
    def on_discovery_finished(self):
        """Handle discovery finished"""
        self.status_label.setText(f"Discovery complete. Found {len(self.controllers)} controller(s).")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if len(self.controllers) == 0:
            self.status_label.setText("No controllers found. Click 'Refresh Scan' to try again.")
    
    def update_table(self):
        """Update controllers table"""
        self.table.setRowCount(len(self.controllers))
        
        for row, controller in enumerate(self.controllers):
            self.table.setItem(row, 0, QTableWidgetItem(controller.ip))
            self.table.setItem(row, 1, QTableWidgetItem(str(controller.port)))
            self.table.setItem(row, 2, QTableWidgetItem(controller.controller_type.upper()))
            self.table.setItem(row, 3, QTableWidgetItem(controller.name or "Unknown"))
            self.table.setItem(row, 4, QTableWidgetItem(controller.model or "Unknown"))
            self.table.setItem(row, 5, QTableWidgetItem(controller.firmware_version or "Unknown"))
            self.table.setItem(row, 6, QTableWidgetItem(controller.display_resolution or "Unknown"))
            self.table.setItem(row, 7, QTableWidgetItem(controller.display_name or "Unknown"))
            
            # Try to connect and get status
            status_item = QTableWidgetItem("Checking...")
            self.table.setItem(row, 8, status_item)
            
            # Try connection in background
            self.check_controller_status(controller, row)
    
    def check_controller_status(self, controller_info: ControllerInfo, row: int):
        """Check controller connection status"""
        try:
            if controller_info.controller_type == "novastar":
                controller = NovaStarController(controller_info.ip, controller_info.port)
            elif controller_info.controller_type == "huidu":
                controller = HuiduController(controller_info.ip, controller_info.port)
            else:
                self.table.item(row, 6).setText("Unknown Type")
                return
            
            if controller.connect():
                device_info = controller.get_device_info()
                if device_info:
                    # Update controller info with device data
                    if "firmware_version" in device_info:
                        controller_info.firmware_version = device_info["firmware_version"]
                    if "resolution" in device_info:
                        controller_info.display_resolution = device_info["resolution"]
                    if "name" in device_info:
                        controller_info.name = device_info["name"]
                    
                    # Update table with device info
                    if controller_info.firmware_version:
                        self.table.item(row, 5).setText(controller_info.firmware_version)
                    if controller_info.display_resolution:
                        self.table.item(row, 6).setText(controller_info.display_resolution)
                    if controller_info.name:
                        self.table.item(row, 3).setText(controller_info.name)
                    if "model" in device_info:
                        self.table.item(row, 4).setText(device_info.get("model", "Unknown"))
                    if "display_name" in device_info:
                        self.table.item(row, 7).setText(device_info.get("display_name", "Unknown"))
                
                self.table.item(row, 8).setText("Connected")
                self.table.item(row, 8).setForeground(Qt.darkGreen)
                controller.disconnect()
            else:
                self.table.item(row, 8).setText("Disconnected")
                self.table.item(row, 8).setForeground(Qt.red)
        except Exception as e:
            logger.error(f"Error checking controller status: {e}")
            self.table.item(row, 8).setText("Error")
            self.table.item(row, 8).setForeground(Qt.red)
    
    def on_table_double_click(self, index):
        """Handle table double-click"""
        self.on_connect()
    
    def on_connect(self):
        """Handle connect button"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a controller to connect.")
            return
        
        row = selected_rows[0].row()
        if row >= len(self.controllers):
            return
        
        controller_info = self.controllers[row]
        self.controller_selected.emit(
            controller_info.ip,
            controller_info.port,
            controller_info.controller_type
        )
        self.accept()
    
    def exec_(self):
        """Override exec_ to return result"""
        return super().exec_()

