"""
Diagnostics and logging panel
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QTextEdit, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
import json


class DiagnosticsPanel(QWidget):
    """Panel for diagnostics and logging"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.log_entries: List[Dict] = []
        self.init_ui()
        self.start_log_timer()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs for different diagnostic views
        tabs = QTabWidget()
        
        # Connection Test Tab
        connection_tab = QWidget()
        connection_layout = QVBoxLayout(connection_tab)
        
        test_group = QGroupBox("Connection Test")
        test_layout = QVBoxLayout()
        
        self.test_result_label = QLabel("Status: Not tested")
        test_layout.addWidget(self.test_result_label)
        
        test_btn_layout = QHBoxLayout()
        test_btn_layout.addStretch()
        
        ping_btn = QPushButton("Ping Controller")
        ping_btn.clicked.connect(self.test_ping)
        test_btn_layout.addWidget(ping_btn)
        
        test_connection_btn = QPushButton("Test Connection")
        test_connection_btn.clicked.connect(self.test_connection)
        test_btn_layout.addWidget(test_connection_btn)
        
        test_layout.addLayout(test_btn_layout)
        test_group.setLayout(test_layout)
        connection_layout.addWidget(test_group)
        
        connection_layout.addStretch()
        tabs.addTab(connection_tab, "Connection")
        
        # Event Log Tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        log_group = QGroupBox("Event Log")
        log_group_layout = QVBoxLayout()
        
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Level", "Source", "Message"])
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.log_table.setAlternatingRowColors(True)
        log_group_layout.addWidget(self.log_table)
        
        log_btn_layout = QHBoxLayout()
        log_btn_layout.addStretch()
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        log_btn_layout.addWidget(clear_log_btn)
        
        export_log_btn = QPushButton("Export Log")
        export_log_btn.clicked.connect(self.export_log)
        log_btn_layout.addWidget(export_log_btn)
        
        log_group_layout.addLayout(log_btn_layout)
        log_group.setLayout(log_group_layout)
        log_layout.addWidget(log_group)
        
        tabs.addTab(log_tab, "Event Log")
        
        # Backup/Restore Tab
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        
        backup_group = QGroupBox("Backup & Restore")
        backup_group_layout = QVBoxLayout()
        
        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.addStretch()
        
        create_backup_btn = QPushButton("Create Backup")
        create_backup_btn.clicked.connect(self.create_backup)
        backup_btn_layout.addWidget(create_backup_btn)
        
        restore_backup_btn = QPushButton("Restore Backup")
        restore_backup_btn.clicked.connect(self.restore_backup)
        backup_btn_layout.addWidget(restore_backup_btn)
        
        backup_group_layout.addLayout(backup_btn_layout)
        
        export_user_data_btn = QPushButton("Export User Data")
        export_user_data_btn.clicked.connect(self.export_user_data)
        backup_group_layout.addWidget(export_user_data_btn)
        
        import_user_data_btn = QPushButton("Import User Data")
        import_user_data_btn.clicked.connect(self.import_user_data)
        backup_group_layout.addWidget(import_user_data_btn)
        
        backup_group.setLayout(backup_group_layout)
        backup_layout.addWidget(backup_group)
        backup_layout.addStretch()
        
        tabs.addTab(backup_tab, "Backup/Restore")
        
        layout.addWidget(tabs)
    
    def set_controller(self, controller):
        """Set current controller"""
        self.controller = controller
    
    def start_log_timer(self):
        """Start timer to update log display"""
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_log_display)
        self.log_timer.start(1000)  # Update every second
    
    def test_ping(self):
        """Test ping to controller"""
        if not self.controller:
            self.add_log("ERROR", "Diagnostics", "No controller connected")
            self.test_result_label.setText("Status: No controller connected")
            return
        
        if self.controller.test_connection():
            self.add_log("INFO", "Connection", "Ping successful")
            self.test_result_label.setText("Status: Ping successful ✓")
        else:
            self.add_log("ERROR", "Connection", "Ping failed")
            self.test_result_label.setText("Status: Ping failed ✗")
    
    def test_connection(self):
        """Test full connection to controller"""
        if not self.controller:
            self.add_log("ERROR", "Diagnostics", "No controller connected")
            return
        
        self.add_log("INFO", "Connection", "Testing connection...")
        if self.controller.connect():
            info = self.controller.get_device_info()
            if info:
                self.add_log("INFO", "Connection", f"Connected to {info.get('name', 'Controller')}")
                self.test_result_label.setText(f"Status: Connected to {info.get('name', 'Controller')} ✓")
            else:
                self.add_log("WARNING", "Connection", "Connected but could not get device info")
        else:
            self.add_log("ERROR", "Connection", "Connection failed")
            self.test_result_label.setText("Status: Connection failed ✗")
    
    def add_log(self, level: str, source: str, message: str):
        """Add log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message
        }
        self.log_entries.append(entry)
        # Keep only last 1000 entries
        if len(self.log_entries) > 1000:
            self.log_entries.pop(0)
    
    def update_log_display(self):
        """Update log table display"""
        self.log_table.setRowCount(len(self.log_entries))
        for i, entry in enumerate(self.log_entries):
            self.log_table.setItem(i, 0, QTableWidgetItem(entry["timestamp"][:19]))
            self.log_table.setItem(i, 1, QTableWidgetItem(entry["level"]))
            self.log_table.setItem(i, 2, QTableWidgetItem(entry["source"]))
            self.log_table.setItem(i, 3, QTableWidgetItem(entry["message"]))
    
    def clear_log(self):
        """Clear log entries"""
        self.log_entries.clear()
        self.log_table.setRowCount(0)
    
    def export_log(self):
        """Export log to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "", "JSON Files (*.json);;Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.log_entries, f, indent=2, ensure_ascii=False)
                self.add_log("INFO", "Export", f"Log exported to {file_path}")
            except Exception as e:
                self.add_log("ERROR", "Export", f"Failed to export log: {e}")
    
    def create_backup(self):
        """Create complete backup"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create Backup", "", "Backup Files (*.backup);;All Files (*)"
        )
        if file_path:
            self.add_log("INFO", "Backup", f"Creating backup: {file_path}")
            try:
                from core.backup_restore import BackupRestore
                from core.program_manager import ProgramManager
                from core.media_library import MediaLibrary
                from config.settings import settings
                
                backup_restore = BackupRestore()
                program_manager = ProgramManager()
                media_library = MediaLibrary()
                
                if backup_restore.create_backup(program_manager, media_library, settings, file_path):
                    self.add_log("INFO", "Backup", "Backup created successfully")
                    QMessageBox.information(self, "Success", "Backup created successfully")
                else:
                    self.add_log("ERROR", "Backup", "Failed to create backup")
                    QMessageBox.warning(self, "Failed", "Could not create backup")
            except Exception as e:
                self.add_log("ERROR", "Backup", f"Error creating backup: {e}")
                QMessageBox.warning(self, "Error", f"Error creating backup: {e}")
    
    def restore_backup(self):
        """Restore from backup"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Restore Backup", "", "Backup Files (*.backup);;All Files (*)"
        )
        if file_path:
            reply = QMessageBox.question(
                self, "Restore Backup",
                "This will replace all current data. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.add_log("INFO", "Restore", f"Restoring from backup: {file_path}")
                try:
                    from core.backup_restore import BackupRestore
                    from core.program_manager import ProgramManager
                    from core.media_library import MediaLibrary
                    
                    backup_restore = BackupRestore()
                    program_manager = ProgramManager()
                    media_library = MediaLibrary()
                    
                    if backup_restore.restore_backup(file_path, program_manager, media_library):
                        self.add_log("INFO", "Restore", "Backup restored successfully")
                        QMessageBox.information(self, "Success", "Backup restored successfully. Please restart the application.")
                    else:
                        self.add_log("ERROR", "Restore", "Failed to restore backup")
                        QMessageBox.warning(self, "Failed", "Could not restore backup")
                except Exception as e:
                    self.add_log("ERROR", "Restore", f"Error restoring backup: {e}")
                    QMessageBox.warning(self, "Error", f"Error restoring backup: {e}")
    
    def export_user_data(self):
        """Export user data"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export User Data", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                from core.backup_restore import BackupRestore
                backup_restore = BackupRestore()
                if backup_restore.export_user_data(file_path):
                    self.add_log("INFO", "Export", f"User data exported to {file_path}")
                    QMessageBox.information(self, "Success", "User data exported successfully")
                else:
                    self.add_log("ERROR", "Export", "Failed to export user data")
                    QMessageBox.warning(self, "Failed", "Could not export user data")
            except Exception as e:
                self.add_log("ERROR", "Export", f"Error exporting user data: {e}")
                QMessageBox.warning(self, "Error", f"Error exporting user data: {e}")
    
    def import_user_data(self):
        """Import user data"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import User Data", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            reply = QMessageBox.question(
                self, "Import User Data",
                "This will replace current user data. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    from core.backup_restore import BackupRestore
                    backup_restore = BackupRestore()
                    if backup_restore.import_user_data(file_path):
                        self.add_log("INFO", "Import", f"User data imported from {file_path}")
                        QMessageBox.information(self, "Success", "User data imported successfully. Please restart the application.")
                    else:
                        self.add_log("ERROR", "Import", "Failed to import user data")
                        QMessageBox.warning(self, "Failed", "Could not import user data")
                except Exception as e:
                    self.add_log("ERROR", "Import", f"Error importing user data: {e}")
                    QMessageBox.warning(self, "Error", f"Error importing user data: {e}")

