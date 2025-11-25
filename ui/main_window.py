import sys
from datetime import datetime
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
from ui.properties_panel import PropertiesPanel

logger = get_logger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLPlayer")
        self.setGeometry(100, 100, 800, 600)
        
        self.program_manager = ProgramManager()
        self.screen_manager = ScreenManager()
        self.file_manager = FileManager(self.screen_manager)
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
        main_splitter = QSplitter(Qt.Vertical, self)
        
        top_splitter = QSplitter(Qt.Horizontal, self)
        self.screen_list_panel = ScreenListPanel(self)
        self.screen_list_panel.set_screen_manager(self.screen_manager)
        top_splitter.addWidget(self.screen_list_panel)
        
        self.content_widget = ContentWidget(self, self.screen_manager)
        top_splitter.addWidget(self.content_widget)
        
        top_splitter.setSizes([250, 750])
        top_splitter.setStretchFactor(0, 0)
        top_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(top_splitter)
        
        self.properties_panel = PropertiesPanel(self)
        self.content_widget.set_properties_panel(self.properties_panel)
        self.content_widget.set_screen_list_panel(self.screen_list_panel)
        self.properties_panel.set_program_manager(self.program_manager)
        self.properties_panel.set_screen_manager(self.screen_manager)
        main_splitter.addWidget(self.properties_panel)
        
        main_splitter.setSizes([600, 300])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        
        self.setCentralWidget(main_splitter)
        
    def _setup_chessboard_background(self):
        central_widget = ContentWidget(self)
        self.setCentralWidget(central_widget)

    def _setup_properties_panel(self):
        self.properties_panel = PropertiesPanel(self)
        self.addWidget(self.properties_panel)
    
    def _connect_signals(self):
        self.menu_bar.send_requested.connect(self.on_send_program)
        self.menu_bar.export_to_usb_requested.connect(self.on_export_to_usb)
        self.menu_bar.open_program_requested.connect(self._on_open_file_requested)
        self.menu_bar.new_program_requested.connect(self._on_new_program_from_menu)
        self.menu_bar.new_screen_requested.connect(self._on_new_screen_from_menu)
        self.menu_bar.screen_settings_requested.connect(self._on_screen_settings_requested)
        self.menu_bar.sync_settings_requested.connect(self._on_sync_settings_requested)
        self.control_toolbar.action_triggered.connect(self.on_toolbar_action)
        self.playback_toolbar.action_triggered.connect(self.on_playback_action)
        self.program_toolbar.new_program_requested.connect(self._on_new_program_from_toolbar)
        self.program_toolbar.new_screen_requested.connect(self._on_new_screen_from_toolbar)
        
        screen_config_manager = get_screen_config_manager()
        screen_config_manager.config_changed.connect(self._on_screen_config_changed)
        
        self.screen_list_panel.new_screen_requested.connect(self._on_new_screen_requested)
        self.screen_list_panel.screen_selected.connect(self._on_screen_selected)
        self.screen_list_panel.screen_deleted.connect(self._on_screen_deleted)
        self.screen_list_panel.screen_renamed.connect(self._on_screen_renamed)
        self.screen_list_panel.screen_insert_requested.connect(self._on_screen_insert)
        self.screen_list_panel.screen_close_requested.connect(self._on_screen_close)
        self.screen_list_panel.program_selected.connect(self._on_program_selected)
        self.screen_list_panel.content_selected.connect(self._on_content_selected)
        self.screen_list_panel.content_add_requested.connect(self._on_content_add_requested)
        self.screen_list_panel.delete_program_requested.connect(self._on_program_delete)
        self.screen_list_panel.delete_content_requested.connect(self._on_content_delete)
        self.screen_list_panel.program_copy_requested.connect(self._on_program_copy)
        self.screen_list_panel.content_copy_requested.connect(self._on_content_copy)
        self.content_types_toolbar.content_type_selected.connect(self._on_content_type_selected)
        self.menu_bar.save_program_requested.connect(self._on_save_requested)
    
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
            self.on_insert()
        elif action == "clear":
            self.on_clear()
    
    def on_insert(self):
        self.program_action_service.show_insert_instructions(self)
    
    def on_clear(self):
        result = self.program_action_service.clear_program(self)
        if result:
            current_program = self.program_manager.current_program
            if not current_program and self.screen_manager:
                if self.screen_manager.current_screen and self.screen_manager.current_screen.programs:
                    current_program = self.screen_manager.current_screen.programs[0]
            if current_program:
                self.properties_panel.set_program(current_program)
            if hasattr(self, 'content_widget'):
                self.content_widget.update()
            if hasattr(self, 'screen_list_panel'):
                self.screen_list_panel.refresh_screens(debounce=False)
    
    def on_playback_action(self, action: str):
        if not hasattr(self, 'content_widget'):
            return
        
        if action == "play":
            self.content_widget.set_playing(True)
        elif action == "pause":
            self.content_widget.set_playing(False)
        elif action == "stop":
            self.content_widget.set_playing(False)
            self.content_widget._cleanup_all_video_players()
            self.content_widget._photo_animations.clear()
            self.content_widget.update()
    
    def _on_screen_selected(self, screen_name: str):
        if not self.screen_manager:
                return
        screen = self.screen_manager.get_screen_by_name(screen_name)
        if screen:
            if hasattr(self, 'content_widget'):
                self.content_widget._cleanup_all_video_players()
            self.content_widget._photo_animations.clear()
            self.screen_manager.current_screen = screen
            from core.screen_config import set_screen_config, get_screen_config
            screen_config = get_screen_config()
            brand = screen_config.get("brand", "") if screen_config else ""
            model = screen_config.get("model", "") if screen_config else ""
            set_screen_config(
                brand,
                model,
                screen.width,
                screen.height,
                0,
                screen_name
            )
            self.properties_panel.set_screen(
                screen_name, 
                screen.programs, 
                self.program_manager, 
                self.screen_manager
            )
            if hasattr(self, 'content_widget'):
                self.content_widget.update()
    
    def _on_program_selected(self, program_id: str):
        if not self.screen_manager:
                return
        program = self.screen_manager.get_program_by_id(program_id)
        if program:
            for screen in self.screen_manager.screens:
                if program in screen.programs:
                    self.screen_manager.current_screen = screen
                    break
            self.properties_panel.set_program(program)
        if hasattr(self, 'content_widget'):
            self.content_widget.set_selected_element(None)
            self.content_widget.update()
    
    def _on_content_selected(self, program_id: str, element_id: str):
        if not self.screen_manager:
                return
        program = self.screen_manager.get_program_by_id(program_id)
        if program:
            element = next((e for e in program.elements if e.get("id") == element_id), None)
            if element:
                self.properties_panel.set_element(element, program)
                if hasattr(self, 'content_widget'):
                    self.content_widget.set_selected_element(element_id)
    
    def _on_program_delete(self, program_id: str):
        if not self.screen_manager:
                return
            
        program = self.screen_manager.get_program_by_id(program_id)
        if not program:
            return
            
        for screen in self.screen_manager.screens:
            if program in screen.programs:
                screen.remove_program(program)
                self.screen_manager._programs_by_id.pop(program_id, None)
                if hasattr(self, 'screen_list_panel'):
                    self.screen_list_panel.refresh_screens(debounce=False)
                if hasattr(self, 'content_widget'):
                    self.content_widget.update()
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.show_empty()
                break
            
    def _on_content_delete(self, program_id: str, element_id: str):
        if not self.screen_manager:
                return
            
        program = self.screen_manager.get_program_by_id(program_id)
        if not program:
            return
        
        element = next((e for e in program.elements if e.get("id") == element_id), None)
        if element:
            program.elements.remove(element)
            from datetime import datetime
            program.modified = datetime.now().isoformat()
            if hasattr(self, 'screen_list_panel'):
                self.screen_list_panel.refresh_screens(debounce=False)
            if hasattr(self, 'content_widget'):
                self.content_widget.update()
            self.properties_panel.show_empty()
    
    def _on_content_add_requested(self, program_id: str, content_type: str):
        if hasattr(self, 'content_widget'):
            self.content_widget.add_content(program_id, content_type)
    
    def _on_content_type_selected(self, content_type: str):
        if hasattr(self, 'content_widget'):
            self.content_widget.add_content_to_current_program(content_type)
    
    def _on_screen_insert(self, screen_name: str):
        self.program_action_service.show_insert_instructions(self)
    
    def _on_screen_close(self, screen_name: str):
        if not self.screen_manager:
                return
        screen = self.screen_manager.get_screen_by_name(screen_name)
        if screen:
            self.screen_manager.delete_screen(screen)
            if hasattr(self, 'screen_list_panel'):
                self.screen_list_panel.refresh_screens(debounce=False)
            if hasattr(self, 'content_widget'):
                self.content_widget.update()
    
    def _on_program_copy(self, program_id: str):
        if not self.screen_manager:
                return
        program = self.screen_manager.get_program_by_id(program_id)
        if program and hasattr(self, 'screen_list_panel'):
            import copy
            self.screen_list_panel._clipboard_data = program.to_dict()
            self.screen_list_panel._clipboard_type = "program"
    
    def _on_content_copy(self, program_id: str, element_id: str):
        if not self.screen_manager:
            return
        program = self.screen_manager.get_program_by_id(program_id)
        if program and hasattr(self, 'screen_list_panel'):
            element = next((e for e in program.elements if e.get("id") == element_id), None)
            if element:
                import copy
                self.screen_list_panel._clipboard_data = copy.deepcopy(element)
                self.screen_list_panel._clipboard_type = "content"
                self.screen_list_panel._clipboard_program_id = program_id
    
    def _load_autosaved_files(self):
        if not self.file_manager or not self.screen_manager:
            return
        
        autosaved_screens = self.file_manager.load_autosaved_screens()
        for screen in autosaved_screens:
            if screen.id not in self.screen_manager._screens_by_id:
                self.screen_manager.screens.append(screen)
                self.screen_manager._screens_by_name[screen.name] = screen
                self.screen_manager._screens_by_id[screen.id] = screen
                
                for program in screen.programs:
                    self.screen_manager._programs_by_id[program.id] = program
        
        if autosaved_screens and hasattr(self, 'screen_list_panel'):
            self.screen_list_panel.refresh_screens(debounce=False)
        elif not autosaved_screens:
            if not self.screen_manager.screens:
                self.open_screen_settings_on_startup()
    
    def _on_open_file_requested(self, file_path: str):
        if not file_path:
            return
        
        result = self.load_soo_file(file_path, clear_existing=False)
        if result:
            if hasattr(self, 'content_widget'):
                self.content_widget.update()
            if self.screen_manager and self.screen_manager.current_screen:
                if self.screen_manager.current_screen.programs:
                    current_program = self.screen_manager.current_screen.programs[0]
                    self.properties_panel.set_program(current_program)
                else:
                    self.properties_panel.set_screen(
                        self.screen_manager.current_screen.name,
                        self.screen_manager.current_screen.programs,
                        self.program_manager,
                        self.screen_manager
                    )
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to load file: {file_path}"
            )
    
    def load_soo_file(self, file_path: str, clear_existing: bool = False):
        result = self.file_manager.load_soo_file(file_path, clear_existing)
        if result and hasattr(self, 'screen_list_panel'):
            self.screen_list_panel.refresh_screens(debounce=False)
        return result
    
    def _on_save_requested(self, file_path: str = ""):
        from PyQt5.QtWidgets import QFileDialog
        from pathlib import Path
        
        if not self.screen_manager or not self.screen_manager.screens:
                return
            
        if not file_path:
            default_path = ""
            if self.screen_manager.current_screen and self.screen_manager.current_screen.file_path:
                default_path = self.screen_manager.current_screen.file_path
            else:
                from utils.app_data import get_app_data_dir
                work_dir = get_app_data_dir() / "work"
                work_dir.mkdir(parents=True, exist_ok=True)
                if self.screen_manager.current_screen:
                    safe_name = ScreenManager.sanitize_screen_name(self.screen_manager.current_screen.name)
                    default_path = str(work_dir / f"{safe_name}.soo")
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Screen",
                default_path,
                "SOO Files (*.soo);;All Files (*)"
            )
        
        if file_path:
            self._save_screen_to_file(file_path)
    
    def _save_screen_to_file(self, file_path: str):
        if not self.screen_manager or not self.screen_manager.current_screen:
            return
        
        screen = self.screen_manager.current_screen
        properties_panel = self.properties_panel if hasattr(self, 'properties_panel') else None
        self.file_manager.save_screen_to_file(screen, file_path, properties_panel)
    
    def _on_screen_config_changed(self, config: dict):
        if hasattr(self, 'content_widget'):
            self.content_widget.update()
        
        if self._pending_new_screen:
            self._pending_new_screen = False
            if hasattr(self, 'screen_list_panel'):
                screen_name = self.screen_list_panel.add_new_screen()
                if screen_name:
                    self.screen_list_panel.add_program_to_screen(screen_name)
    
    def _on_new_screen_requested(self):
        self._pending_new_screen = True
        self.open_screen_settings_dialog()
    
    def _on_screen_deleted(self, screen_name: str):
        screen = self.screen_manager.get_screen_by_name(screen_name)
        if not screen:
            return
        
        deleted_file_path = screen.file_path
        is_autosaved = False
        
        if deleted_file_path:
            from pathlib import Path
            from utils.app_data import get_app_data_dir
            
            file_path_obj = Path(deleted_file_path)
            work_dir = get_app_data_dir() / "work"
            
            try:
                resolved_path = file_path_obj.resolve()
                resolved_work_dir = work_dir.resolve()
                is_autosaved = resolved_path.parent == resolved_work_dir
                
                if is_autosaved:
                    if file_path_obj.exists():
                        file_path_obj.unlink()
                        logger.info(f"Deleted autosaved file: {deleted_file_path}")
            except Exception as e:
                logger.error(f"Error checking file path '{deleted_file_path}': {e}")
        
        self.screen_manager.delete_screen(screen)
        
        if deleted_file_path and not is_autosaved:
            remaining_screens_from_file = [
                s for s in self.screen_manager.screens 
                if s.file_path == deleted_file_path
            ]
            
            if not remaining_screens_from_file:
                work_dir = get_app_data_dir() / "work"
                real_saved_screens = [
                    s for s in self.screen_manager.screens 
                    if s.file_path and Path(s.file_path).parent.resolve() != work_dir.resolve()
                ]
                
                if not real_saved_screens:
                    logger.info(f"Closed/unloaded file: {deleted_file_path} (no remaining screens from real saved files)")
        
        if hasattr(self, 'screen_list_panel'):
            if self.screen_list_panel._last_selected_screen == screen_name:
                self.screen_list_panel._last_selected_screen = None
            if not self.screen_manager.screens:
                self.screen_list_panel._last_selected_program = None
                self.screen_list_panel._last_selected_content = None
                from core.screen_config import set_screen_name
                set_screen_name("")
            self.screen_list_panel.refresh_screens(debounce=False)
        if hasattr(self, 'content_widget'):
            self.content_widget.update()
        if hasattr(self, 'properties_panel'):
            if not self.screen_manager.screens:
                self.properties_panel.show_empty()
            elif self.screen_manager.current_screen:
                if self.screen_manager.current_screen.programs:
                    self.properties_panel.set_program(self.screen_manager.current_screen.programs[0])
                else:
                    self.properties_panel.set_screen(
                        self.screen_manager.current_screen.name,
                        self.screen_manager.current_screen.programs,
                        self.program_manager,
                        self.screen_manager
                    )
    
    def _on_screen_renamed(self, old_name: str, new_name: str):
        screen = self.screen_manager.get_screen_by_name(old_name)
        if screen:
            screen.name = new_name
            self.screen_manager._screens_by_name.pop(old_name, None)
            self.screen_manager._screens_by_name[new_name] = screen
            from core.screen_config import set_screen_name
            set_screen_name(new_name)
            if hasattr(self, 'screen_list_panel'):
                self.screen_list_panel.refresh_screens(debounce=False)
    
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
    
    def _on_screen_settings_requested(self):
        if not self.screen_manager or not self.screen_manager.current_screen:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Screen Selected", "Please select a screen first.")
            return
        
        self.open_screen_settings_dialog(load_current_screen=True)
    
    def _on_sync_settings_requested(self):
        from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox
        from core.sync_manager import SyncManager
        
        if not self.controller_service:
            QMessageBox.warning(self, "Error", "Controller service is not available.")
            return
        
        controller = self.controller_service.current_controller
        if not controller or not self.controller_service.is_connected():
            reply = QMessageBox.question(
                self,
                "No Controller Connected",
                "No controller is currently connected. Do you want to connect to a controller first?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                return
            else:
                QMessageBox.information(self, "Information", "Please connect to a controller to use sync settings.")
                return
        
        sync_manager = SyncManager()
        
        reply = QMessageBox.question(
            self,
            "Sync Settings",
            "Choose sync direction:\n\nYes: Import from controller to local\nNo: Export from local to controller\nCancel: Compare and show differences",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        
        try:
            if reply == QMessageBox.Yes:
                imported_data = sync_manager.import_from_controller(
                    controller,
                    self.screen_manager,
                    self.program_manager
                )
                program_count = len(imported_data.get('programs', {}))
                media_count = len(imported_data.get('media', {}))
                msg = f"Successfully imported data from controller.\n\nPrograms: {program_count}\nMedia files: {media_count}"
                if imported_data.get('brightness'):
                    msg += f"\nBrightness: {imported_data['brightness']}"
                if imported_data.get('screen_resolution'):
                    res = imported_data['screen_resolution']
                    msg += f"\nResolution: {res.get('width')}x{res.get('height')}"
                QMessageBox.information(self, "Import Complete", msg)
                if hasattr(self, 'screen_list_panel'):
                    self.screen_list_panel.refresh_screens(debounce=False)
                if hasattr(self, 'content_widget'):
                    self.content_widget.update()
            elif reply == QMessageBox.No:
                success = sync_manager.export_to_controller(
                    controller,
                    self.program_manager,
                    self.screen_manager
                )
                if success:
                    QMessageBox.information(self, "Export Complete", "Successfully exported data to controller.")
                else:
                    QMessageBox.warning(self, "Export Failed", "Failed to export some data to controller.")
            else:
                changes = sync_manager.compare_and_sync(
                    controller,
                    self.program_manager,
                    self.screen_manager
                )
                programs_to_upload = len(changes.get('programs_to_upload', []))
                programs_to_delete = len(changes.get('programs_to_delete', []))
                params_to_update = len(changes.get('parameters_to_update', {}))
                msg = f"Sync Comparison:\n\nPrograms to upload: {programs_to_upload}\nPrograms to delete: {programs_to_delete}\nParameters to update: {params_to_update}"
                if programs_to_upload == 0 and programs_to_delete == 0 and params_to_update == 0:
                    msg += "\n\nNo differences found."
                QMessageBox.information(self, "Sync Comparison", msg)
        except Exception as e:
            logger.exception(f"Error during sync: {e}")
            QMessageBox.critical(self, "Sync Error", f"An error occurred during sync:\n{str(e)}")
    
    def open_screen_settings_dialog(self, load_current_screen: bool = False):
        try:
            from ui.screen_settings_dialog import ScreenSettingsDialog
            from PyQt5.QtWidgets import QDialog
            from core.screen_config import get_screen_config
            
            dialog = ScreenSettingsDialog(self)
            
            if load_current_screen and self.screen_manager and self.screen_manager.current_screen:
                screen = self.screen_manager.current_screen
                screen_config = get_screen_config()
                
                brand = screen_config.get("brand", "") if screen_config else ""
                model = screen_config.get("model", "") if screen_config else ""
                rotate = screen_config.get("rotate", 0) if screen_config else 0
                
                dialog.load_screen_parameters(
                    brand=brand,
                    model=model,
                    width=screen.width,
                    height=screen.height,
                    rotate=rotate
                )
            
            result = dialog.exec()
            if result == QDialog.Accepted:
                if load_current_screen and self.screen_manager and self.screen_manager.current_screen:
                    screen = self.screen_manager.current_screen
                    brand = dialog.selected_series()
                    model = dialog.selected_model()
                    width, height = dialog.selected_size()
                    rotate = dialog.selected_rotate()
                    
                    screen.width = width
                    screen.height = height
                    screen.modified = datetime.now().isoformat()
                    
                    from core.screen_config import set_screen_config
                    set_screen_config(brand, model, width, height, rotate, screen.name)
                    
                    if screen.file_path:
                        self.file_manager.save_screen_to_file(screen, screen.file_path, self.properties_panel)
                    
                    if hasattr(self, 'screen_list_panel'):
                        self.screen_list_panel.refresh_screens(debounce=False)
                    if hasattr(self, 'content_widget'):
                        self.content_widget.update()
                    if hasattr(self, 'properties_panel'):
                        self.properties_panel.set_screen(
                            screen.name,
                            screen.programs,
                            self.program_manager,
                            self.screen_manager
                        )
            else:
                if self._pending_new_screen:
                    self._pending_new_screen = False
        except Exception as e:
            logger.error(f"Error opening screen settings dialog: {e}", exc_info=True)
            if self._pending_new_screen:
                self._pending_new_screen = False       

    def closeEvent(self, event: QtGui.QCloseEvent):
        try:
            if self.screen_manager and self.screen_manager.screens:
                saved_count = self.file_manager.save_all_screens()
                logger.info(f"Auto-saved {saved_count} screen(s) to work directory on close")
        except Exception as e:
            logger.error(f"Error auto-saving on close: {e}", exc_info=True)
        
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())