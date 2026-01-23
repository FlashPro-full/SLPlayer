import sys
import asyncio
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QSplitter, QMessageBox, QFileDialog

from core.program_manager import ProgramManager
from core.screen_manager import ScreenManager
from core.file_manager import FileManager
from core.screen_config import get_screen_config_manager
from services.controller_service import get_controller_service
from utils.logger import get_logger
from ui.toolbar import ProgramToolbar, ContentTypesToolbar, ControlToolbar, DeviceToolbar
from ui.screen_list_panel import ScreenListPanel
from ui.content_widget import ContentWidget
from ui.properties_panel import PropertiesPanel

logger = get_logger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLPlayer")
        self.setGeometry(100, 100, 800, 600)
        
        # Set dark grey background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
            }
            QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
        """)
        
        self.program_manager = ProgramManager()
        self.screen_manager = ScreenManager()
        self.file_manager = FileManager(self.screen_manager)
        self.controller_service = get_controller_service()
        self.current_controller = self.controller_service.get_current_controller()
        self._latest_file_loaded = False
        self._pending_new_screen = False
        self._setup_toolbar()
        self._setup_main_content()
        self._connect_signals()
        self._load_autosaved_files()
    
    def _setup_toolbar(self):
        self.program_toolbar = ProgramToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.program_toolbar)
        self.program_toolbar.setOrientation(Qt.Horizontal)
        self.content_types_toolbar = ContentTypesToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.content_types_toolbar)
        self.content_types_toolbar.setOrientation(Qt.Horizontal)
        self.control_toolbar = ControlToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.control_toolbar)
        self.control_toolbar.setOrientation(Qt.Horizontal)
        self.device_toolbar = DeviceToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.device_toolbar)
        self.device_toolbar.setOrientation(Qt.Horizontal)
    
    def _setup_main_content(self):
        main_splitter = QSplitter(Qt.Horizontal, self)
        
        left_splitter = QSplitter(Qt.Horizontal, self)
        self.screen_list_panel = ScreenListPanel(self)
        self.screen_list_panel.set_screen_manager(self.screen_manager)
        left_splitter.addWidget(self.screen_list_panel)
        
        self.content_widget = ContentWidget(self, self.screen_manager)
        self.content_widget.set_playing(True)
        left_splitter.addWidget(self.content_widget)
        
        left_splitter.setSizes([250, 750])
        left_splitter.setStretchFactor(0, 0)
        left_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(left_splitter)
        
        # Right side: properties panel
        self.properties_panel = PropertiesPanel(self)
        self.content_widget.set_properties_panel(self.properties_panel)
        self.content_widget.set_screen_list_panel(self.screen_list_panel)
        self.properties_panel.set_program_manager(self.program_manager)
        self.properties_panel.set_screen_manager(self.screen_manager)
        main_splitter.addWidget(self.properties_panel)
        
        main_splitter.setSizes([1000, 370])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        
        self.setCentralWidget(main_splitter)
        
        # Setup status bar
        from ui.status_bar import StatusBarWidget
        self.status_bar = StatusBarWidget(self)
        self.setStatusBar(self.status_bar)
        
    def _setup_chessboard_background(self):
        central_widget = ContentWidget(self)
        self.setCentralWidget(central_widget)

    def _setup_properties_panel(self):
        self.properties_panel = PropertiesPanel(self)
        self.addWidget(self.properties_panel)
    
    def _connect_signals(self):
        self.control_toolbar.action_triggered.connect(self.on_toolbar_action)
        self.program_toolbar.new_program_requested.connect(self._on_new_program)
        self.program_toolbar.export_requested.connect(self._on_save_requested)
        self.device_toolbar.time_requested.connect(self._on_time_requested)
        self.device_toolbar.brightness_requested.connect(self._on_brightness_requested)
        self.device_toolbar.power_requested.connect(self._on_power_requested)
        self.device_toolbar.schedule_requested.connect(self._on_schedule_requested)
        self.device_toolbar.network_requested.connect(self._on_network_config_requested)
        
        screen_config_manager = get_screen_config_manager()
        screen_config_manager.config_changed.connect(self._on_screen_config_changed)
        
        self.screen_list_panel.new_screen_requested.connect(self._on_new_screen_requested)
        self.screen_list_panel.screen_selected.connect(self._on_screen_selected)
        self.screen_list_panel.screen_deleted.connect(self._on_screen_deleted)
        self.screen_list_panel.screen_renamed.connect(self._on_screen_renamed)
        self.screen_list_panel.screen_insert_requested.connect(self._on_screen_insert)
        self.screen_list_panel.screen_close_requested.connect(self._on_screen_close)
        self.screen_list_panel.program_selected.connect(self._on_program_selected)
        self.screen_list_panel.program_renamed.connect(self._on_program_renamed)
        self.screen_list_panel.content_selected.connect(self._on_content_selected)
        self.screen_list_panel.content_renamed.connect(self._on_content_renamed)
        self.screen_list_panel.content_add_requested.connect(self._on_content_add_requested)
        self.screen_list_panel.delete_program_requested.connect(self._on_program_delete)
        self.screen_list_panel.delete_content_requested.connect(self._on_content_delete)
        self.screen_list_panel.program_copy_requested.connect(self._on_program_copy)
        self.screen_list_panel.content_copy_requested.connect(self._on_content_copy)
        self.content_types_toolbar.content_type_selected.connect(self._on_content_type_selected)
    
    def on_send_program(self):
        controller_dict = self.current_controller
        controller_type = controller_dict.get("controller_type", "").lower() if isinstance(controller_dict, dict) else ""
        
        if controller_type != "huidu":
            QMessageBox.warning(self, "Unsupported Controller", "This operation is only supported for Huidu controllers.")
            return
        
        try:
            from controllers.huidu import HuiduController
            from core.program_converter import ProgramConverter
            
            controller_id = controller_dict.get("controller_id")

            huidu_controller = HuiduController()
            
            current_program = self.screen_manager.current_screen.programs[0]
            program_dict = current_program.to_dict()
            
            # Check if content upload is disabled for this program
            properties = program_dict.get("properties", {})
            content_upload_enabled = properties.get("content_upload_enabled", True)
            
            # If content upload is disabled, skip sending this program entirely
            if not content_upload_enabled:
                logger.info(f"Content upload disabled for program '{program_dict.get('name')}' - skipping send")
                QMessageBox.information(self, "Info", f"Program '{program_dict.get('name')}' upload is disabled. Skipping send.")
                return
            
            sdk_program = ProgramConverter.soo_to_sdk(program_dict, "huidu")
            sdk_program_list = [sdk_program]
            
            # Run async update_program
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(huidu_controller.update_program(sdk_program_list, [controller_id]))
            
            if response.get("message") == "ok":
                QMessageBox.information(self, "Success", f"Program sent successfully.")
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Error", f"Failed to send program: {error_msg}")
        except Exception as e:
            logger.error(f"Error sending program: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while sending program:\n{str(e)}")
    
    def on_toolbar_action(self, action: str):
        if action == "send":
            self.on_send_program()
        elif action == "insert":
            self.on_insert_program()
        elif action == "clear":
            self.on_clear_program()
    
    def on_insert_program(self):
        controller_dict = self.current_controller
        controller_type = controller_dict.get("controller_type", "").lower() if isinstance(controller_dict, dict) else ""
        
        if controller_type != "huidu":
            QMessageBox.warning(self, "Unsupported Controller", "This operation is only supported for Huidu controllers.")
            return
        
        try:
            from controllers.huidu import HuiduController
            from core.program_converter import ProgramConverter
            
            controller_id = controller_dict.get("controller_id")

            huidu_controller = HuiduController()
            
            current_program = self.screen_manager.current_screen.programs[0]
            program_dict = current_program.to_dict()
            
            # Check if content upload is disabled for this program
            properties = program_dict.get("properties", {})
            content_upload_enabled = properties.get("content_upload_enabled", True)
            
            # If content upload is disabled, skip inserting this program entirely
            if not content_upload_enabled:
                logger.info(f"Content upload disabled for program '{program_dict.get('name')}' - skipping insert")
                QMessageBox.information(self, "Info", f"Program '{program_dict.get('name')}' upload is disabled. Skipping insert.")
                return
            
            sdk_program = ProgramConverter.soo_to_sdk(program_dict, "huidu")
            sdk_program_list = [sdk_program]
            
            # Run async add_program
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(huidu_controller.add_program(sdk_program_list, [controller_id]))
            
            if response.get("message") == "ok":
                QMessageBox.information(self, "Success", f"Program added successfully.")
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Error", f"Failed to send program: {error_msg}")
        except Exception as e:
            logger.error(f"Error sending program: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while sending program:\n{str(e)}")
    
    def on_clear_program(self):
        controller_dict = self.current_controller
        controller_type = controller_dict.get("controller_type", "").lower() if isinstance(controller_dict, dict) else ""
        
        if controller_type != "huidu":
            QMessageBox.warning(self, "Unsupported Controller", "This operation is only supported for Huidu controllers.")
            return
        
        try:
            from controllers.huidu import HuiduController
            from core.program_converter import ProgramConverter
            
            controller_id = controller_dict.get("controller_id")

            huidu_controller = HuiduController()
            
            current_program = self.screen_manager.current_screen.programs[0]
            program_dict = current_program.to_dict()
            
            # Check if content upload is disabled for this program
            properties = program_dict.get("properties", {})
            content_upload_enabled = properties.get("content_upload_enabled", True)
            
            # If content upload is disabled, remove all elements (content) from the program
            if not content_upload_enabled:
                program_dict = program_dict.copy()
                program_dict["elements"] = []
                logger.info(f"Content upload disabled for program '{program_dict.get('name')}' - inserting without elements")
            
            sdk_program = ProgramConverter.soo_to_sdk(program_dict, "huidu")
            sdk_program_list = [sdk_program]
            
            response = huidu_controller.remove_program(sdk_program_list, [controller_id])
            
            if response.get("message") == "ok":
                QMessageBox.information(self, "Success", f"Program added successfully.")
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Error", f"Failed to send program: {error_msg}")
        except Exception as e:
            logger.error(f"Error sending program: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while sending program:\n{str(e)}")
    
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
            controller_type = screen_config.get("controller_type", "") if screen_config else ""
            if screen and hasattr(screen, 'properties') and screen.properties:
                controller_type = screen.properties.get("controller_type", controller_type)
            set_screen_config(
                controller_type,
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
                if hasattr(self.content_widget, '_initialize_videos_for_program'):
                    self.content_widget._initialize_videos_for_program()
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
            if hasattr(self.content_widget, '_initialize_videos_for_program'):
                self.content_widget._initialize_videos_for_program()
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

    def _on_program_renamed(self, program_id: str, new_name: str):
        if not self.screen_manager:
            return
        
        program = self.screen_manager.get_program_by_id(program_id)
        if program:
            program.name = new_name
            program.modified = datetime.now().isoformat()
            if hasattr(self, 'screen_list_panel'):
                self.screen_list_panel.refresh_screens(debounce=False)
            if hasattr(self, 'properties_panel'):
                self.properties_panel.set_program(program)
    
    def _on_content_renamed(self, program_id: str, element_id: str, new_name: str):
        if not self.screen_manager:
            return
        
        program = self.screen_manager.get_program_by_id(program_id)
        if program:
            element = next((e for e in program.elements if e.get("id") == element_id), None)
            if element:
                element["name"] = new_name
                program.modified = datetime.now().isoformat()
                if hasattr(self, 'screen_list_panel'):
                    self.screen_list_panel.refresh_screens(debounce=False)
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.set_element(element, program)

    def _on_content_add_requested(self, program_id: str, content_type: str):
        if hasattr(self, 'content_widget'):
            self.content_widget.add_content(program_id, content_type)
    
    def _on_content_type_selected(self, content_type: str):
        if hasattr(self, 'screen_list_panel') and hasattr(self, 'content_widget'):
            program_id = self.screen_list_panel.get_selected_program_id()
            if program_id:
                self.content_widget.add_content(program_id, content_type)
            else:
                self.content_widget.add_content_to_current_program(content_type)
    
    def _on_screen_insert(self, screen_name: str):
        pass
    
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

        controller_name = None
        if self.controller_service and self.current_controller:
            controller_name = self.current_controller.get("name")
        if controller_name:
            from utils.app_data import get_app_data_dir
            from core.screen_manager import ScreenManager
            work_dir = get_app_data_dir() / "work"
            work_dir.mkdir(parents=True, exist_ok=True)
            safe_name = ScreenManager.sanitize_screen_name(controller_name)
            file_path = str(work_dir / f"{safe_name}.soo")
            
            existing_screen = self.file_manager.load_screen_from_file(file_path)
            if existing_screen:
                if existing_screen.id not in self.screen_manager._screens_by_id:
                    self.screen_manager.screens.append(existing_screen)
                    self.screen_manager._screens_by_name[existing_screen.name] = existing_screen
                    self.screen_manager._screens_by_id[existing_screen.id] = existing_screen
                    for program in existing_screen.programs:
                        self.screen_manager._programs_by_id[program.id] = program
                self.screen_manager.current_screen = existing_screen
                if hasattr(self, 'screen_list_panel'):
                    self.screen_list_panel.refresh_screens(debounce=False)
            else:
                from core.screen_config import get_screen_config
                config = get_screen_config()
                width = config.get("width", 1920) if config else 1920
                height = config.get("height", 1080) if config else 1080
                controller_type = config.get("controller_type", "").split()[0] if config else ""
                
                screen = self.screen_manager.create_screen_for_device(controller_name, controller_type, width, height, file_path)
                self.file_manager.save_screen_to_file(screen, file_path)
                self.load_soo_file(file_path, clear_existing=False)
    
    def load_soo_file(self, file_path: str, clear_existing: bool = False):
        result = self.file_manager.load_soo_file(file_path, clear_existing)
        logger.info(f"Loaded file: {file_path}, result: {result}")
        if result:
            if hasattr(self, 'screen_list_panel'):
                self.screen_list_panel.refresh_screens(debounce=False)
            if hasattr(self, 'content_widget'):
                self.content_widget.update()
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
    
    def _on_new_program(self):
        if hasattr(self, 'screen_list_panel'):
            from core.screen_config import get_screen_name
            screen_name = get_screen_name()
            self.screen_list_panel.add_program_to_screen(screen_name)
    
    def _on_new_screen(self):
        if hasattr(self, 'screen_list_panel'):
            self.screen_list_panel.add_new_screen()    
    
    def _on_login_requested(self):
        try:
            from ui.login_dialog import LoginDialog
            from core.startup_service import StartupService
            
            startup_service = StartupService()
            controller_id, _ = startup_service.verify_license_at_startup()
            
            if self.controller_service.is_online() and self.current_controller:
                controller_id = self.current_controller.get('controller_id') or controller_id
            
            login_dialog = LoginDialog(controller_id=controller_id, parent=self)
            dialog_result = login_dialog.exec()
            
            if dialog_result:
                controller_id = login_dialog.controller_id or controller_id
                if controller_id and login_dialog.is_license_valid():
                    if startup_service.check_license_after_activation(controller_id):
                        logger.info(f"License activated for controller: {controller_id}")
                        QMessageBox.information(self, "License Activated", f"License successfully activated for controller: {controller_id}")
                        self._update_license_dependent_actions()
                    else:
                        logger.warning(f"License validation failed for controller: {controller_id}")
                        QMessageBox.warning(self, "License Validation Failed", f"License validation failed for controller: {controller_id}")
                else:
                    logger.info("License activation cancelled or invalid")
        except Exception as e:
            logger.exception(f"Error showing login dialog: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while opening login dialog:\n{str(e)}")
    
    def _on_network_config_requested(self):
        try:
            from ui.network_config_dialog import NetworkConfigDialog
            
            controller = None
            if self.controller_service and self.controller_service.is_online():
                controller = self.current_controller
            
            if not controller:
                QMessageBox.warning(self, "No Controller", "Please connect to a controller first.")
                return
            
            dialog = NetworkConfigDialog(parent=self, controller=controller)
            dialog.exec()
        except Exception as e:
            logger.exception(f"Error opening network config dialog: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while opening the dialog:\n{str(e)}")
    
    def _on_time_requested(self):
        try:
            from ui.time_dialog import TimeDialog
            
            controller = None
            if self.controller_service and self.controller_service.is_online():
                controller = self.current_controller
            
            if not controller:
                QMessageBox.warning(self, "No Controller", "Please connect to a controller first.")
                return
            
            screen_name = None
            if self.screen_manager and self.screen_manager.current_screen:
                screen_name = self.screen_manager.current_screen.name
            
            dialog = TimeDialog(parent=self, controller=controller, screen_name=screen_name)
            dialog.exec()
        except Exception as e:
            logger.exception(f"Error opening time dialog: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while opening the dialog:\n{str(e)}")
    
    def _on_brightness_requested(self):
        try:
            from ui.brightness_dialog import BrightnessDialog
            
            controller = None
            if self.controller_service and self.controller_service.is_online():
                controller = self.current_controller
            
            if not controller:
                QMessageBox.warning(self, "No Controller", "Please connect to a controller first.")
                return
            
            screen_name = None
            if self.screen_manager and self.screen_manager.current_screen:
                screen_name = self.screen_manager.current_screen.name
            
            dialog = BrightnessDialog(parent=self, controller=controller, screen_name=screen_name)
            dialog.exec()
        except Exception as e:
            logger.exception(f"Error opening brightness dialog: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while opening the dialog:\n{str(e)}")
    
    def _on_power_requested(self):
        try:
            from ui.power_dialog import PowerDialog
            
            controller = None
            if self.controller_service and self.controller_service.is_online():
                controller = self.current_controller
            
            if not controller:
                QMessageBox.warning(self, "No Controller", "Please connect to a controller first.")
                return
            
            screen_name = None
            if self.screen_manager and self.screen_manager.current_screen:
                screen_name = self.screen_manager.current_screen.name
            
            dialog = PowerDialog(parent=self, controller=controller, screen_name=screen_name)
            dialog.exec()
        except Exception as e:
            logger.exception(f"Error opening power dialog: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while opening the dialog:\n{str(e)}")
    
    def _on_schedule_requested(self):
        try:
            from ui.schedule_dialog import ScheduleDialog
            
            if not self.screen_manager or not self.screen_manager.current_screen:
                QMessageBox.warning(self, "No Screen", "Please select a screen first.")
                return
            
            if not self.screen_manager.current_screen.programs:
                QMessageBox.warning(self, "No Program", "Please add a program to the screen first.")
                return
            
            dialog = ScheduleDialog(parent=self, screen_manager=self.screen_manager)
            dialog.exec()
        except Exception as e:
            logger.exception(f"Error opening schedule dialog: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while opening the dialog:\n{str(e)}")
    
    def _update_license_dependent_actions(self):
        try:
            has_license = False
            is_online = self.controller_service.is_online()
            
            if is_online:
                controller = self.current_controller
                if controller:
                    controller_id = controller.get("controller_id") if isinstance(controller, dict) else None
                    if controller_id:
                        try:
                            from core.license_manager import LicenseManager
                            license_manager = LicenseManager()
                            license_file = license_manager.get_license_file_path(controller_id)
                            has_license = license_file.exists()
                        except Exception as e:
                            logger.error(f"Error checking license: {e}", exc_info=True)
            
            send_enabled = is_online and has_license
            insert_enabled = is_online and has_license
            import_enabled = is_online and has_license
            export_enabled = is_online and has_license
            
            
            if hasattr(self, 'control_toolbar'):
                for action in self.control_toolbar.actions():
                    action_text = action.text()
                    if action_text:
                        if "⬆️" in action_text or "Send" in action_text:
                            pass
                        elif "📲" in action_text or "Insert" in action_text:
                            pass
        except Exception as e:
            logger.error(f"Error updating license-dependent actions: {e}", exc_info=True)
    
    def _read_brightness_on_connection(self):
        try:
            if not self.controller_service or not self.current_controller:
                return
            
            controller = self.current_controller
            if hasattr(controller, 'get_brightness'):
                brightness = controller.get_brightness()
                if brightness is not None:
                    logger.info(f"Brightness read from controller: {brightness}%")
                else:
                    logger.warning("Could not read brightness from controller")
        except Exception as e:
            logger.warning(f"Error reading brightness on connection: {e}", exc_info=True)
    
    def update_controller(self, controller_dict):
        if hasattr(self, 'status_bar') and self.status_bar:
            if hasattr(self.status_bar, '_update_status'):
                self.status_bar._update_status()
            elif controller_dict:
                is_online = controller_dict.get("is_online", False)
                controller_name = controller_dict.get("name", "")
                self.status_bar.set_connection_status(is_online, controller_name)
            else:
                self.status_bar.set_connection_status(False, "")
    
    def _on_export_logs_requested(self):
        try:
            from utils.logger import export_all_logs, get_log_directory
            from datetime import datetime
            
            # Suggest a default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"SLPlayer_Logs_{timestamp}.txt"
            
            # Open file dialog to choose save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Logs",
                default_filename,
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if not file_path:
                return  # User cancelled
            
            from pathlib import Path
            output_path = Path(file_path)
            
            # Export the logs
            success = export_all_logs(output_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"All logs have been exported to:\n{output_path}\n\n"
                    f"Log directory: {get_log_directory()}"
                )
                logger.info(f"Logs exported to: {output_path}")
            else:
                log_dir = get_log_directory()
                if not log_dir.exists():
                    QMessageBox.warning(
                        self,
                        "No Logs Found",
                        f"No log directory found at:\n{log_dir}\n\n"
                        "Logs will be created when the application runs."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        f"Failed to export logs.\n\n"
                        f"Log directory: {log_dir}\n"
                        "Check if log files exist and you have write permissions."
                    )
        except Exception as e:
            logger.exception(f"Error exporting logs: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting logs:\n{str(e)}"
            )
    
    
    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, '_device_dialog') and self._device_dialog:
            self._device_dialog.hide()
            if hasattr(self._device_dialog, 'select_btn'):
                self._device_dialog.select_btn.setEnabled(False)
    
    def closeEvent(self, event):
        try:
            if self.screen_manager and self.screen_manager.screens:
                controller_name = None
                if self.controller_service and self.current_controller:
                    controller_name = self.current_controller.get('name')
                saved_count = self.file_manager.save_all_screens(controller_name)
                logger.info(f"Auto-saved {saved_count} screen(s) to work directory on close")
        except Exception as e:
            logger.error(f"Error auto-saving on close: {e}", exc_info=True)
        
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())