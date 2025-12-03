from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from typing import List, Optional
from core.controller_discovery import ControllerInfo
from services.controller_service import ControllerService
from utils.logger import get_logger

logger = get_logger(__name__)


class DashboardDialog(QDialog):
    
    controller_selected = pyqtSignal(str, int, str)
    
    def __init__(self, parent=None, controller_service: Optional[ControllerService] = None):
        super().__init__(parent)
        self.setWindowTitle("Controller Dashboard - Detected Displays")
        self.setModal(False)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Use provided controller service or get from parent
        if controller_service:
            self.controller_service = controller_service
        elif parent and hasattr(parent, 'controller_service'):
            self.controller_service = parent.controller_service
        else:
            self.controller_service = ControllerService()
        
        self.controllers: List[ControllerInfo] = []
        self._selected_controller_info: Optional[ControllerInfo] = None
        
        self.init_ui()
        self.connect_signals()
        self.start_discovery()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        

        title = QLabel("Detected LED Display Controllers")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        

        status_group = QGroupBox("Discovery Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Scanning network...")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        

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
        # Connect to controller service discovery signals
        self.controller_service.discovery.controller_found.connect(self.on_controller_found)
        self.controller_service.discovery.discovery_finished.connect(self.on_discovery_finished)
    
    def start_discovery(self):
        self.controllers.clear()
        self.table.setRowCount(0)
        self.status_label.setText("Scanning network for controllers...")
        self.progress_bar.setRange(0, 0)
        # Use controller service to discover
        discovered = self.controller_service.discover_controllers(timeout=20)
        if discovered:
            self.controllers = discovered
            self.update_table()
            self.on_discovery_finished()
    
    def on_controller_found(self, controller_info: ControllerInfo):
        self.controllers.append(controller_info)
        self.update_table()
    
    def on_discovery_finished(self):
        self.status_label.setText(f"Discovery complete. Found {len(self.controllers)} controller(s).")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if len(self.controllers) == 0:
            self.status_label.setText("No controllers found. Click 'Refresh Scan' to try again.")
    
    def update_table(self):
        self.table.setRowCount(len(self.controllers))
        
        for row, controller in enumerate(self.controllers):
            self.table.setItem(row, 0, QTableWidgetItem(controller.ip))
            self.table.setItem(row, 1, QTableWidgetItem(str(controller.port)))
            self.table.setItem(row, 2, QTableWidgetItem(controller.controller_type.upper()))
            self.table.setItem(row, 3, QTableWidgetItem(controller.name or "Unknown"))
            self.table.setItem(row, 4, QTableWidgetItem(getattr(controller, 'model', None) or "Unknown"))
            self.table.setItem(row, 5, QTableWidgetItem(controller.firmware_version or "Unknown"))
            self.table.setItem(row, 6, QTableWidgetItem(str(controller.display_resolution) if controller.display_resolution else "Unknown"))
            self.table.setItem(row, 7, QTableWidgetItem(getattr(controller, 'display_name', None) or "Unknown"))
            
            # Status item
            status_item = QTableWidgetItem("Checking...")
            self.table.setItem(row, 8, status_item)
            
            # Check controller status asynchronously
            QTimer.singleShot(100 * (row + 1), lambda r=row, c=controller: self.check_controller_status(c, r))
    
    def check_controller_status(self, controller_info: ControllerInfo, row: int):
        """Check controller status asynchronously"""
        try:
            # Try to connect using controller service
            success = self.controller_service.connect_to_controller(
                controller_info.ip,
                controller_info.port,
                controller_info.controller_type
            )
            
            if success and self.controller_service.current_controller:
                controller = self.controller_service.current_controller
                device_info = controller.get_device_info()
                if device_info:
                    # Update controller info with device data
                    if "firmware_version" in device_info:
                        controller_info.firmware_version = device_info["firmware_version"]
                    if "resolution" in device_info or "display_resolution" in device_info:
                        controller_info.display_resolution = device_info.get("resolution") or device_info.get("display_resolution")
                    if "name" in device_info:
                        controller_info.name = device_info["name"]
                    if "model" in device_info:
                        controller_info.model = device_info["model"]
                    if "display_name" in device_info:
                        controller_info.display_name = device_info["display_name"]
                    
                    # Update table
                    if controller_info.firmware_version:
                        self.table.item(row, 5).setText(controller_info.firmware_version)
                    if controller_info.display_resolution:
                        self.table.item(row, 6).setText(str(controller_info.display_resolution))
                    if controller_info.name:
                        self.table.item(row, 3).setText(controller_info.name)
                    if controller_info.model:
                        self.table.item(row, 4).setText(controller_info.model)
                    if controller_info.display_name:
                        self.table.item(row, 7).setText(controller_info.display_name)
                
                self.table.item(row, 8).setText("Connected")
                self.table.item(row, 8).setForeground(Qt.darkGreen)
                # Disconnect after checking
                self.controller_service.disconnect()
            else:
                self.table.item(row, 8).setText("Disconnected")
                self.table.item(row, 8).setForeground(Qt.red)
        except Exception as e:
            logger.error(f"Error checking controller status: {e}", exc_info=True)
            if row < self.table.rowCount():
                self.table.item(row, 8).setText("Error")
                self.table.item(row, 8).setForeground(Qt.red)
    
    def on_table_double_click(self, index):
        self.on_connect()
    
    def on_connect(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a controller to connect.")
            return
        
        row = selected_rows[0].row()
        if row >= len(self.controllers):
            return
        
        controller_info = self.controllers[row]
        # Emit with controller_info as additional parameter
        # Note: pyqtSignal doesn't support optional args, so we'll pass it as a dict
        self.controller_selected.emit(
            controller_info.ip,
            controller_info.port,
            controller_info.controller_type
        )
        # Store controller_info for connection
        self._selected_controller_info = controller_info
        self.accept()
    
    def exec_(self):
        return super().exec_()

