from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor
from typing import List, Dict
from core.controller_database import get_controller_database
from services.controller_service import get_controller_service
from utils.logger import get_logger
from ui.widgets.loading_spinner import LoadingSpinner
from ui.main_window import MainWindow
from config.settings import settings
from utils.icon_manager import IconManager
from pathlib import Path
import sys
import json

logger = get_logger(__name__)

class ControllerDiscoveryThread(QThread):
    controllers_discovered = pyqtSignal(dict)
    
    def __init__(self, controller_service):
        super().__init__()
        self.controller_service = controller_service
    
    def run(self):
        try:
            discovered = self.controller_service.discover_controllers()
            self.controllers_discovered.emit(discovered)
        except Exception as e:
            logger.error(f"Error in controller discovery thread: {e}")
            self.controllers_discovered.emit({"online_controller_ids": [], "all_controllers": []})


class ControllerDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select controller")
        self.setModal(False)
        self.setMinimumWidth(900)
        self.setMinimumHeight(500)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.controller_service = get_controller_service()
        self.controller_db = get_controller_database()
        self.discovery_thread = None
        self.is_admin = False
        self.main_window = None
        
        self.init_ui()
        self.load_controllers_from_database()
        self.start_discovery()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Select Controller")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Discovering controllers...")
        
        self.loading_spinner = LoadingSpinner(self, size=20, color="#2196F3")
        self.loading_spinner.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.loading_spinner)
        status_layout.addStretch()
        
        status_group_layout = QVBoxLayout(status_group)
        status_group_layout.addLayout(status_layout)
        
        layout.addWidget(status_group)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Controller Type", "Controller ID", "IP Address", "Resolution", "Connection Status", "License"
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
    
    def load_controllers_from_database(self) -> None:
        try:
            online_controller_ids = self.controller_service.online_controller_ids.copy()
            
            controllers: List[Dict] = []
            huidu_controllers = self.controller_db.get_all_huidu_controllers()
            controllers.extend(huidu_controllers)
            
            self.update_table_with_controllers(controllers, online_controller_ids)
        except Exception as e:
            logger.error(f"Error loading controllers from database: {e}")
    
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
        
        self.status_label.setText("Discovering controllers...")
        self.loading_spinner.start()
        
        self.discovery_thread = ControllerDiscoveryThread(self.controller_service)
        self.discovery_thread.controllers_discovered.connect(self.on_controllers_discovered)
        self.discovery_thread.finished.connect(lambda: setattr(self, 'discovery_thread', None))
        self.discovery_thread.start()
    
    def on_controllers_discovered(self, discovered_controllers):
        try:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(200, lambda: self._refresh_table_after_discovery(discovered_controllers))
        except Exception as e:
            logger.error(f"Error processing discovered controllers: {e}")
            self.status_label.setText("Error discovering controllers")
            self.loading_spinner.stop()
    
    def _refresh_table_after_discovery(self, discovered_controllers):
        try:
            controllers = discovered_controllers.get('all_controllers', [])
            online_controller_ids = discovered_controllers.get('online_controller_ids', [])

            self.update_table_with_controllers(controllers, online_controller_ids)
            connected_count = len(online_controller_ids)
            total_count = len(controllers)
            self.status_label.setText(f"Connected: {connected_count} / Total: {total_count}")
            self.loading_spinner.stop()
        except Exception as e:
            logger.error(f"Error refreshing table after discovery: {e}")
            self.status_label.setText("Error refreshing table")
            self.loading_spinner.stop()
    
    def update_table_with_controllers(self, controllers: List[Dict], online_controller_ids: List[str]):
  
        self.table.setRowCount(len(controllers))
        
        for row, controller in enumerate(controllers):
            controller_type = controller.get('controller_type', 'Unknown')
            controller_id = controller.get('controller_id', 'Unknown')
            ip = controller.get('eth_ip', 'Unknown')
            screen_width = controller.get('screen_width')
            screen_height = controller.get('screen_height')
            if screen_width and screen_height:
                resolution = f"{screen_width}x{screen_height}"
            else:
                resolution = 'Unknown'
            
            self.table.setItem(row, 0, QTableWidgetItem(controller_type))
            self.table.setItem(row, 1, QTableWidgetItem(controller_id))
            self.table.setItem(row, 2, QTableWidgetItem(ip))
            self.table.setItem(row, 3, QTableWidgetItem(resolution))
            
            is_online = controller_id in online_controller_ids
            if is_online:
                status_text = "ON"
                status_color = QColor(0, 255, 0)
            else:
                status_text = "OFF"
                status_color = QColor(255, 0, 0)
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(status_color)
            self.table.setItem(row, 4, status_item)
            
            license_file_name = controller.get('license_file_name', '') or ''
            license_item = QTableWidgetItem(license_file_name)
            if license_file_name:
                license_item.setForeground(QColor(0, 255, 0))
            self.table.setItem(row, 5, license_item)
            
            self.table.setRowHeight(row, 30)
        
        connected_count = len(online_controller_ids)
        total_count = len(controllers)
        self.status_label.setText(f"Connected: {connected_count} / Total: {total_count}")
    
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
            QMessageBox.warning(self, "No Selection", "Please select a controller.")
            return
        
        row = selected_rows[0].row()
        
        controller_type_item = self.table.item(row, 0)
        controller_id_item = self.table.item(row, 1)
        controller_resolution_item = self.table.item(row, 3)
        controller_status_item = self.table.item(row, 4)
        
        controller_type = controller_type_item.text()
        controller_id = controller_id_item.text()
        resolution_text = controller_resolution_item.text()
        resolution_parts = resolution_text.split("x")
        width_str = resolution_parts[0] if len(resolution_parts) > 0 else "1920"
        height_str = resolution_parts[1] if len(resolution_parts) > 1 else "1080"
        try:
            width = int(width_str) if width_str.isdigit() else 1920
        except (ValueError, AttributeError):
            width = 1920
        try:
            height = int(height_str) if height_str.isdigit() else 1080
        except (ValueError, AttributeError):
            height = 1080
        is_online = controller_status_item.text() == "ON"
        
        from core.license_manager import LicenseManager
        license_manager = LicenseManager()
        license_file = license_manager.get_license_file_path(controller_id)
        
        if not license_file.exists() and not self.is_admin:
            from ui.password_dialog import PasswordDialog
            password_dialog = PasswordDialog(parent=self)
            result = password_dialog.exec()
            
            if result and password_dialog.is_password_correct():
                self.is_admin = True
            else:
                return
        
        controllerType = controller_type + " " + controller_id.split("-")[0]
 
        if is_online:
            reply = QMessageBox.question(
                self.main_window,
                "Upload Program",
                "Do you want to upload the program from the device?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                try:
                    from controllers.huidu import HuiduController
                    from utils.app_data import get_app_data_dir
                    
                    controller = HuiduController()
                    response = controller.get_programs([controller_id])
                    
                    if response.get("message") == "ok":
                        response_data = response.get("data")
                        xml_string = None
                        
                        if isinstance(response_data, str):
                            try:
                                json_data = json.loads(response_data)
                                xml_string = json_data.get("raw") or json_data.get("xml") or json_data.get("data") or response_data
                            except (json.JSONDecodeError, AttributeError):
                                xml_string = response_data
                        
                        elif isinstance(response_data, dict):
                            xml_string = response_data.get("raw") or response_data.get("xml") or response_data.get("data")
                        elif isinstance(response_data, list) and len(response_data) > 0:
                            first_item = response_data[0]
                            if isinstance(first_item, dict):
                                xml_string = first_item.get("raw") or first_item.get("xml") or first_item.get("data")
                        
                        logger.info(f"XML string: {xml_string}")
                        
                        if not xml_string or not isinstance(xml_string, str):
                            logger.warning(f"Could not extract XML from response: {response}")
                            raise ValueError("Could not extract XML from response")
                        
                        from core.xml_converter import XMLConverter
                        
                        soo_programs, parsed_width, parsed_height = XMLConverter.huidu_xml_to_soo_programs(xml_string, width, height)
                        try:
                            parsed_width_int = int(parsed_width) if isinstance(parsed_width, str) else parsed_width
                            if parsed_width_int > 0:
                                width = parsed_width_int
                        except (ValueError, TypeError):
                            pass
                        try:
                            parsed_height_int = int(parsed_height) if isinstance(parsed_height, str) else parsed_height
                            if parsed_height_int > 0:
                                height = parsed_height_int
                        except (ValueError, TypeError):
                            pass
                        
                        sdk_programs = soo_programs

                        logger.info(f"SDK programs: {sdk_programs}")
                        
                        if sdk_programs:
                            work_dir = get_app_data_dir() / "work"
                            work_dir.mkdir(parents=True, exist_ok=True)
                            soo_file_path = work_dir / f"{controller_id}.soo"
                            
                            if soo_file_path.exists():
                                soo_file_path.unlink()
                            
                            from core.soo_file_config import SOOFileConfig, ScreenPropertiesConfig
                            screen_props = ScreenPropertiesConfig(
                                screen_name=controller_id,
                                width=width,
                                height=height,
                                controller_type=controllerType
                            )
                            file_config = SOOFileConfig(
                                screen_properties=screen_props,
                                programs=sdk_programs
                            )
                            
                            with open(soo_file_path, 'w', encoding='utf-8') as f:
                                json.dump(file_config.to_dict(), f, indent=2, ensure_ascii=False)

                except Exception as e:
                    logger.error(f"Error uploading programs to device {controller_id}: {e}", exc_info=True)
    
        try:
            if self.main_window:
                self.main_window.close()
                self.main_window = None
            
            window_width = settings.get("window.width", 1400)
            window_height = settings.get("window.height", 900)
            window_x = settings.get("window.x", 100)
            window_y = settings.get("window.y", 100)
            
            self.main_window = MainWindow()
            self.main_window.resize(window_width, window_height)
            self.main_window.move(window_x, window_y)
            
            if getattr(sys, 'frozen', False):
                base_path = Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent.parent
            IconManager.setup_taskbar_icon(self.main_window, base_path)
            
            from core.screen_config import set_screen_config
            from utils.app_data import get_app_data_dir

            logger.info(f"Setting screen config: {controllerType}, {width}, {height}, 0, None")
            
            set_screen_config(controllerType, width, height, 0, None)
            
            controller_dict = {
                "controller_id": controller_id,
                "controller_type": controller_type,
                "screen_width": width if isinstance(width, int) else (int(width) if str(width).isdigit() else 1920),
                "screen_height": height if isinstance(height, int) else (int(height) if str(height).isdigit() else 1080),
                "is_online": is_online
            }
            self.controller_service.set_current_controller(controller_id, controller_dict)
            
            if self.main_window:
                self.main_window.update_controller(self.controller_service.get_current_controller())
            
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
              
        except Exception as e:
            logger.error(f"Error connecting to device: {e}", exc_info=True)
            if self.main_window:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
    
    def on_license(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a controller.")
            return
        
        row = selected_rows[0].row()
        
        controller_id_item = self.table.item(row, 1)
        
        if not controller_id_item:
            return
        
        controller_id = controller_id_item.text()
        
        from ui.login_dialog import LoginDialog
        login_dialog = LoginDialog(controller_id=controller_id, parent=self)
        result = login_dialog.exec()
        
        if result:
            self.load_controllers_from_database()
    
    def closeEvent(self, event):
        from PyQt5.QtWidgets import QApplication
        if self.main_window:
            self.main_window.close()
            self.main_window = None
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

