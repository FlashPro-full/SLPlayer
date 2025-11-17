"""
Menu bar component
"""
from PyQt5.QtWidgets import QMenuBar, QMessageBox, QAction, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from utils.logger import get_logger
from config.i18n import tr, set_language

logger = get_logger(__name__)


class MenuBar(QMenuBar):
    """Application menu bar"""
    
    new_program_requested = pyqtSignal()
    open_program_requested = pyqtSignal(str)
    save_program_requested = pyqtSignal(str)
    exit_requested = pyqtSignal()
    
    screen_settings_requested = pyqtSignal()
    sync_settings_requested = pyqtSignal()
    
    device_info_requested = pyqtSignal()
    clear_program_requested = pyqtSignal()
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    upload_requested = pyqtSignal()
    download_requested = pyqtSignal()
    
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
        """Initialize menu items per draft"""
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
        
        discover_action = QAction("🔍 Discover Controllers", self)
        discover_action.triggered.connect(self.discover_controllers_requested.emit)
        control_menu.addAction(discover_action)
        self.actions["control.discover"] = discover_action
        
        dashboard_action = QAction("📊 Dashboard", self)
        dashboard_action.triggered.connect(self.dashboard_requested.emit)
        control_menu.addAction(dashboard_action)
        self.actions["control.dashboard"] = dashboard_action
        
        control_menu.addSeparator()
        
        device_info_action = QAction("📱 Controller Information", self)
        device_info_action.triggered.connect(self.device_info_requested.emit)
        control_menu.addAction(device_info_action)
        self.actions["control.device_info"] = device_info_action
        
        clear_action = QAction(tr("action.clear_program"), self)
        clear_action.triggered.connect(self.clear_program_requested.emit)
        control_menu.addAction(clear_action)
        self.actions["control.clear"] = clear_action
        
        upload_action = QAction(tr("action.upload"), self)
        upload_action.triggered.connect(self.upload_requested.emit)
        control_menu.addAction(upload_action)
        self.actions["control.upload"] = upload_action
        
        download_action = QAction(tr("action.download"), self)
        download_action.triggered.connect(self.download_requested.emit)
        control_menu.addAction(download_action)
        self.actions["control.download"] = download_action
        
        language_menu = self.addMenu(tr("menu.language"))
        self.menus["language"] = language_menu
        
        self.lang_actions = {}
        for label, code in [("English", "en"), ("italiano", "it"), ("中文", "zh"), ("polski", "pl")]:
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
        except Exception:
            pass
    
    def set_language_checked(self, code: str):
        for c, act in self.lang_actions.items():
            act.setChecked(c == code)
    
    def refresh_texts(self):
        """Refresh menu and actions texts based on current language."""
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
        if "control.upload" in a: a["control.upload"].setText(tr("action.upload"))
        if "control.download" in a: a["control.download"].setText(tr("action.download"))
        if "help.about" in a: a["help.about"].setText(tr("action.about"))
    
    def set_actions_enabled_for_screen(self, has_screen: bool):
        """
        Enable/disable menu items depending on whether a controller screen/program exists.
        Requirement: disable all related items except Screen Setting before adding a screen.
        """
        if "file.save" in self.actions:
            self.actions["file.save"].setEnabled(has_screen)
        if "setting.screen" in self.actions:
            self.actions["setting.screen"].setEnabled(True)
        if "setting.sync" in self.actions:
            self.actions["setting.sync"].setEnabled(has_screen)
        for key in ["control.device_info", "control.clear", "control.upload", "control.download"]:
            if key in self.actions:
                self.actions[key].setEnabled(has_screen)
    
    def on_open(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Program", "",
            "Program Files (*.soo);;All Files (*)"
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

