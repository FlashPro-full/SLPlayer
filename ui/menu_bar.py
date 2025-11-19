from PyQt5.QtWidgets import QMenuBar, QMessageBox, QAction, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from utils.logger import get_logger
from config.i18n import tr, set_language

logger = get_logger(__name__)


class MenuBar(QMenuBar):
    
    new_program_requested = pyqtSignal()
    new_screen_requested = pyqtSignal()
    open_program_requested = pyqtSignal(str)
    save_program_requested = pyqtSignal(str)
    exit_requested = pyqtSignal()
    
    screen_settings_requested = pyqtSignal()
    sync_settings_requested = pyqtSignal()
    
    device_info_requested = pyqtSignal()
    clear_program_requested = pyqtSignal()
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    send_requested = pyqtSignal()
    export_to_usb_requested = pyqtSignal()
    time_power_brightness_requested = pyqtSignal()
    network_config_requested = pyqtSignal()
    diagnostics_requested = pyqtSignal()
    import_requested = pyqtSignal()
    export_requested = pyqtSignal()
    
    language_changed = pyqtSignal(str)
    about_requested = pyqtSignal()
    dashboard_requested = pyqtSignal()
    discover_controllers_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenuBar {
                background-color: #E5E5E5;
                padding: 2px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #D6D6D6;
            }
            QMenuBar::item:pressed {
                background-color: #C5C5C5;
            }
        """)
        self.menus = {}
        self.actions = {}
        self.init_menus()
    
    def init_menus(self):
        file_menu = self.addMenu(tr("menu.file"))
        self.menus["file"] = file_menu
        
        new_action = QAction(tr("action.new"), self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_program_requested.emit)
        file_menu.addAction(new_action)
        self.actions["file.new"] = new_action
        
        open_action = QAction(tr("action.open"), self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        self.actions["file.open"] = open_action
        
        save_action = QAction(tr("action.save"), self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        self.actions["file.save"] = save_action
        
        file_menu.addSeparator()
        exit_action = QAction(tr("action.exit"), self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.on_exit)
        file_menu.addAction(exit_action)
        self.actions["file.exit"] = exit_action
        
        setting_menu = self.addMenu(tr("menu.setting"))
        self.menus["setting"] = setting_menu
        
        screen_action = QAction(tr("action.screen_setting"), self)
        screen_action.triggered.connect(self.screen_settings_requested.emit)
        setting_menu.addAction(screen_action)
        self.actions["setting.screen"] = screen_action
        
        sync_action = QAction(tr("action.sync_setting"), self)
        sync_action.triggered.connect(self.sync_settings_requested.emit)
        setting_menu.addAction(sync_action)
        self.actions["setting.sync"] = sync_action
        
        control_menu = self.addMenu(tr("menu.control"))
        self.menus["control"] = control_menu
        
        discover_action = QAction(tr("action.discover"), self)
        discover_action.triggered.connect(self.discover_controllers_requested.emit)
        control_menu.addAction(discover_action)
        self.actions["control.discover"] = discover_action
        
        dashboard_action = QAction(tr("action.dashboard"), self)
        dashboard_action.triggered.connect(self.dashboard_requested.emit)
        control_menu.addAction(dashboard_action)
        self.actions["control.dashboard"] = dashboard_action
        
        control_menu.addSeparator()
        
        time_power_action = QAction(tr("action.time_power"), self)
        time_power_action.triggered.connect(self.time_power_brightness_requested.emit)
        control_menu.addAction(time_power_action)
        self.actions["control.time_power"] = time_power_action
        
        network_config_action = QAction(tr("action.network_config"), self)
        network_config_action.triggered.connect(self.network_config_requested.emit)
        control_menu.addAction(network_config_action)
        self.actions["control.network"] = network_config_action
        
        diagnostics_action = QAction(tr("action.diagnostics"), self)
        diagnostics_action.triggered.connect(self.diagnostics_requested.emit)
        control_menu.addAction(diagnostics_action)
        self.actions["control.diagnostics"] = diagnostics_action
        
        control_menu.addSeparator()
        
        device_info_action = QAction(tr("action.device_info"), self)
        device_info_action.triggered.connect(self.device_info_requested.emit)
        control_menu.addAction(device_info_action)
        self.actions["control.device_info"] = device_info_action
        
        clear_action = QAction(tr("action.clear_program"), self)
        clear_action.triggered.connect(self.clear_program_requested.emit)
        control_menu.addAction(clear_action)
        self.actions["control.clear"] = clear_action
        
        send_action = QAction(tr("action.send"), self)
        send_action.triggered.connect(self.send_requested.emit)
        control_menu.addAction(send_action)
        self.actions["control.send"] = send_action
        
        control_menu.addSeparator()
        
        export_usb_action = QAction(tr("action.export_to_usb"), self)
        export_usb_action.triggered.connect(self.export_to_usb_requested.emit)
        control_menu.addAction(export_usb_action)
        self.actions["control.export_to_usb"] = export_usb_action
        
        control_menu.addSeparator()
        
        import_action = QAction(tr("action.import_controller"), self)
        import_action.triggered.connect(self.import_requested.emit)
        control_menu.addAction(import_action)
        self.actions["control.import"] = import_action
        
        export_action = QAction(tr("action.export"), self)
        export_action.triggered.connect(self.export_requested.emit)
        control_menu.addAction(export_action)
        self.actions["control.export"] = export_action
        
        control_menu.addSeparator()
        
        language_menu = self.addMenu(tr("menu.language"))
        self.menus["language"] = language_menu
        
        self.lang_actions = {}
        for label, code in [("English", "en"), ("italiano", "it"), ("polski", "pl")]:
            act = QAction(label, self)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, c=code: self.on_language_change(c))
            language_menu.addAction(act)
            self.lang_actions[code] = act
        self.set_language_checked("en")
        
        help_menu = self.addMenu(tr("menu.help"))
        self.menus["help"] = help_menu
        about_action = QAction(tr("action.about"), self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        self.actions["help.about"] = about_action
    
    def on_display_settings(self):
        try:
            from ui.screen_settings_dialog import ScreenSettingsDialog
            dlg = ScreenSettingsDialog(self)
            if dlg.exec():
                main_window = self.parent()
                if main_window and hasattr(main_window, 'program_manager'):
                    program = main_window.program_manager.current_program
                    if program:
                        rotate = int(dlg.rotate_combo.currentText() if dlg.rotate_combo.currentText().isdigit() else 0)
                        if "screen" not in program.properties:
                            program.properties["screen"] = {}
                        program.properties["screen"]["rotate"] = rotate
        except Exception as e:
            logger.error(f"Error in on_display_settings: {e}", exc_info=True)
    
    def set_language_checked(self, code: str):
        for c, act in self.lang_actions.items():
            act.setChecked(c == code)
    
    def refresh_texts(self):
        if "file" in self.menus:
            self.menus["file"].setTitle(tr("menu.file"))
        if "setting" in self.menus:
            self.menus["setting"].setTitle(tr("menu.setting"))
        if "control" in self.menus:
            self.menus["control"].setTitle(tr("menu.control"))
        if "language" in self.menus:
            self.menus["language"].setTitle(tr("menu.language"))
        if "help" in self.menus:
            self.menus["help"].setTitle(tr("menu.help"))
        a = self.actions
        if "file.new" in a: a["file.new"].setText(tr("action.new"))
        if "file.open" in a: a["file.open"].setText(tr("action.open"))
        if "file.save" in a: a["file.save"].setText(tr("action.save"))
        if "file.exit" in a: a["file.exit"].setText(tr("action.exit"))
        if "setting.screen" in a: a["setting.screen"].setText(tr("action.screen_setting"))
        if "setting.sync" in a: a["setting.sync"].setText(tr("action.sync_setting"))
        if "control.device_info" in a: a["control.device_info"].setText("📱 Controller Information")
        if "control.clear" in a: a["control.clear"].setText(tr("action.clear_program"))
        if "control.send" in a: a["control.send"].setText(tr("action.send"))
        if "control.export_to_usb" in a: a["control.export_to_usb"].setText(tr("action.export_to_usb"))
        if "help.about" in a: a["help.about"].setText(tr("action.about"))
    
    def set_actions_enabled_for_screen(self, has_screen: bool):
        if "file.save" in self.actions:
            self.actions["file.save"].setEnabled(has_screen)
        if "setting.screen" in self.actions:
            self.actions["setting.screen"].setEnabled(True)
        if "setting.sync" in self.actions:
            self.actions["setting.sync"].setEnabled(has_screen)
        for key in ["control.device_info", "control.clear", "control.send", "control.export_to_usb"]:
            if key in self.actions:
                self.actions[key].setEnabled(has_screen)
    
    def on_open(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("action.open_program"), "",
            tr("action.program_files")
        )
        if file_path:
            self.open_program_requested.emit(file_path)
    
    def on_save(self):
        self.save_program_requested.emit("")
    
    def on_exit(self):
        try:
            self.parent().close()
        except Exception:
            self.exit_requested.emit()
    
    def on_language_change(self, language: str):
        from config.settings import settings
        settings.set("language", language)
        set_language(language)
        self.set_language_checked(language)
        self.refresh_texts()
        self.language_changed.emit(language)
        logger.info(f"Language changed to: {language}")
    
    def on_about(self):
        from config.constants import APP_NAME, APP_VERSION
        QMessageBox.about(self, "About", f"{APP_NAME} v{APP_VERSION}\n\nLED Display Controller Program Manager")

