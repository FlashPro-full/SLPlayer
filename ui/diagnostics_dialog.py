from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QTextEdit, QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QProgressBar, QSplitter, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from typing import Optional, List, Dict
from datetime import datetime
import subprocess
import platform
from utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)


class PingThread(QThread):
    ping_result = pyqtSignal(str, bool, float)
    
    def __init__(self, host: str):
        super().__init__()
        self.host = host
    
    def run(self):
        try:

            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", "1000", self.host]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", self.host]
            
            start_time = datetime.now()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            end_time = datetime.now()
            
            elapsed_ms = (end_time - start_time).total_seconds() * 1000
            success = result.returncode == 0
            
            self.ping_result.emit(self.host, success, elapsed_ms)
            
        except subprocess.TimeoutExpired:
            self.ping_result.emit(self.host, False, 0.0)
        except Exception as e:
            logger.error(f"Error pinging {self.host}: {e}")
            self.ping_result.emit(self.host, False, 0.0)


class DiagnosticsDialog(QDialog):
    
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Diagnostics & Logs")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        
        self.event_logs = []
        self.error_logs = []
        
        self.init_ui()
        self.load_logs()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        

        tabs = QTabWidget()
        

        connection_tab = self.create_connection_tab()
        tabs.addTab(connection_tab, "🔌 Connection Test")
        

        event_log_tab = self.create_event_log_tab()
        tabs.addTab(event_log_tab, "📋 Event Log")
        

        error_log_tab = self.create_error_log_tab()
        tabs.addTab(error_log_tab, "❌ Error Log")
        

        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, "💾 Backup/Restore")
        
        layout.addWidget(tabs)
        

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_all)
        button_layout.addWidget(refresh_btn)
        
        export_logs_btn = QPushButton("📤 Export Logs")
        export_logs_btn.clicked.connect(self.export_logs)
        button_layout.addWidget(export_logs_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_connection_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        

        test_group = QGroupBox("Connection Test")
        test_layout = QVBoxLayout(test_group)
        

        controller_layout = QHBoxLayout()
        controller_layout.addWidget(QLabel("Controller:"))
        
        self.controller_status_label = QLabel("Not Connected")
        self.controller_status_label.setStyleSheet("color: red; font-weight: bold;")
        controller_layout.addWidget(self.controller_status_label)
        
        test_controller_btn = QPushButton("Test Connection")
        test_controller_btn.clicked.connect(self.test_controller_connection)
        controller_layout.addWidget(test_controller_btn)
        
        controller_layout.addStretch()
        test_layout.addLayout(controller_layout)
        

        ping_group = QGroupBox("Ping Test")
        ping_layout = QVBoxLayout(ping_group)
        
        ping_input_layout = QHBoxLayout()
        ping_input_layout.addWidget(QLabel("Host/IP:"))
        
        self.ping_host_edit = QLineEdit()
        self.ping_host_edit.setPlaceholderText("192.168.1.100")
        if self.controller:
            self.ping_host_edit.setText(self.controller.ip_address)
        ping_input_layout.addWidget(self.ping_host_edit)
        
        ping_btn = QPushButton("Ping")
        ping_btn.clicked.connect(self.test_ping)
        ping_input_layout.addWidget(ping_btn)
        
        ping_layout.addLayout(ping_input_layout)
        
        self.ping_result_label = QLabel("")
        self.ping_result_label.setWordWrap(True)
        ping_layout.addWidget(self.ping_result_label)
        
        test_layout.addWidget(ping_group)
        

        network_group = QGroupBox("Network Information")
        network_layout = QVBoxLayout(network_group)
        
        self.network_info_text = QTextEdit()
        self.network_info_text.setReadOnly(True)
        self.network_info_text.setMaximumHeight(150)
        network_layout.addWidget(self.network_info_text)
        
        refresh_network_btn = QPushButton("🔄 Refresh Network Info")
        refresh_network_btn.clicked.connect(self.refresh_network_info)
        network_layout.addWidget(refresh_network_btn)
        
        test_layout.addWidget(network_group)
        
        layout.addWidget(test_group)
        layout.addStretch()
        
        return widget
    
    def create_event_log_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        

        self.event_log_table = QTableWidget()
        self.event_log_table.setColumnCount(4)
        self.event_log_table.setHorizontalHeaderLabels(["Timestamp", "Type", "Event", "Details"])
        self.event_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.event_log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.event_log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.event_log_table)
        

        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_event_log)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_error_log_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        

        self.error_log_table = QTableWidget()
        self.error_log_table.setColumnCount(4)
        self.error_log_table.setHorizontalHeaderLabels(["Timestamp", "Level", "Error", "Details"])
        self.error_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.error_log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.error_log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.error_log_table)
        

        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_error_log)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_backup_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        

        backup_group = QGroupBox("Backup")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_info = QLabel(
            "Create a complete backup of all programs, media, schedules, "
            "network configurations, and settings."
        )
        backup_info.setWordWrap(True)
        backup_layout.addWidget(backup_info)
        
        create_backup_btn = QPushButton("💾 Create Backup")
        create_backup_btn.clicked.connect(self.create_backup)
        backup_layout.addWidget(create_backup_btn)
        
        layout.addWidget(backup_group)
        

        restore_group = QGroupBox("Restore")
        restore_layout = QVBoxLayout(restore_group)
        
        restore_info = QLabel(
            "Restore from a previously created backup file. "
            "This will replace all current data."
        )
        restore_info.setWordWrap(True)
        restore_layout.addWidget(restore_info)
        
        restore_backup_btn = QPushButton("📥 Restore from Backup")
        restore_backup_btn.clicked.connect(self.restore_backup)
        restore_layout.addWidget(restore_backup_btn)
        
        layout.addWidget(restore_group)
        

        users_group = QGroupBox("User Management")
        users_layout = QVBoxLayout(users_group)
        
        users_info = QLabel("Import or export user data and licenses.")
        users_info.setWordWrap(True)
        users_layout.addWidget(users_info)
        
        users_btn_layout = QHBoxLayout()
        import_users_btn = QPushButton("📥 Import Users")
        import_users_btn.clicked.connect(self.import_users)
        users_btn_layout.addWidget(import_users_btn)
        
        export_users_btn = QPushButton("📤 Export Users")
        export_users_btn.clicked.connect(self.export_users)
        users_btn_layout.addWidget(export_users_btn)
        
        users_layout.addLayout(users_btn_layout)
        layout.addWidget(users_group)
        
        layout.addStretch()
        
        return widget
    
    def test_controller_connection(self):
        try:
            if not self.controller:
                self.controller_status_label.setText("Not Connected")
                self.controller_status_label.setStyleSheet("color: red; font-weight: bold;")
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            

            if self.controller.status.value == "connected":
                self.controller_status_label.setText("Connected ✓")
                self.controller_status_label.setStyleSheet("color: green; font-weight: bold;")
                

                device_info = self.controller.get_device_info()
                if device_info:
                    info_text = f"Controller: {device_info.get('name', 'Unknown')}\n"
                    info_text += f"IP: {self.controller.ip_address}\n"
                    info_text += f"Status: Connected"
                    QMessageBox.information(self, "Connection Test", f"Controller is connected.\n\n{info_text}")
                else:
                    QMessageBox.information(self, "Connection Test", "Controller is connected.")
            else:

                if self.controller.connect():
                    self.controller_status_label.setText("Connected ✓")
                    self.controller_status_label.setStyleSheet("color: green; font-weight: bold;")
                    QMessageBox.information(self, "Connection Test", "Successfully connected to controller.")
                else:
                    self.controller_status_label.setText("Connection Failed")
                    self.controller_status_label.setStyleSheet("color: red; font-weight: bold;")
                    QMessageBox.warning(self, "Connection Test", "Failed to connect to controller.")
                    
        except Exception as e:
            logger.error(f"Error testing controller connection: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error testing connection: {str(e)}")
    
    def test_ping(self):
        host = self.ping_host_edit.text().strip()
        if not host:
            QMessageBox.warning(self, "No Host", "Please enter a host or IP address.")
            return
        
        self.ping_result_label.setText(f"Pinging {host}...")
        self.ping_result_label.setStyleSheet("color: blue;")
        

        self.ping_thread = PingThread(host)
        self.ping_thread.ping_result.connect(self.on_ping_result)
        self.ping_thread.start()
    
    def on_ping_result(self, host: str, success: bool, time_ms: float):
        if success:
            self.ping_result_label.setText(f"✓ {host} is reachable (Response time: {time_ms:.2f} ms)")
            self.ping_result_label.setStyleSheet("color: green;")
        else:
            self.ping_result_label.setText(f"✗ {host} is not reachable or timed out")
            self.ping_result_label.setStyleSheet("color: red;")
    
    def refresh_network_info(self):
        try:
            info_text = ""
            
            if self.controller:
                info_text += f"Controller IP: {self.controller.ip_address}\n"
                info_text += f"Controller Port: {self.controller.port}\n"
                info_text += f"Controller Type: {self.controller.controller_type.value}\n"
                info_text += f"Connection Status: {self.controller.status.value}\n\n"
            

            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            info_text += f"Local Hostname: {hostname}\n"
            info_text += f"Local IP: {local_ip}\n"
            
            self.network_info_text.setText(info_text)
            
        except Exception as e:
            logger.error(f"Error refreshing network info: {e}", exc_info=True)
            self.network_info_text.setText(f"Error: {str(e)}")
    
    def load_logs(self):

        self.refresh_event_log()
        

        self.refresh_error_log()
        

        self.refresh_network_info()
        

        if self.controller:
            if self.controller.status.value == "connected":
                self.controller_status_label.setText("Connected ✓")
                self.controller_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.controller_status_label.setText("Not Connected")
                self.controller_status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def refresh_event_log(self):


        self.event_log_table.setRowCount(len(self.event_logs))
        
        for i, log in enumerate(self.event_logs):
            self.event_log_table.setItem(i, 0, QTableWidgetItem(log.get("timestamp", "")))
            self.event_log_table.setItem(i, 1, QTableWidgetItem(log.get("type", "")))
            self.event_log_table.setItem(i, 2, QTableWidgetItem(log.get("event", "")))
            self.event_log_table.setItem(i, 3, QTableWidgetItem(log.get("details", "")))
    
    def refresh_error_log(self):


        self.error_log_table.setRowCount(len(self.error_logs))
        
        for i, log in enumerate(self.error_logs):
            self.error_log_table.setItem(i, 0, QTableWidgetItem(log.get("timestamp", "")))
            self.error_log_table.setItem(i, 1, QTableWidgetItem(log.get("level", "")))
            self.error_log_table.setItem(i, 2, QTableWidgetItem(log.get("error", "")))
            self.error_log_table.setItem(i, 3, QTableWidgetItem(log.get("details", "")))
    
    def clear_event_log(self):
        reply = QMessageBox.question(
            self, "Clear Event Log",
            "Are you sure you want to clear the event log?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.event_logs.clear()
            self.refresh_event_log()
    
    def clear_error_log(self):
        reply = QMessageBox.question(
            self, "Clear Error Log",
            "Are you sure you want to clear the error log?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.error_logs.clear()
            self.refresh_error_log()
    
    def refresh_all(self):
        self.load_logs()
        QMessageBox.information(self, "Refreshed", "All diagnostics refreshed.")
    
    def export_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=== Event Log ===\n\n")
                    for log in self.event_logs:
                        f.write(f"{log.get('timestamp')} [{log.get('type')}] {log.get('event')}: {log.get('details')}\n")
                    
                    f.write("\n=== Error Log ===\n\n")
                    for log in self.error_logs:
                        f.write(f"{log.get('timestamp')} [{log.get('level')}] {log.get('error')}: {log.get('details')}\n")
                
                QMessageBox.information(self, "Success", f"Logs exported to: {file_path}")
            except Exception as e:
                logger.error(f"Error exporting logs: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Error exporting logs: {str(e)}")
    
    def create_backup(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create Backup", "", "Backup Files (*.backup);;All Files (*)"
        )
        if file_path:
            try:
                from core.backup_restore import BackupRestore
                from core.program_manager import ProgramManager
                

                program_manager = None
                if self.parent() and hasattr(self.parent(), 'program_manager'):
                    program_manager = self.parent().program_manager
                else:
                    program_manager = ProgramManager()
                
                backup_service = BackupRestore()
                if backup_service.create_backup(file_path, program_manager=program_manager):
                    QMessageBox.information(self, "Success", f"Backup created: {file_path}")
                else:
                    QMessageBox.warning(self, "Failed", "Failed to create backup.")
            except Exception as e:
                logger.error(f"Error creating backup: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Error creating backup: {str(e)}")
    
    def restore_backup(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Restore Backup", "", "Backup Files (*.backup);;All Files (*)"
        )
        if file_path:
            reply = QMessageBox.question(
                self, "Restore Backup",
                "This will replace all current data with the backup.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    from core.backup_restore import BackupRestore
                    from core.program_manager import ProgramManager
                    

                    program_manager = None
                    if self.parent() and hasattr(self.parent(), 'program_manager'):
                        program_manager = self.parent().program_manager
                    else:
                        program_manager = ProgramManager()
                    
                    backup_service = BackupRestore()
                    if backup_service.restore_backup(file_path, program_manager=program_manager):
                        QMessageBox.information(self, "Success", "Backup restored successfully.")

                        if self.parent() and hasattr(self.parent(), 'screen_list_panel'):
                            self.parent().screen_list_panel.refresh_screens()
                    else:
                        QMessageBox.warning(self, "Failed", "Failed to restore backup.")
                except Exception as e:
                    logger.error(f"Error restoring backup: {e}", exc_info=True)
                    QMessageBox.critical(self, "Error", f"Error restoring backup: {str(e)}")
    
    def import_users(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Users", "", "User Files (*.users);;All Files (*)"
        )
        if file_path:
            QMessageBox.information(self, "Import Users", f"Import users from: {file_path}\n\n(Implementation pending)")
    
    def export_users(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Users", "", "User Files (*.users);;All Files (*)"
        )
        if file_path:
            QMessageBox.information(self, "Export Users", f"Export users to: {file_path}\n\n(Implementation pending)")

