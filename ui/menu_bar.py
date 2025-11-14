"""
Menu bar component
"""
from PyQt6.QtWidgets import QMenuBar, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence


class MenuBar(QMenuBar):
    """Application menu bar"""
    
    # Signals
    new_program_requested = pyqtSignal()
    new_from_template_requested = pyqtSignal(str)
    open_program_requested = pyqtSignal(str)
    save_program_requested = pyqtSignal(str)
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    upload_requested = pyqtSignal()
    download_requested = pyqtSignal()
    preview_requested = pyqtSignal()
    dashboard_requested = pyqtSignal()
    discover_controllers_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set menubar color to distinguish it
        self.setStyleSheet("""
            QMenuBar {
                background-color: #E8EAF6;
                padding: 2px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #C5CAE9;
            }
            QMenuBar::item:pressed {
                background-color: #9FA8DA;
            }
        """)
        self.init_menus()
    
    def init_menus(self):
        """Initialize menu items"""
        # File menu
        self.file_menu = self.addMenu("File")
        file_menu = self.file_menu
        
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_program_requested.emit)
        file_menu.addAction(new_action)
        
        # New from Template submenu
        template_menu = file_menu.addMenu("New from Template")
        from core.templates import TemplateManager
        templates = TemplateManager.get_templates()
        for template in templates:
            template_action = QAction(f"{template['icon']} {template['name']}", self)
            template_action.setToolTip(template['description'])
            template_action.triggered.connect(lambda checked, t=template['name']: self.new_from_template_requested.emit(t))
            template_menu.addAction(template_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.on_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.parent().close)
        file_menu.addAction(exit_action)
        
        # Setting menu
        setting_menu = self.addMenu("Setting")
        
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.on_preferences)
        setting_menu.addAction(preferences_action)
        
        display_settings_action = QAction("Display Settings", self)
        display_settings_action.triggered.connect(self.on_display_settings)
        setting_menu.addAction(display_settings_action)
        
        controller_settings_action = QAction("Controller Settings", self)
        controller_settings_action.triggered.connect(self.on_controller_settings)
        setting_menu.addAction(controller_settings_action)
        
        setting_menu.addSeparator()
        
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(self.dashboard_requested.emit)
        setting_menu.addAction(dashboard_action)
        
        # Control menu
        control_menu = self.addMenu("Control")
        
        discover_action = QAction("Discover Controllers...", self)
        discover_action.triggered.connect(self.on_discover_controllers)
        control_menu.addAction(discover_action)
        
        control_menu.addSeparator()
        
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.on_connect)
        control_menu.addAction(connect_action)
        
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.on_disconnect)
        control_menu.addAction(disconnect_action)
        
        control_menu.addSeparator()
        
        upload_action = QAction("Upload", self)
        upload_action.triggered.connect(self.on_upload)
        control_menu.addAction(upload_action)
        
        download_action = QAction("Download", self)
        download_action.triggered.connect(self.on_download)
        control_menu.addAction(download_action)
        
        test_connection_action = QAction("Test Connection", self)
        test_connection_action.triggered.connect(self.on_test_connection)
        control_menu.addAction(test_connection_action)
        
        control_menu.addSeparator()
        
        preview_action = QAction("Preview", self)
        preview_action.setShortcut("F5")
        preview_action.triggered.connect(self.preview_requested.emit)
        control_menu.addAction(preview_action)
        
        # Language menu
        language_menu = self.addMenu("Language")
        
        english_action = QAction("English", self)
        english_action.setCheckable(True)
        english_action.setChecked(True)
        english_action.triggered.connect(lambda: self.on_language_change("en"))
        language_menu.addAction(english_action)
        
        chinese_action = QAction("中文", self)
        chinese_action.setCheckable(True)
        chinese_action.triggered.connect(lambda: self.on_language_change("zh"))
        language_menu.addAction(chinese_action)
        
        # Help menu
        help_menu = self.addMenu("Help")
        
        user_manual_action = QAction("User Manual", self)
        user_manual_action.triggered.connect(self.on_user_manual)
        help_menu.addAction(user_manual_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
        # Update recent files menu
        self.update_recent_files_menu()
    
    def on_open_recent(self, file_path: str):
        """Handle opening a recent file"""
        self.open_program_requested.emit(file_path)
    
    def on_open(self):
        """Handle open file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Program", "",
            "Program Files (*.json);;All Files (*)"
        )
        if file_path:
            self.open_program_requested.emit(file_path)
            # Add to recent files
            self.add_to_recent_files(file_path)
    
    def add_to_recent_files(self, file_path: str):
        """Add file to recent files list"""
        from config.settings import settings
        recent = settings.get("recent_files", [])
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        # Keep only last 10 files
        recent = recent[:10]
        settings.set("recent_files", recent)
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        """Update recent files menu items"""
        from config.settings import settings
        recent = settings.get("recent_files", [])
        
        # Get file menu
        file_menu = self.actions()[0].menu() if self.actions() else None
        if not file_menu:
            # Find file menu by iterating
            for action in self.actions():
                if action.text() == "File":
                    file_menu = action.menu()
                    break
        
        if not file_menu:
            return
        
        # Clear existing recent file actions
        for action in self.recent_file_actions:
            file_menu.removeAction(action)
        self.recent_file_actions.clear()
        
        if recent:
            file_menu.addSeparator()
            for file_path in recent:
                from pathlib import Path
                file_name = Path(file_path).name
                action = file_menu.addAction(file_name)
                action.setData(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.on_open_recent(path))
                self.recent_file_actions.append(action)
    
    def on_save(self):
        """Handle save file"""
        # TODO: Implement file dialog
        self.save_program_requested.emit("")
    
    def on_save_as(self):
        """Handle save as file"""
        # TODO: Implement file dialog
        self.save_program_requested.emit("")
    
    def on_preferences(self):
        """Handle preferences"""
        QMessageBox.information(self, "Preferences", "Preferences dialog - To be implemented")
    
    def on_display_settings(self):
        """Handle display settings"""
        QMessageBox.information(self, "Display Settings", "Display settings dialog - To be implemented")
    
    def on_controller_settings(self):
        """Handle controller settings"""
        QMessageBox.information(self, "Controller Settings", "Controller settings dialog - To be implemented")
    
    # Signals for controller operations
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    upload_requested = pyqtSignal()
    download_requested = pyqtSignal()
    
    def on_connect(self):
        """Handle connect to controller"""
        self.connect_requested.emit()
    
    def on_disconnect(self):
        """Handle disconnect from controller"""
        self.disconnect_requested.emit()
    
    def on_upload(self):
        """Handle upload program"""
        self.upload_requested.emit()
    
    def on_download(self):
        """Handle download program"""
        self.download_requested.emit()
    
    def on_test_connection(self):
        """Handle test connection"""
        from ui.controller_dialog import ControllerDialog
        dialog = ControllerDialog(self)
        if dialog.exec():
            controller = dialog.get_controller()
            if controller and controller.test_connection():
                QMessageBox.information(self, "Success", "Connection test successful!")
            else:
                QMessageBox.warning(self, "Failed", "Connection test failed")
    
    def on_language_change(self, language: str):
        """Handle language change"""
        # TODO: Implement language switching
        print(f"Language changed to: {language}")
    
    def on_user_manual(self):
        """Handle user manual"""
        QMessageBox.information(self, "User Manual", "User manual - To be implemented")
    
    def on_about(self):
        """Handle about dialog"""
        from config.constants import APP_NAME, APP_VERSION
        QMessageBox.about(self, "About", f"{APP_NAME} v{APP_VERSION}\n\nLED Display Controller Program Manager")

