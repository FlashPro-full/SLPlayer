from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QColor
from typing import List, Optional, Dict
from core.controller_database import get_controller_database
from services.controller_service import ControllerService
from controllers.huidu_sdk import HuiduSDK, SDK_AVAILABLE, DEFAULT_HOST
from utils.logger import get_logger
from ui.widgets.loading_spinner import LoadingSpinner

logger = get_logger(__name__)


class DeviceDiscoveryThread(QThread):
    devices_discovered = pyqtSignal(list)
    
    def __init__(self, controller_service: ControllerService):
        super().__init__()
        self.controller_service = controller_service
    
    def run(self):
        try:
            discovered = self.controller_service.discover_controllers(timeout=10)
            self.devices_discovered.emit(discovered)
        except Exception as e:
            logger.error(f"Error in device discovery thread: {e}")
            self.devices_discovered.emit([])


class DeviceSelectionDialog(QDialog):
    
    device_selected = pyqtSignal(str, int, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Device")
        self.setModal(False)
        self.setMinimumWidth(900)
        self.setMinimumHeight(500)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.controller_service = ControllerService()
        self.device_db = get_controller_database()
        self.selected_controller_id = None
        self.selected_ip = None
        self.selected_port = None
        self.selected_type = None
        self.discovery_thread = None
        self.is_admin = False
        self.main_window = None
        
        self.init_ui()
        self.load_devices_from_database()
        self.start_discovery()
    
    def set_main_window(self, main_window):
        self.main_window = main_window
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Select Device")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Discovering devices...")
        
        self.loading_spinner = LoadingSpinner(self, size=20, color="#2196F3")
        self.loading_spinner.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.loading_spinner)
        status_layout.addStretch()
        
        status_group_layout = QVBoxLayout(status_group)
        status_group_layout.addLayout(status_layout)
        
        layout.addWidget(status_group)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name (Device ID)", "IP Address", "Resolution", "Connection Status", "License"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.on_table_double_click)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.start_discovery)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        
        self.license_btn = QPushButton("License")
        self.license_btn.setEnabled(False)
        self.license_btn.clicked.connect(self.on_license)
        button_layout.addWidget(self.license_btn)
        
        self.select_btn = QPushButton("Edit")
        self.select_btn.setDefault(True)
        self.select_btn.setEnabled(False)
        self.select_btn.clicked.connect(self.on_select)
        button_layout.addWidget(self.select_btn)
        
        layout.addLayout(button_layout)
        
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #FFFFFF;
            }
            QTableWidget {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                color: #FFFFFF;
                gridline-color: #555555;
            }
            QTableWidget::item {
                color: #FFFFFF;
                border-bottom: 1px solid #555555;
            }
            QTableWidget::item:hover {
                background-color: #2A60B2;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: #2A60B2;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QTableWidget::item:selected:hover {
                background-color: #2A60B2;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QHeaderView {
                background-color: #3B3B3B;
            }
            QHeaderView::section {
                background-color: #3B3B3B;
                color: #FFFFFF;
                padding: 8px;
                border: 1px solid #555555;
            }
            QTableWidget QHeaderView::section:horizontal {
                background-color: #3B3B3B;
                color: #FFFFFF;
                padding: 8px;
                border: 1px solid #555555;
                border-top: none;
            }
            QTableCornerButton::section {
                background-color: #3B3B3B;
                border: 1px solid #555555;
            }
            QScrollBar:vertical {
                background-color: #2B2B2B;
                width: 15px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar:horizontal {
                background-color: #2B2B2B;
                height: 15px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background-color: #555555;
                min-width: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
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
        """)
    
    def load_devices_from_database(self):
        try:
            controllers = self.device_db.get_all_controllers(active_only=False)
            self.update_table_with_devices(controllers)
            connected_count = sum(1 for c in controllers if c.get('status') == 'connected')
            total_count = len(controllers)
            self.status_label.setText(f"Connected: {connected_count} / Total: {total_count}")
        except Exception as e:
            logger.error(f"Error loading devices from database: {e}")
    
    def start_discovery(self):
        try:
            if self.discovery_thread:
                try:
                    if self.discovery_thread.isRunning():
                        return
                except RuntimeError:
                    self.discovery_thread = None
        except Exception:
            self.discovery_thread = None
        
        self.status_label.setText("Discovering devices...")
        self.loading_spinner.start()
        
        self.discovery_thread = DeviceDiscoveryThread(self.controller_service)
        self.discovery_thread.devices_discovered.connect(self.on_devices_discovered)
        self.discovery_thread.finished.connect(lambda: setattr(self, 'discovery_thread', None))
        self.discovery_thread.start()
    
    def on_devices_discovered(self, discovered_controllers):
        try:
            controllers = self.device_db.get_all_controllers(active_only=False)
            self.update_table_with_devices(controllers)
            connected_count = sum(1 for c in controllers if c.get('status') == 'connected')
            total_count = len(controllers)
            self.status_label.setText(f"Connected: {connected_count} / Total: {total_count}")
            self.loading_spinner.stop()
            
            QTimer.singleShot(500, self.check_connection_statuses)
        except Exception as e:
            logger.error(f"Error processing discovered devices: {e}")
            self.status_label.setText("Error discovering devices")
            self.loading_spinner.stop()
    
    def update_table_with_devices(self, controllers: List[Dict]):
        self.table.setRowCount(len(controllers))
        
        for row, controller in enumerate(controllers):
            device_id = controller.get('controller_id', 'Unknown')
            ip = controller.get('ip_address', 'Unknown')
            resolution = controller.get('display_resolution') or 'Unknown'
            status = controller.get('status', 'disconnected')
            
            self.table.setItem(row, 0, QTableWidgetItem(device_id))
            self.table.setItem(row, 1, QTableWidgetItem(ip))
            self.table.setItem(row, 2, QTableWidgetItem(str(resolution)))
            
            if status == 'connected':
                status_text = "ON"
                status_color = QColor(0, 255, 0)
            else:
                status_text = "OFF"
                status_color = QColor(255, 0, 0)
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(status_color)
            self.table.setItem(row, 3, status_item)
            
            license_file_name = controller.get('license_file_name', '') or ''
            license_item = QTableWidgetItem(license_file_name)
            if license_file_name:
                license_item.setForeground(QColor(0, 255, 0))
            self.table.setItem(row, 4, license_item)
            
            self.table.setRowHeight(row, 30)
    
    def check_connection_statuses(self):
        try:
            controllers = self.device_db.get_all_controllers(active_only=False)
            
            for row in range(self.table.rowCount()):
                device_id_item = self.table.item(row, 0)
                if not device_id_item:
                    continue
                
                device_id = device_id_item.text()
                status_item = self.table.item(row, 3)
                
                controller = next((c for c in controllers if c.get('controller_id') == device_id), None)
                
                if controller:
                    status = controller.get('status', 'disconnected')
                    if status == 'connected':
                        if status_item:
                            status_item.setText("ON")
                            status_item.setForeground(QColor(0, 255, 0))
                        
                        ip = controller.get('ip_address', '')
                        if ip and ip != '0.0.0.0':
                            ip_item = QTableWidgetItem(ip)
                            self.table.setItem(row, 1, ip_item)
                        
                        resolution = controller.get('display_resolution', '')
                        if resolution:
                            resolution_item = QTableWidgetItem(str(resolution))
                            self.table.setItem(row, 2, resolution_item)
                        
                        controller_info = self.device_db.get_controller(device_id)
                        license_file_name = controller_info.get('license_file_name', '') or '' if controller_info else ''
                        license_item = QTableWidgetItem(license_file_name)
                        if license_file_name:
                            license_item.setForeground(QColor(0, 255, 0))
                        self.table.setItem(row, 4, license_item)
                    else:
                        if status_item:
                            status_item.setText("OFF")
                            status_item.setForeground(QColor(255, 0, 0))
                else:
                    if status_item:
                        status_item.setText("OFF")
                        status_item.setForeground(QColor(255, 0, 0))
            
            connected_count = sum(1 for c in controllers if c.get('status') == 'connected')
            total_count = len(controllers)
            self.status_label.setText(f"Connected: {connected_count} / Total: {total_count}")
        except Exception as e:
            logger.error(f"Error checking connection statuses: {e}")
    
    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            self.select_btn.setEnabled(True)
            self.license_btn.setEnabled(True)
        else:
            self.select_btn.setEnabled(False)
            self.license_btn.setEnabled(False)
    
    def on_table_double_click(self, index):
        self.on_select()
    
    def on_select(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a device.")
            return
        
        row = selected_rows[0].row()
        
        device_id_item = self.table.item(row, 0)
        ip_item = self.table.item(row, 1)
        
        if not device_id_item or not ip_item:
            return
        
        device_id = device_id_item.text()
        ip = ip_item.text()
        
        controller_info = self.device_db.get_controller(device_id)
        if controller_info:
            port = controller_info.get('port', 30080)
            controller_type = controller_info.get('controller_type', 'Huidu').lower()
        else:
            port = 30080
            controller_type = 'huidu'
        
        from core.license_manager import LicenseManager
        license_manager = LicenseManager()
        license_file = license_manager.get_license_file_path(device_id)
        
        if not license_file.exists() and not self.is_admin:
            from ui.password_dialog import PasswordDialog
            password_dialog = PasswordDialog(parent=self)
            result = password_dialog.exec()
            
            if result and password_dialog.is_password_correct():
                self.is_admin = True
            else:
                return
        
        self.selected_controller_id = device_id
        self.selected_ip = ip
        self.selected_port = port
        self.selected_type = controller_type
        
        self.device_selected.emit(ip, port, controller_type, device_id)
    
    def on_license(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a device.")
            return
        
        row = selected_rows[0].row()
        
        device_id_item = self.table.item(row, 0)
        
        if not device_id_item:
            return
        
        device_id = device_id_item.text()
        
        controller_info = self.device_db.get_controller(device_id)
        if not controller_info:
            QMessageBox.warning(self, "Device Not Found", "Device information not found in database.")
            return
        
        from ui.login_dialog import LoginDialog
        login_dialog = LoginDialog(controller_id=device_id, parent=self)
        result = login_dialog.exec()
        
        if result:
            self.load_devices_from_database()
    
    def closeEvent(self, event):
        from PyQt5.QtWidgets import QApplication
        try:
            if self.discovery_thread:
                try:
                    if self.discovery_thread.isRunning():
                        self.discovery_thread.wait(3000)
                        if self.discovery_thread.isRunning():
                            self.discovery_thread.terminate()
                            self.discovery_thread.wait(1000)
                except RuntimeError:
                    pass
        except Exception:
            pass
        QApplication.quit()
        event.accept()

