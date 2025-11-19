import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QSplitter, QProgressDialog, QMessageBox
from PyQt5.QtGui import QCloseEvent

from core.program_manager import ProgramManager
from core.screen_manager import ScreenManager
from core.file_manager import FileManager
from core.file_io_thread import FileLoadThread, BatchFileLoadThread
from core.screen_config import get_screen_config_manager
from services.controller_service import ControllerService
from services.program_action_service import ProgramActionService
from utils.logger import get_logger
from ui.menu_bar import MenuBar
from ui.toolbar import ProgramToolbar, ContentTypesToolbar, ControlToolbar, PlaybackToolbar
from ui.screen_list_panel import ScreenListPanel
from ui.content_widget import ContentWidget

logger = get_logger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLPlayer")
        self.setGeometry(100, 100, 800, 600)
        
        self.program_manager = ProgramManager()
        self.screen_manager = ScreenManager()
        self.file_manager = FileManager(self.program_manager, self.screen_manager)
        self.controller_service = ControllerService()
        self.program_action_service = ProgramActionService(self.program_manager, self.controller_service, self.screen_manager)
        self._latest_file_loaded = False
        self._file_load_thread = None
        self._batch_load_thread = None
        self._pending_new_screen = False
        
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_main_content()
        self._connect_signals()
    
    def _setup_menu_bar(self):
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
    
    def _setup_toolbar(self):
        self.program_toolbar = ProgramToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.program_toolbar)
        self.content_types_toolbar = ContentTypesToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.content_types_toolbar)
        self.control_toolbar = ControlToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.control_toolbar)
        self.playback_toolbar = PlaybackToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.playback_toolbar)
    
    def _setup_main_content(self):
        splitter = QSplitter(Qt.Horizontal, self)
        self.screen_list_panel = ScreenListPanel(self)
        self.screen_list_panel.set_screen_manager(self.screen_manager)
        splitter.addWidget(self.screen_list_panel)
        
        self.content_widget = ContentWidget(self)
        splitter.addWidget(self.content_widget)
        
        splitter.setSizes([250, 750])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        self.setCentralWidget(splitter)
        
    def _setup_chessboard_background(self):
        central_widget = ContentWidget(self)
        self.setCentralWidget(central_widget)
    
    def _connect_signals(self):
        self.menu_bar.send_requested.connect(self.on_send_program)
        self.menu_bar.export_to_usb_requested.connect(self.on_export_to_usb)
        self.menu_bar.new_program_requested.connect(self._on_new_program_from_menu)
        self.menu_bar.new_screen_requested.connect(self._on_new_screen_from_menu)
        self.control_toolbar.action_triggered.connect(self.on_toolbar_action)
        self.program_toolbar.new_program_requested.connect(self._on_new_program_from_toolbar)
        self.program_toolbar.new_screen_requested.connect(self._on_new_screen_from_toolbar)
        
        screen_config_manager = get_screen_config_manager()
        screen_config_manager.config_changed.connect(self._on_screen_config_changed)
        
        self.screen_list_panel.new_screen_requested.connect(self._on_new_screen_requested)
        self.screen_list_panel.screen_selected.connect(self._on_screen_selected)
        self.screen_list_panel.screen_deleted.connect(self._on_screen_deleted)
        self.screen_list_panel.screen_renamed.connect(self._on_screen_renamed)
    
    def on_send_program(self):
        self.program_action_service.send_program(self)
    
    def on_export_to_usb(self):
        self.program_action_service.export_to_usb(self)
    
    def on_toolbar_action(self, action: str):
        if action == "send":
            self.on_send_program()
        elif action == "export_to_usb":
            self.on_export_to_usb()
        elif action == "insert":
            self.program_action_service.show_insert_instructions(self)
        elif action == "clear":
            self.program_action_service.clear_program(self)
    
    def load_soo_file(self, file_path: str, clear_existing: bool = False, async_load: bool = True) -> bool:
        if not async_load:
            try:
                result = self.file_manager.load_soo_file(file_path, clear_existing)
                self._latest_file_loaded = result
                return result
            except Exception as e:
                logger.error(f"Error loading .soo file: {e}", exc_info=True)
                self._latest_file_loaded = False
                return False
        
        if self._file_load_thread and self._file_load_thread.isRunning():
            logger.warning("File load already in progress")
            return False
        
        progress = QProgressDialog("Loading file...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        
        self._file_load_thread = FileLoadThread(file_path, self.file_manager, clear_existing)
        self._file_load_thread.progress.connect(progress.setLabelText)
        self._file_load_thread.finished.connect(
            lambda success, path, error: self._on_file_loaded(success, path, error, progress)
        )
        self._file_load_thread.start()
        
        return True
    
    def _on_file_loaded(self, success: bool, file_path: str, error: Exception, progress: QProgressDialog):
        """Handle file load completion"""
        progress.close()
        self._latest_file_loaded = success
        
        if error:
            QMessageBox.critical(
                self,
                "File Load Error",
                f"Error loading file:\n{str(error)}"
            )
        elif success:
            logger.info(f"File loaded successfully: {file_path}")
        else:
            QMessageBox.warning(
                self,
                "File Load Failed",
                f"Failed to load file: {file_path}"
            )

            if not self._latest_file_loaded:
                self.open_screen_settings_on_startup()
    
    def load_latest_soo_files_async(self):
        """Load all .soo files in background thread"""
        if self._batch_load_thread and self._batch_load_thread.isRunning():
            logger.warning("Batch file load already in progress")
            return False
        
        progress = QProgressDialog("Loading files...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        
        self._batch_load_thread = BatchFileLoadThread(self.file_manager)
        self._batch_load_thread.progress.connect(
            lambda msg, current, total: progress.setLabelText(f"{msg} ({current}/{total})")
        )
        self._batch_load_thread.finished.connect(
            lambda success, loaded, total: self._on_batch_files_loaded(success, loaded, total, progress)
        )
        self._batch_load_thread.start()
        
        return True
    
    def _on_batch_files_loaded(self, success: bool, files_loaded: int, files_total: int, progress: QProgressDialog):

        progress.close()
        self._latest_file_loaded = success
        
        if success:
            logger.info(f"Loaded {files_loaded}/{files_total} files successfully")
        else:
            logger.warning("No files were loaded")
            # Open screen settings dialog if no files were loaded
            if files_loaded == 0:
                self.open_screen_settings_on_startup()

    def _on_screen_config_changed(self, config: dict):
        if hasattr(self, 'content_widget'):
            self.content_widget.update()
        
        if self._pending_new_screen:
            self._pending_new_screen = False
            if hasattr(self, 'screen_list_panel'):
                self.screen_list_panel.add_new_screen()
                from core.screen_config import get_screen_name
                screen_name = get_screen_name()
                if screen_name:
                    self.screen_list_panel.add_program_to_screen(screen_name)
    
    def _on_new_screen_requested(self):
        from core.screen_config import get_screen_config
        config = get_screen_config()
        width = config.get("width", 640) if config else 640
        height = config.get("height", 480) if config else 480
        
        screen = self.screen_manager.create_screen("New Screen", width, height)
        from core.screen_config import set_screen_name
        set_screen_name(screen.name)
    
    def _on_screen_selected(self, screen_name: str):
        screen = self.screen_manager.get_screen_by_name(screen_name)
        if screen:
            self.screen_manager.current_screen = screen
    
    def _on_screen_deleted(self, screen_name: str):
        screen = self.screen_manager.get_screen_by_name(screen_name)
        if screen:
            self.screen_manager.delete_screen(screen)
    
    def _on_screen_renamed(self, old_name: str, new_name: str):
        screen = self.screen_manager.get_screen_by_name(old_name)
        if screen:
            screen.name = new_name
            self.screen_manager._screens_by_name.pop(old_name, None)
            self.screen_manager._screens_by_name[new_name] = screen
            from core.screen_config import set_screen_name
            set_screen_name(new_name)
    
    def _on_new_program_from_menu(self):
        if hasattr(self, 'screen_list_panel'):
            from core.screen_config import get_screen_name
            screen_name = get_screen_name()
            self.screen_list_panel.add_program_to_screen(screen_name)
    
    def _on_new_screen_from_menu(self):
        self._pending_new_screen = True
        self.open_screen_settings_dialog()
    
    def _on_new_program_from_toolbar(self):
        if hasattr(self, 'screen_list_panel'):
            from core.screen_config import get_screen_name
            screen_name = get_screen_name()
            self.screen_list_panel.add_program_to_screen(screen_name)
    
    def _on_new_screen_from_toolbar(self):
        self._pending_new_screen = True
        self.open_screen_settings_dialog()

    def open_screen_settings_on_startup(self):
        self._pending_new_screen = True
        self.open_screen_settings_dialog()
    
    def open_screen_settings_dialog(self):
        try:
            from ui.screen_settings_dialog import ScreenSettingsDialog
            dialog = ScreenSettingsDialog(self)
            result = dialog.exec()
        except Exception as e:
            logger.error(f"Error opening screen settings dialog: {e}", exc_info=True)

    def closeEvent(self, event: QtGui.QCloseEvent):
        try:
            if self.screen_manager and self.screen_manager.screens:
                saved_count = 0
                for screen in self.screen_manager.screens:
                    if screen.programs:
                        program = screen.programs[0]
                        if self.file_manager.save_soo_file_for_screen(program):
                            saved_count += 1
                logger.info(f"Auto-saved {saved_count} screen(s) to work directory on close")
        except Exception as e:
            logger.error(f"Error auto-saving on close: {e}", exc_info=True)

        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())