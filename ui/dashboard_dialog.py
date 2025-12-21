from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar, QGroupBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QModelIndex
from typing import List, Optional, Dict, Any
from services.controller_service import get_controller_service
from utils.logger import get_logger

logger = get_logger(__name__)


class DashboardDialog(QDialog):
    
    controller_selected = pyqtSignal(str, int, str)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Controller Dashboard - Detected Displays")
        self.setModal(False)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.controller_service = get_controller_service()
        
        self.controllers: List[Dict[str, Any]] = []
        self._selected_controller_info: Optional[Dict[str, Any]] = None
        
        self.init_ui()
        self.connect_signals()
        self.start_discovery()
    
    def init_ui(self) -> None:
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
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.Stretch)
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
    
    def connect_signals(self) -> None:
        pass
    
    def start_discovery(self) -> None:
        self.controllers.clear()
        self.table.setRowCount(0)
        self.status_label.setText("Scanning network for controllers...")
        self.progress_bar.setRange(0, 0)
        # Use controller service to discover
        discovered = self.controller_service.discover_controllers()
        if discovered and discovered.get("all_controllers"):
            self.controllers = discovered["all_controllers"]
            self.update_table()
            self.on_discovery_finished()
    
    def on_controller_found(self, controller_info: Dict[str, Any]) -> None:
        self.controllers.append(controller_info)
        self.update_table()
    
    def on_discovery_finished(self) -> None:
        self.status_label.setText(f"Discovery complete. Found {len(self.controllers)} controller(s).")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if len(self.controllers) == 0:
            self.status_label.setText("No controllers found. Click 'Refresh Scan' to try again.")
    
    def update_table(self) -> None:
        self.table.setRowCount(len(self.controllers))
        
        for row, controller in enumerate(self.controllers):
            self.table.setItem(row, 0, QTableWidgetItem(controller.get('ip', 'Unknown')))
            self.table.setItem(row, 1, QTableWidgetItem(str(controller.get('port', 0))))
            self.table.setItem(row, 2, QTableWidgetItem(controller.get('controller_type', 'Unknown').upper()))
            self.table.setItem(row, 3, QTableWidgetItem(controller.get('name', 'Unknown')))
            self.table.setItem(row, 4, QTableWidgetItem(controller.get('model', 'Unknown')))
            self.table.setItem(row, 5, QTableWidgetItem(controller.get('version_app', controller.get('firmware_version', 'Unknown'))))
            resolution = controller.get('display_resolution') or controller.get('resolution')
            if resolution:
                self.table.setItem(row, 6, QTableWidgetItem(str(resolution)))
            else:
                width = controller.get('screen_width') or controller.get('width')
                height = controller.get('screen_height') or controller.get('height')
                if width and height:
                    self.table.setItem(row, 6, QTableWidgetItem(f"{width}x{height}"))
                else:
                    self.table.setItem(row, 6, QTableWidgetItem("Unknown"))
            self.table.setItem(row, 7, QTableWidgetItem(controller.get('display_name', controller.get('name', 'Unknown'))))
            
            # Status item
            status_item = QTableWidgetItem("Checking...")
            self.table.setItem(row, 8, status_item)
    
    def on_table_double_click(self, index: QModelIndex) -> None:
        self.on_connect()
    
    def on_connect(self) -> None:
        selection_model = self.table.selectionModel()
        if selection_model is None:
            QMessageBox.warning(self, "No Selection", "Please select a controller to connect.")
            return
        
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a controller to connect.")
            return
        
        row = selected_rows[0].row()
        if row >= len(self.controllers):
            return
        
        controller_info = self.controllers[row]
        self.controller_selected.emit(
            controller_info.get('ip', ''),
            controller_info.get('port', 0),
            controller_info.get('controller_type', '')
        )
        self._selected_controller_info = controller_info
        self.accept()
    
    def exec_(self) -> int:
        return super().exec_()

