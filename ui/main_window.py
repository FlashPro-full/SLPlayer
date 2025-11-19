from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QDialog,
    QMessageBox, QInputDialog, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QPainter, QColor
from typing import Optional, Dict, List
from datetime import datetime
import uuid

from config.settings import settings
from config.i18n import tr, set_language
from core.program_manager import ProgramManager, Program
from core.screen_manager import ScreenManager
from core.file_manager import FileManager
from core.event_bus import event_bus
from services.program_service import ProgramService
from services.file_service import FileService
from services.controller_service import ControllerService
from ui.menu_bar import MenuBar
from ui.toolbar import (
    ProgramToolbar, ContentTypesToolbar, PlaybackToolbar, ControlToolbar
)
from ui.status_bar import StatusBarWidget
from controllers.base_controller import BaseController, ConnectionStatus
from controllers.novastar import NovaStarController
from controllers.huidu import HuiduController
from core.sync_manager import SyncManager
from utils.logger import get_logger

logger = get_logger(__name__)


class ChessboardBackgroundWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tile_size = 12
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        widget_width = self.width()
        widget_height = self.height()
        
        color1 = QColor(240, 240, 240)
        color2 = QColor(255, 255, 255)
        
        for row in range(0, widget_height, self.tile_size):
            for col in range(0, widget_width, self.tile_size):
                if ((row // self.tile_size) + (col // self.tile_size)) % 2 == 0:
                    painter.fillRect(col, row, self.tile_size, self.tile_size, color1)
                else:
                    painter.fillRect(col, row, self.tile_size, self.tile_size, color2)


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLPlayer")
        
        self.program_manager = ProgramManager()
        self.file_manager = FileManager(self.program_manager)
        self.sync_manager = SyncManager()
        
        self.program_service = ProgramService(self.program_manager)
        self.file_service = FileService(self.program_manager, self.file_manager)
        self.controller_service = ControllerService()
        
        self.clipboard_program: Optional[Dict] = None
        self._latest_file_loaded = False
        self._screen_dialog_opened = False
        self.current_controller: Optional[BaseController] = None
        
        self.init_ui()
        self.connect_signals()
        self._connect_event_bus()
        
        self._latest_file_loaded = self.file_service.load_latest_files()
        
        QTimer.singleShot(100, self._perform_startup_tasks)
    
    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.setVisible(True)
        
        central_widget = ChessboardBackgroundWidget(self)
        self.setCentralWidget(central_widget)
        
        self.program_toolbar = ProgramToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.program_toolbar)
        
        self.visible_content_toolbar = ContentTypesToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.visible_content_toolbar)
        
        self.playback_control_toolbar = PlaybackToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.playback_control_toolbar)
        
        self.control_toolbar = ControlToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.control_toolbar)
        
        from core.auto_save import AutoSaveManager
        self.auto_save_manager = AutoSaveManager(self.program_manager, self.file_manager)
        self.auto_save_manager.start()
        
        self.status_bar = StatusBarWidget(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
        
        self._ui_components_initialized = True
    
    def connect_signals(self):
        self.menu_bar.exit_requested.connect(self.close)
        self.menu_bar.screen_settings_requested.connect(self.on_display_settings)
        self.menu_bar.language_changed.connect(self.on_language_changed)
        self.menu_bar.save_program_requested.connect(self.on_save_program)
        self.menu_bar.open_program_requested.connect(self.on_open_program)
        self.menu_bar.new_program_requested.connect(self.on_new_program_from_menu)
        
        self.menu_bar.device_info_requested.connect(self.on_device_info)
        self.menu_bar.upload_requested.connect(self.on_upload)
        self.menu_bar.download_requested.connect(self.on_download)
        self.menu_bar.discover_controllers_requested.connect(self.on_discover_controllers)
        self.menu_bar.dashboard_requested.connect(self.on_dashboard)
        self.menu_bar.connect_requested.connect(self.on_connect_controller)
        self.menu_bar.disconnect_requested.connect(self.on_disconnect_controller)
        self.menu_bar.time_power_brightness_requested.connect(self.on_time_power_brightness)
        self.menu_bar.network_config_requested.connect(self.on_network_config)
        self.menu_bar.diagnostics_requested.connect(self.on_diagnostics)
        self.menu_bar.import_requested.connect(self.on_import)
        self.menu_bar.export_requested.connect(self.on_export)
        self.menu_bar.import_xml_requested.connect(self.on_import_xml)
        self.menu_bar.export_xml_requested.connect(self.on_export_xml)
        
        self._connect_toolbar_signals()
    
    def _connect_event_bus(self):
        event_bus.program_created.connect(self._on_program_created)
        event_bus.program_updated.connect(self._on_program_updated)
        event_bus.program_selected.connect(self._on_program_selected_event)
        event_bus.program_saved.connect(self._on_program_saved)
        
        event_bus.ui_program_list_refresh.connect(self._on_program_list_refresh_needed)
        
        event_bus.file_loaded.connect(self._on_file_loaded)
        event_bus.file_error.connect(self._on_file_error)
        
        event_bus.controller_connected.connect(self._on_controller_connected)
        event_bus.controller_disconnected.connect(self._on_controller_disconnected)
        event_bus.controller_error.connect(self._on_controller_error)
    
    def _on_program_created(self, program: Program):
        pass
    
    def _on_program_updated(self, program: Program):
        if program == self.program_manager.current_program:
            self._update_ui_for_program(program, refresh_list=False)
    
    def _on_program_selected_event(self, program_id: str):
        program = self.program_manager.get_program_by_id(program_id)
        if program:
            self._update_ui_for_program(program)
    
    def _on_program_saved(self, program: Program, file_path: str):
        logger.debug(f"Program saved: {program.name} to {file_path}")
    
    def _on_file_loaded(self, file_path: str):
        pass
    
    def _on_file_error(self, file_path: str, error: str):
        QMessageBox.warning(self, "File Error", f"Error with file {file_path}:\n{error}")
    
    def _on_controller_connected(self, controller: BaseController):
        self.current_controller = controller
        if self._ui_components_initialized:
            device_info = controller.get_device_info() if controller else None
            device_name = device_info.get("name", "") if device_info else ""
            self.status_bar.set_connection_status(controller.get_connection_status(), device_name)
            
            if not hasattr(self, '_status_update_timer'):
                from PyQt5.QtCore import QTimer
                self._status_update_timer = QTimer()
                self._status_update_timer.timeout.connect(self._update_connection_status)
                self._status_update_timer.start(5000)
    
    def _on_controller_disconnected(self):
        self.current_controller = None
        if self._ui_components_initialized:
            from controllers.base_controller import ConnectionStatus
            self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
            
            if hasattr(self, '_status_update_timer'):
                self._status_update_timer.stop()
    
    def _update_connection_status(self):
        if self._ui_components_initialized and self.current_controller:
            status = self.current_controller.get_connection_status()
            device_info = self.current_controller.get_device_info() if self.current_controller else None
            device_name = device_info.get("name", "") if device_info else ""
            self.status_bar.set_connection_status(status, device_name)
    
    def _auto_check_connection_status(self):
        if not self._ui_components_initialized:
            return
        
        if not self.current_controller:
            if not hasattr(self, '_last_network_check') or \
               (datetime.now() - self._last_network_check).total_seconds() > 30:
                self._last_network_check = datetime.now()
                self._perform_network_check()
        
        if self.current_controller:
            self._update_connection_status()
        else:
            from controllers.base_controller import ConnectionStatus
            self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
    
    def _perform_network_check(self):
        try:
            from core.controller_discovery import ControllerDiscovery
            discovery = ControllerDiscovery(self)
            
            def on_discovery_finished():
                controllers = discovery.get_discovered_controllers()
                if controllers and not self.current_controller:
                    ctrl = controllers[0]
                    self.connect_to_controller(ctrl.ip, ctrl.port, ctrl.controller_type)
            
            discovery.discovery_finished.connect(on_discovery_finished)
            discovery.start_scan()
        except Exception as e:
            logger.debug(f"Network check error (non-critical): {e}")
    
    def _on_controller_error(self, error: str):
        QMessageBox.warning(self, "Controller Error", error)
    
    def _on_program_list_refresh_needed(self):
        if self._ui_components_initialized:
            self._throttled_refresh()
    
    def _do_program_list_refresh(self):
        pass
    
    def _throttled_refresh(self):
        if not hasattr(self, '_refresh_timer'):
            self._refresh_timer = QTimer()
            self._refresh_timer.setSingleShot(True)
            self._refresh_timer.timeout.connect(self._do_program_list_refresh)
        
        self._refresh_timer.stop()
        self._refresh_timer.start(100)
    
    def _connect_program_list_signals(self):
        pass
    
    def _connect_toolbar_signals(self):
        self.visible_content_toolbar.content_type_selected.connect(self.on_content_type_selected)
        self.playback_control_toolbar.action_triggered.connect(self.on_playback_action)
        self.control_toolbar.action_triggered.connect(self.on_control_action)
    
    def on_language_changed(self, language: str):
        set_language(language)
        if self._ui_components_initialized:
            self.menu_bar.refresh_texts()
    
    def on_content_type_selected(self, content_type: str):
        try:
            if self.program_manager and self.program_manager.current_program:
                from datetime import datetime
                program = self.program_manager.current_program
                
                screen_props = program.properties.get("screen", {})
                screen_width = screen_props.get("width")
                screen_height = screen_props.get("height")
                
                if not screen_width or not screen_height or screen_width <= 0 or screen_height <= 0:
                    screen_width = program.width
                    screen_height = program.height
                
                if not screen_width or not screen_height or screen_width <= 0 or screen_height <= 0:
                    from config.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT
                    screen_width = DEFAULT_CANVAS_WIDTH
                    screen_height = DEFAULT_CANVAS_HEIGHT
                
                element = {
                    "type": content_type,
                    "id": f"element_{datetime.now().timestamp()}",
                    "properties": {
                        "x": 0,
                        "y": 0,
                        "width": screen_width,
                        "height": screen_height
                    }
                }
                self.program_manager.current_program.elements.append(element)
                self.program_manager.current_program.modified = datetime.now().isoformat()
                if self.auto_save_manager:
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            logger.error(f"Error adding content: {e}", exc_info=True)
    
    def on_playback_action(self, action_id: str):
        logger.debug(f"Playback action: {action_id}")
    
    def on_control_action(self, action_id: str):
        logger.debug(f"Control action: {action_id}")
    
    def _update_ui_for_program(self, program: Program, refresh_list: bool = True):
        if self._ui_components_initialized:
            if program:
                self.status_bar.set_program_name(program.name)
    
    def _save_and_refresh(self, program: Program, file_path: Optional[str] = None):
        return self.file_service.save_file(program, file_path)
    
    def on_program_selected(self, program_id: str):
        try:
            if not self.program_manager:
                return
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                self.program_manager.current_program = program
                self._update_ui_for_program(program)
        except Exception as e:
            logger.error(f"Error selecting program: {e}")
    
    def on_screen_selected(self, screen_name: str):
        try:
            if not self.program_manager:
                return
            screen_programs = ScreenManager.get_programs_for_screen(
                self.program_manager.programs, screen_name
            )
            pass
        except Exception as e:
            logger.error(f"Error selecting screen '{screen_name}': {e}", exc_info=True)
    
    def on_new_program_from_menu(self):
        self._create_new_screen_with_dialog()
    
    def on_new_program(self):
        try:
            if not self.program_manager:
                return
            
            screen_name = None
            if self.program_manager.current_program:
                screen_name = ScreenManager.get_screen_name_from_program(self.program_manager.current_program)
            
            if not screen_name:
                screen_name = "Screen1"
            
            program_name = ScreenManager.generate_unique_program_name(
                self.program_manager.programs, screen_name
            )
            program = self.program_manager.create_program(program_name)
            
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            
            program.properties["screen"]["screen_name"] = screen_name
            
            screen_programs = ScreenManager.get_programs_for_screen(
                self.program_manager.programs, screen_name
            )
            
            for existing_program in screen_programs:
                if existing_program.id != program.id:
                    existing_screen = existing_program.properties.get("screen", {})
                    if isinstance(existing_screen, dict) and "width" in existing_screen and "height" in existing_screen:
                        program.properties["screen"]["width"] = existing_screen["width"]
                        program.properties["screen"]["height"] = existing_screen["height"]
                        if "rotate" in existing_screen:
                            program.properties["screen"]["rotate"] = existing_screen["rotate"]
                        if "brand" in existing_screen:
                            program.properties["screen"]["brand"] = existing_screen["brand"]
                        if "model" in existing_screen:
                            program.properties["screen"]["model"] = existing_screen["model"]
                        if "controller_type" in existing_screen:
                            program.properties["screen"]["controller_type"] = existing_screen["controller_type"]
                        if "controller_id" in existing_screen:
                            program.properties["screen"]["controller_id"] = existing_screen["controller_id"]
                        break
            
            self.program_manager.current_program = program
            self._save_and_refresh(program)
            self._update_ui_for_program(program)
            if hasattr(self, 'auto_save_manager'):
                self.auto_save_manager.save_current_program()
        except Exception as e:
            logger.error(f"Error creating new program: {e}")
    
    def _create_new_screen_with_dialog(self):
        try:
            from ui.screen_settings_dialog import ScreenSettingsDialog
            from pathlib import Path
            import time
            
            self._screen_dialog_opened = True
            
            dialog = ScreenSettingsDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                if self.program_manager:
                    w, h = dialog.selected_size()
                    rotate = dialog.selected_rotate()
                    series = dialog.selected_series()
                    model = dialog.selected_model()
                    ctrl_id = dialog.selected_controller_id()
                    
                    existing_screen_names = set()
                    for p in self.program_manager.programs:
                        p_screen_name = ScreenManager.get_screen_name_from_program(p)
                        if p_screen_name:
                            existing_screen_names.add(p_screen_name)
                    
                    screen_name = None
                    counter = 1
                    while not screen_name or screen_name in existing_screen_names:
                        screen_name = f"Screen{counter}"
                        counter += 1
                        if counter > 1000:
                            screen_name = f"Screen_{int(time.time())}"
                            break
                    
                    program1_name = "Program1"
                    existing_program_names = [p.name for p in self.program_manager.programs]
                    counter = 1
                    while program1_name in existing_program_names:
                        counter += 1
                        program1_name = f"Program{counter}"
                    
                    program1 = self.program_manager.create_program(program1_name, w, h)
                    if "screen" not in program1.properties:
                        program1.properties["screen"] = {}
                    program1.properties["screen"]["screen_name"] = screen_name
                    program1.properties["screen"]["width"] = w
                    program1.properties["screen"]["height"] = h
                    program1.properties["screen"]["rotate"] = rotate
                    program1.properties["screen"]["brand"] = series
                    program1.properties["screen"]["model"] = model
                    program1.properties["screen"]["controller_type"] = f"{series} {model}" if model else series
                    if ctrl_id:
                        program1.properties["screen"]["controller_id"] = ctrl_id
                    
                    self.program_manager.current_program = program1
                    self._save_and_refresh(program1)
                    
                    logger.info(f"Created new screen: {screen_name}, program: {program1.name}, width: {w}, height: {h}, rotate: {rotate}, programs count: {len(self.program_manager.programs)}")
                    
                    self._update_ui_for_program(program1)
                    if self.auto_save_manager:
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            logger.error(f"Error creating new screen: {e}", exc_info=True)
    
    def on_delete_program(self, program_id: str):
        try:
            if not self.program_manager:
                return
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                self.program_manager.delete_program(program)
                
                self._cleanup_orphaned_files()
                
                QTimer.singleShot(100, self._check_and_open_screen_dialog_if_needed)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error deleting program: {e}")
    
    def on_program_renamed(self, program_id: str, new_name: str):
        from datetime import datetime
        try:
            if not self.program_manager:
                return
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                old_name = program.name
                program.name = new_name
                program.modified = datetime.now().isoformat()
                self._save_and_refresh(program)
                self._update_ui_for_program(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error renaming program: {e}")
    
    def on_program_duplicated(self, program_id: str):
        import uuid
        from datetime import datetime
        from core.program_manager import Program
        try:
            if self.program_manager:
                program = self.program_manager.get_program_by_id(program_id)
                if program:
                    program_data = program.to_dict()
                    new_program = Program()
                    new_program.from_dict(program_data)
                    new_program.id = f"program_{uuid.uuid4().hex[:12]}"
                    new_program.name = f"{program.name} (Copy)"
                    new_program.created = datetime.now().isoformat()
                    new_program.modified = datetime.now().isoformat()
                    self.program_manager.programs.append(new_program)
                    self.program_manager.current_program = new_program
                    if "screen" in program.properties:
                        new_program.properties["screen"] = program.properties["screen"].copy()
                    self._save_and_refresh(new_program)
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error duplicating program: {e}")
    
    def on_program_moved(self, program_id: str, direction: int):
        try:
            if self.program_manager:
                programs = self.program_manager.programs
                current_index = next((i for i, p in enumerate(programs) if p.id == program_id), None)
                if current_index is not None:
                    new_index = current_index + direction
                    if 0 <= new_index < len(programs):
                        programs[current_index], programs[new_index] = programs[new_index], programs[current_index]
                        if hasattr(self, 'auto_save_manager'):
                            self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error moving program: {e}")
    
    def on_program_activated(self, program_id: str, enabled: bool):
        from datetime import datetime
        try:
            if self.program_manager:
                program = self.program_manager.get_program_by_id(program_id)
                if program:
                    if "activation" not in program.properties:
                        program.properties["activation"] = {}
                    program.properties["activation"]["enabled"] = enabled
                    program.modified = datetime.now().isoformat()
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error activating/deactivating program: {e}")
    
    def on_program_checked(self, program_id: str, checked: bool):
        try:
            if self.program_manager:
                program = self.program_manager.get_program_by_id(program_id)
                if program:
                    program.properties["checked"] = checked
                    program.modified = datetime.now().isoformat()
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error checking/unchecking program: {e}")
    
    
    def on_display_settings(self):
        try:
            from ui.screen_settings_dialog import ScreenSettingsDialog
            dlg = ScreenSettingsDialog(self)
            if dlg.exec():
                w, h = dlg.selected_size()
                rotate = dlg.selected_rotate()
                if self.program_manager and self.program_manager.current_program:
                    program = self.program_manager.current_program
                    if "screen" not in program.properties:
                        program.properties["screen"] = {}
                    
                    program.properties["screen"]["width"] = w
                    program.properties["screen"]["height"] = h
                    program.properties["screen"]["rotate"] = rotate
                    program.properties["screen"]["brand"] = dlg.selected_series()
                    program.properties["screen"]["model"] = dlg.selected_model()
                    program.properties["screen"]["controller_type"] = f"{dlg.selected_series()} {dlg.selected_model()}"
                    
                    if dlg.controller_combo.currentIndex() > 0:
                        row = dlg.controller_combo.currentIndex() - 1
                        if row < len(dlg.controller_data):
                            controller_id = dlg.controller_data[row].get("controller_id")
                            if controller_id:
                                program.properties["screen"]["controller_id"] = controller_id
                    
                    screen_name = ScreenManager.determine_screen_name(program)
                    if screen_name:
                        program.properties["screen"]["screen_name"] = screen_name
                    
                    screen_programs = ScreenManager.get_programs_for_screen(
                        self.program_manager.programs, screen_name
                    )
                    for p in screen_programs:
                        if "screen" not in p.properties:
                            p.properties["screen"] = {}
                        p.properties["screen"]["width"] = w
                        p.properties["screen"]["height"] = h
                        p.properties["screen"]["rotate"] = rotate
                    
                    self._update_ui_for_program(program)
                    self._save_and_refresh(program)
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            logger.error(f"Error in display settings: {e}")
    
    def load_soo_file(self, file_path: str, clear_existing: bool = False) -> bool:
        result = self.file_manager.load_soo_file(file_path, clear_existing)
        if result:
            if self.program_manager and self.program_manager.current_program:
                self._update_ui_for_program(self.program_manager.current_program)
        return result
    
    def on_open_program(self, file_path: str = ""):
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Open Program",
                    "",
                    "Program Files (*.soo);;All Files (*)"
                )
            
            if file_path:
                result = self.load_soo_file(file_path, clear_existing=False)
                if result:
                    QMessageBox.information(self, "Success", f"Program loaded from: {file_path}")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to load program from: {file_path}")
        except Exception as e:
            logger.error(f"Error opening program: {e}")
            QMessageBox.critical(self, "Error", f"Error opening program: {e}")
    
    
    def on_save_program(self, file_path: str = ""):
        try:
            if not self.program_manager or not self.program_manager.current_program:
                QMessageBox.warning(self, "Save", "No program to save.")
                return
        
            program = self.program_manager.current_program
            screen_name = ScreenManager.get_screen_name_from_program(program)
            if not screen_name:
                QMessageBox.warning(self, "Save", "No screen associated with current program.")
                return
        
            from PyQt5.QtWidgets import QFileDialog
            from pathlib import Path
            
            default_name = screen_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
            
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Program",
                    f"{default_name}.soo",
                    "Program Files (*.soo);;All Files (*)"
                )
            
            if file_path:
                if not file_path.endswith('.soo'):
                    file_path += '.soo'
                
                result = self._save_and_refresh(program, file_path)
                
                if result:
                    logger.info(f"Program saved to: {file_path}")
                    QMessageBox.information(self, "Success", f"Program saved to: {file_path}")
                else:
                    logger.error(f"Failed to save program to: {file_path}")
                    QMessageBox.warning(self, "Error", f"Failed to save program to: {file_path}")
        except Exception as e:
            logger.error(f"Error saving program: {e}", exc_info=True)
    
    def on_screen_renamed(self, screen_name: str, new_name: str):
        try:
            if not new_name:
                new_name, ok = QInputDialog.getText(self, "Rename Screen", "Enter new screen name:", text=screen_name)
                if not ok or not new_name:
                    return
            
            if self.program_manager:
                for program in self.program_manager.programs:
                    program_screen_name = ScreenManager.get_screen_name_from_program(program)
                    if program_screen_name == screen_name:
                        if "screen" not in program.properties:
                            program.properties["screen"] = {}
                        program.properties["screen"]["screen_name"] = new_name
                        program.modified = datetime.now().isoformat()
                        self._save_and_refresh(program)
                        if hasattr(self, 'auto_save_manager'):
                            self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error renaming screen: {e}")
    
    def on_screen_deleted(self, screen_name: str):
        try:
            reply = QMessageBox.question(
                self, 
                "Delete Screen", 
                f"Are you sure you want to delete screen '{screen_name}' and all its programs?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.program_manager:
                    programs_to_delete = []
                    for program in self.program_manager.programs:
                        program_screen_name = ScreenManager.get_screen_name_from_program(program)
                        if program_screen_name == screen_name:
                            programs_to_delete.append(program)
                    
                    for program in programs_to_delete:
                        self.program_manager.delete_program(program)
                    
                    self._cleanup_orphaned_files()
                    
                    QTimer.singleShot(100, self._check_and_open_screen_dialog_if_needed)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error deleting screen: {e}")
    
    def on_new_screen(self):
        self._create_new_screen_with_dialog()
    
    def on_add_program(self, screen_name: str):
        try:
            if not self.program_manager:
                return
            
            screen_programs = ScreenManager.get_programs_for_screen(
                self.program_manager.programs, screen_name
            )
            
            latest_num = 0
            for p in screen_programs:
                name = p.name
                if name.startswith("Program"):
                    try:
                        num_str = name.replace("Program", "").strip()
                        if num_str and num_str.isdigit():
                            num = int(num_str)
                            latest_num = max(latest_num, num)
                    except ValueError:
                        pass
            
            new_program_num = latest_num + 1
            program_name = f"Program{new_program_num}"
            
            existing_program_names = [p.name for p in self.program_manager.programs]
            counter = new_program_num
            while program_name in existing_program_names:
                counter += 1
                program_name = f"Program{counter}"
            
            program = self.program_manager.create_program(program_name)
            
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            
            program.properties["screen"]["screen_name"] = screen_name
            
            for existing_program in screen_programs:
                if existing_program.id != program.id:
                    existing_screen = existing_program.properties.get("screen", {})
                    if isinstance(existing_screen, dict) and "width" in existing_screen and "height" in existing_screen:
                        program.properties["screen"]["width"] = existing_screen["width"]
                        program.properties["screen"]["height"] = existing_screen["height"]
                        if "rotate" in existing_screen:
                            program.properties["screen"]["rotate"] = existing_screen["rotate"]
                        if "brand" in existing_screen:
                            program.properties["screen"]["brand"] = existing_screen["brand"]
                        if "model" in existing_screen:
                            program.properties["screen"]["model"] = existing_screen["model"]
                        if "controller_type" in existing_screen:
                            program.properties["screen"]["controller_type"] = existing_screen["controller_type"]
                        if "controller_id" in existing_screen:
                            program.properties["screen"]["controller_id"] = existing_screen["controller_id"]
                        break
            
            program.modified = datetime.now().isoformat()
            self._update_ui_for_program(program)
            self._save_and_refresh(program)
            if hasattr(self, 'auto_save_manager'):
                self.auto_save_manager.save_current_program()
        except Exception as e:
            logger.error(f"Error adding program: {e}")
    
    def on_screen_insert(self, screen_name: str):
        try:
            if self.program_manager and self.clipboard_program:
                program = Program()
                program.from_dict(self.clipboard_program)
                program.id = f"program_{uuid.uuid4().hex[:12]}"
                program.name = f"{program.name} (Inserted)"
                program.created = datetime.now().isoformat()
                program.modified = datetime.now().isoformat()
                
                if "screen" not in program.properties:
                    program.properties["screen"] = {}
                if isinstance(program.properties["screen"], dict):
                    program.properties["screen"]["screen_name"] = screen_name
                
                self.program_manager.programs.append(program)
                self.program_manager.current_program = program
                self._save_and_refresh(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error inserting program: {e}")
    
    def on_screen_download(self, screen_name: str):
        try:
            if self.program_manager:
                screen_programs = ScreenManager.get_programs_for_screen(
                    self.program_manager.programs, screen_name
                )
                
                if screen_programs:
                    from utils.logger import get_logger
                    logger = get_logger(__name__)
                    logger.info(f"Downloading {len(screen_programs)} programs from screen '{screen_name}' to controller")
                    QMessageBox.information(self, "Download", f"Downloading {len(screen_programs)} programs from screen '{screen_name}' to controller.")
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error downloading screen: {e}")
    
    def on_screen_close(self, screen_name: str):
        try:
            reply = QMessageBox.question(
                self, 
                "Close Screen", 
                f"Are you sure you want to close screen '{screen_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.program_manager:
                    for program in self.program_manager.programs:
                        program_screen_name = ScreenManager.get_screen_name_from_program(program)
                        if program_screen_name == screen_name:
                            if "activation" not in program.properties:
                                program.properties["activation"] = {}
                                program.properties["activation"]["enabled"] = False
                                program.modified = datetime.now().isoformat()
                            self.file_manager.save_soo_file_for_screen(program)
                            if hasattr(self, 'auto_save_manager'):
                                self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error closing screen: {e}")
    
    def on_screen_paste(self, screen_name: str):
        try:
            if self.program_manager and self.clipboard_program:
                import uuid
                program = Program()
                program.from_dict(self.clipboard_program)
                program.id = f"program_{uuid.uuid4().hex[:12]}"
                program.name = f"{program.name} (Pasted)"
                program.created = datetime.now().isoformat()
                program.modified = datetime.now().isoformat()
                
                if "screen" not in program.properties:
                    program.properties["screen"] = {}
                if isinstance(program.properties["screen"], dict):
                    program.properties["screen"]["screen_name"] = screen_name
                
                self.program_manager.programs.append(program)
                self.program_manager.current_program = program
                self._save_and_refresh(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error pasting program: {e}")
    
    def on_program_copy(self, program_id: str):
        try:
            if not self.program_manager:
                return
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                self.clipboard_program = program.to_dict()
                from utils.logger import get_logger
                logger = get_logger(__name__)
                logger.info(f"Program '{program.name}' copied to clipboard")
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error copying program: {e}")
    
    def on_program_paste(self, program_id: str):
        try:
            if self.program_manager and self.clipboard_program:
                target_program = self.program_manager.get_program_by_id(program_id)
                if target_program:
                    import uuid
                    for element_data in self.clipboard_program.get("elements", []):
                        new_element = element_data.copy()
                        new_element["id"] = f"element_{uuid.uuid4().hex[:12]}"
                        target_program.elements.append(new_element)
                    target_program.modified = datetime.now().isoformat()
                    self._save_and_refresh(target_program)
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error pasting elements: {e}")
    
    def on_program_add_content(self, program_id: str, content_type: str):
        try:
            if self.program_manager:
                program = self.program_manager.get_program_by_id(program_id)
                if program:
                    self.program_manager.current_program = program
                    self.on_content_type_selected(content_type)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error adding content to program: {e}")
    
    def on_content_selected(self, program_id: str, element_id: str):
        try:
            if not self.program_manager:
                return
            
            program = self.program_manager.get_program_by_id(program_id)
            if not program:
                return
            
            element = next((e for e in program.elements if e.get("id") == element_id), None)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error selecting content: {e}")
    
    def _on_property_changed(self, property_name: str, value):
        pass
    
    def on_content_renamed(self, program_id: str, element_id: str, new_name: str):
        try:
            if not self.program_manager:
                return
            
            program = self.program_manager.get_program_by_id(program_id)
            if not program:
                return
            
            element = next((e for e in program.elements if e.get("id") == element_id), None)
            if element:
                element["name"] = new_name
                program.modified = datetime.now().isoformat()
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error renaming content: {e}")
    
    def on_content_deleted(self, program_id: str, element_id: str):
        try:
            if not self.program_manager:
                return
            
            program = self.program_manager.get_program_by_id(program_id)
            if not program:
                return
            
            program.elements = [e for e in program.elements if e.get("id") != element_id]
            program.modified = datetime.now().isoformat()
            
            if hasattr(self, 'auto_save_manager'):
                self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error deleting content: {e}")
    
    def on_content_add_requested(self, program_id: str, content_type: str):
        try:
            if not self.program_manager:
                return
            
            program = self.program_manager.get_program_by_id(program_id)
            if not program:
                return
            
            name_map = {
                "image": "Photo",
                "picture": "Photo",
                "photo": "Photo",
                "singleline_text": "SingleLineText",
                "3d_text": "3D Text",
                "qrcode": "QR code"
            }
            element_name = name_map.get(content_type, content_type.replace("_", " ").title())
            
            screen_props = program.properties.get("screen", {})
            screen_width = screen_props.get("width")
            screen_height = screen_props.get("height")
            
            if not screen_width or not screen_height or screen_width <= 0 or screen_height <= 0:
                screen_width = program.width
                screen_height = program.height
            
            if not screen_width or not screen_height or screen_width <= 0 or screen_height <= 0:
                from config.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT
                screen_width = DEFAULT_CANVAS_WIDTH
                screen_height = DEFAULT_CANVAS_HEIGHT
            
            element = {
                "type": content_type,
                "id": f"element_{datetime.now().timestamp()}",
                "name": element_name,
                "properties": {
                    "x": 0,
                    "y": 0,
                    "width": screen_width,
                    "height": screen_height
                }
            }
            
            program.elements.append(element)
            program.modified = datetime.now().isoformat()
            
            if hasattr(self, 'auto_save_manager'):
                self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error adding content: {e}")

    def open_screen_settings_on_startup(self):
        if self._screen_dialog_opened:
            logger.info("Screen settings dialog already opened, skipping")
            return
            
        if hasattr(self, '_latest_file_loaded') and self._latest_file_loaded:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.info("Skipping screen settings dialog - file already loaded")
            return
        if hasattr(self, 'program_manager') and self.program_manager and self.program_manager.programs:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.info(f"Skipping screen settings dialog - {len(self.program_manager.programs)} programs already exist")
            return
        try:
            self._screen_dialog_opened = True
            from ui.screen_settings_dialog import ScreenSettingsDialog
            dlg = ScreenSettingsDialog(self)
            if dlg.exec():
                w, h = dlg.selected_size()
                rotate = dlg.selected_rotate()
                series = dlg.selected_series()
                model = dlg.selected_model()
                ctrl_id = dlg.selected_controller_id()
                
                if self.program_manager:
                    screen_name = None
                    if self.program_manager.current_program and "screen" in self.program_manager.current_program.properties:
                        screen_name = ScreenManager.get_screen_name_from_program(self.program_manager.current_program)
                    
                    if not screen_name:
                        screen_name = "Screen1"
                    
                    program_name = ScreenManager.generate_unique_program_name(
                        self.program_manager.programs, screen_name
                    )
                    program = self.program_manager.create_program(program_name)
                    self.program_manager.current_program = program
                    
                    if "screen" not in program.properties:
                        program.properties["screen"] = {}
                    
                    program.properties["screen"]["width"] = w
                    program.properties["screen"]["height"] = h
                    program.properties["screen"]["rotate"] = rotate
                    program.properties["screen"]["brand"] = series
                    program.properties["screen"]["model"] = model
                    program.properties["screen"]["controller_type"] = f"{series} {model}" if model else series
                    
                    if ctrl_id:
                        program.properties["screen"]["controller_id"] = ctrl_id
                    
                    if screen_name:
                        program.properties["screen"]["screen_name"] = screen_name
                    
                self._save_and_refresh(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error opening screen settings: {e}")
    
    def closeEvent(self, event):
        try:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            
            if self.program_manager and self.program_manager.programs:
                screens_saved = set()
                for program in self.program_manager.programs:
                    screen_name = ScreenManager.get_screen_name_from_program(program)
                    if screen_name and screen_name not in screens_saved:
                        try:
                            self.file_manager.save_soo_file_for_screen(program)
                            screens_saved.add(screen_name)
                            logger.info(f"Autosaved screen: {screen_name}")
                        except Exception as e:
                            logger.error(f"Error autosaving screen {screen_name}: {e}")
                
                logger.info(f"Autosaved {len(screens_saved)} screen(s) on close")
            
            if hasattr(self, 'auto_save_manager'):
                self.auto_save_manager.stop()
            
            event.accept()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error in closeEvent: {e}")
            event.accept()
    
    def auto_discover_controllers(self):
        try:
            from core.controller_discovery import ControllerDiscovery
            discovery = ControllerDiscovery(self)
            discovery.discovery_finished.connect(lambda: self.on_discovery_finished(discovery))
            discovery.start_scan()
        except Exception as e:
            logger.error(f"Error in auto-discovery: {e}")
    
    def on_discovery_finished(self, discovery):
        controllers = discovery.get_discovered_controllers()
        if controllers:
            logger.info(f"Auto-discovered {len(controllers)} controller(s)")
            if len(controllers) == 1:
                ctrl = controllers[0]
                self.connect_to_controller(ctrl.ip, ctrl.port, ctrl.controller_type)
    
    def on_discover_controllers(self):
        try:
            from ui.dashboard_dialog import DashboardDialog
            dialog = DashboardDialog(self)
            dialog.controller_selected.connect(self.on_controller_selected_from_dashboard)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Error in discover controllers: {e}")
            QMessageBox.warning(self, "Error", f"Error discovering controllers: {e}")
    
    def on_controller_selected_from_dashboard(self, ip: str, port: int, controller_type: str):
        self.connect_to_controller(ip, port, controller_type)
    
    def on_dashboard(self):
        self.on_discover_controllers()
    
    def connect_to_controller(self, ip: str, port: int, controller_type: str):
        try:
            if self.current_controller:
                self.current_controller.disconnect()
            
            if controller_type == "novastar":
                self.current_controller = NovaStarController(ip, port)
            elif controller_type == "huidu":
                self.current_controller = HuiduController(ip, port)
            else:
                QMessageBox.warning(self, "Error", f"Unknown controller type: {controller_type}")
                return
            
            self.status_bar.set_connection_status(ConnectionStatus.CONNECTING)
            if self.current_controller.connect():
                device_info = self.current_controller.get_device_info()
                device_name = device_info.get("name", "") if device_info else ""
                self.status_bar.set_connection_status(ConnectionStatus.CONNECTED, device_name)
                logger.info(f"Connected to {controller_type} controller at {ip}:{port}")
                
                if self.program_manager.current_program:
                    if "screen" not in self.program_manager.current_program.properties:
                        self.program_manager.current_program.properties["screen"] = {}
                    
                    self.program_manager.current_program.properties["screen"]["controller_id"] = self.current_controller.get_controller_id()
                    self.program_manager.current_program.properties["screen"]["controller_type"] = controller_type
                    
                    if device_info:
                        resolution = (
                            device_info.get("display_resolution") or
                            device_info.get("resolution") or
                            device_info.get("screen_resolution") or
                            device_info.get("screen_size")
                        )
                        
                        if resolution:
                            if isinstance(resolution, str) and "x" in resolution.lower():
                                try:
                                    parts = resolution.lower().replace(" ", "").split("x")
                                    if len(parts) == 2:
                                        ctrl_width = int(parts[0])
                                        ctrl_height = int(parts[1])
                                        self.program_manager.current_program.properties["screen"]["width"] = ctrl_width
                                        self.program_manager.current_program.properties["screen"]["height"] = ctrl_height
                                        logger.info(f"Set controller screen resolution from device_info: {ctrl_width}x{ctrl_height}")
                                except (ValueError, IndexError) as e:
                                    logger.warning(f"Could not parse resolution string '{resolution}': {e}")
                            elif isinstance(resolution, dict):
                                ctrl_width_val = resolution.get("width") or resolution.get("w")
                                ctrl_height_val = resolution.get("height") or resolution.get("h")
                                if ctrl_width_val is not None and ctrl_height_val is not None:
                                    try:
                                        ctrl_width = int(ctrl_width_val)
                                        ctrl_height = int(ctrl_height_val)
                                        self.program_manager.current_program.properties["screen"]["width"] = ctrl_width
                                        self.program_manager.current_program.properties["screen"]["height"] = ctrl_height
                                        logger.info(f"Set controller screen resolution from device_info dict: {ctrl_width}x{ctrl_height}")
                                    except (ValueError, TypeError):
                                        logger.warning(f"Invalid resolution values: {ctrl_width_val}x{ctrl_height_val}")
                        
                        if isinstance(self.program_manager.current_program.properties.get("screen"), dict):
                            if "width" not in self.program_manager.current_program.properties["screen"]:
                                ctrl_width_val = device_info.get("width") or device_info.get("screen_width")
                                ctrl_height_val = device_info.get("height") or device_info.get("screen_height")
                                if ctrl_width_val is not None and ctrl_height_val is not None:
                                    try:
                                        ctrl_width = int(ctrl_width_val)
                                        ctrl_height = int(ctrl_height_val)
                                        self.program_manager.current_program.properties["screen"]["width"] = ctrl_width
                                        self.program_manager.current_program.properties["screen"]["height"] = ctrl_height
                                        logger.info(f"Set controller screen resolution from direct fields: {ctrl_width}x{ctrl_height}")
                                    except (ValueError, TypeError):
                                        logger.warning(f"Invalid resolution values: {ctrl_width_val}x{ctrl_height_val}")
                        
                        if isinstance(self.program_manager.current_program.properties.get("screen"), dict):
                            if "brand" not in self.program_manager.current_program.properties["screen"]:
                                brand = device_info.get("brand") or device_info.get("manufacturer")
                                if brand:
                                    self.program_manager.current_program.properties["screen"]["brand"] = brand
                            
                            if "model" not in self.program_manager.current_program.properties["screen"]:
                                model = device_info.get("model") or device_info.get("model_number") or device_info.get("device_model")
                                if model:
                                    self.program_manager.current_program.properties["screen"]["model"] = model
                    
                    self._save_and_refresh(self.program_manager.current_program)
            else:
                self.status_bar.set_connection_status(ConnectionStatus.ERROR)
                QMessageBox.warning(self, "Connection Failed", f"Failed to connect to controller at {ip}:{port}")
        except Exception as e:
            logger.error(f"Error connecting to controller: {e}")
            self.status_bar.set_connection_status(ConnectionStatus.ERROR)
            QMessageBox.critical(self, "Error", f"Error connecting to controller: {e}")
    
    def on_connect_controller(self):
        ip, ok = QInputDialog.getText(self, "Connect Controller", "Enter IP address:")
        if ok and ip:
            port, ok2 = QInputDialog.getInt(self, "Connect Controller", "Enter port:", 5000, 1, 65535)
            if ok2:
                controller_type, ok3 = QInputDialog.getItem(
                    self, "Connect Controller", "Controller type:",
                    ["huidu", "novastar"], 0, False
                )
                if ok3:
                    self.connect_to_controller(ip, port, controller_type)
    
    def on_disconnect_controller(self):
        if self.current_controller:
            self.current_controller.disconnect()
            self.current_controller = None
            self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
            logger.info("Disconnected from controller")
    
    def on_device_info(self):
        if not self.current_controller:
            QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
            return
        
        try:
            device_info = self.current_controller.get_device_info()
            if device_info:
                info_text = "Controller Information:\n\n"
                for key, value in device_info.items():
                    info_text += f"{key}: {value}\n"
                QMessageBox.information(self, "Controller Information", info_text)
            else:
                QMessageBox.warning(self, "No Information", "Could not retrieve controller information.")
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            QMessageBox.critical(self, "Error", f"Error getting device info: {e}")
    
    def on_upload(self):
        if not self.current_controller:
            QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
            return
        
        if not self.program_manager or not self.program_manager.current_program:
            QMessageBox.warning(self, "No Program", "No program selected. Please create or select a program first.")
            return
        
        try:
            program_data = self.program_manager.current_program.to_dict()
            self.status_bar.set_progress("Uploading program...")
            
            if self.current_controller.upload_program(program_data):
                self.status_bar.set_progress("Upload complete")
                QMessageBox.information(self, "Success", "Program uploaded successfully.")
                QTimer.singleShot(2000, self.status_bar.clear_progress)
            else:
                self.status_bar.set_progress("Upload failed")
                QMessageBox.warning(self, "Upload Failed", "Failed to upload program to controller.")
                QTimer.singleShot(2000, self.status_bar.clear_progress)
        except Exception as e:
            logger.error(f"Error uploading program: {e}")
            self.status_bar.set_progress("Upload error")
            QMessageBox.critical(self, "Error", f"Error uploading program: {e}")
            QTimer.singleShot(2000, self.status_bar.clear_progress)
    
    def on_download(self):
        if not self.current_controller:
            QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
            return
        
        try:
            reply = QMessageBox.question(
                self, "Download Programs",
                "This will import all programs from the controller and create a local database.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.status_bar.set_progress("Downloading from controller...")
                
                imported_data = self.sync_manager.import_from_controller(self.current_controller)
                
                if imported_data:
                    screen_resolution = imported_data.get("screen_resolution", {})
                    ctrl_width = screen_resolution.get("width")
                    ctrl_height = screen_resolution.get("height")
                    
                    for program_id, program_info in imported_data.get("programs", {}).items():
                        program_data = program_info.get("data", {})
                        if program_data:
                            program = Program()
                            program.from_dict(program_data)
                            
                            if "screen" not in program.properties:
                                program.properties["screen"] = {}
                            
                            if ctrl_width and ctrl_height:
                                program.properties["screen"]["width"] = ctrl_width
                                program.properties["screen"]["height"] = ctrl_height
                                logger.info(f"Set screen resolution for program {program.name}: {ctrl_width}x{ctrl_height}")
                            
                            device_info = self.current_controller.get_device_info()
                            if device_info:
                                if "brand" not in program.properties["screen"]:
                                    brand = device_info.get("brand") or device_info.get("manufacturer")
                                    if brand:
                                        program.properties["screen"]["brand"] = brand
                                if "model" not in program.properties["screen"]:
                                    model = device_info.get("model") or device_info.get("model_number")
                                    if model:
                                        program.properties["screen"]["model"] = model
                                if "controller_type" not in program.properties["screen"]:
                                    controller_type = device_info.get("controller_type") or device_info.get("type")
                                    if controller_type:
                                        program.properties["screen"]["controller_type"] = controller_type
                            
                            existing = self.program_manager.get_program_by_id(program.id)
                            if not existing:
                                self.program_manager.programs.append(program)
                    
                    self.status_bar.set_progress("Download complete")
                    QMessageBox.information(self, "Success", f"Downloaded {len(imported_data.get('programs', {}))} program(s) from controller.")
                    QTimer.singleShot(2000, self.status_bar.clear_progress)
                else:
                    self.status_bar.set_progress("Download failed")
                    QMessageBox.warning(self, "Download Failed", "Failed to download programs from controller.")
                    QTimer.singleShot(2000, self.status_bar.clear_progress)
        except Exception as e:
            logger.error(f"Error downloading programs: {e}")
            self.status_bar.set_progress("Download error")
            QMessageBox.critical(self, "Error", f"Error downloading programs: {e}")
            QTimer.singleShot(2000, self.status_bar.clear_progress)
    
    def _perform_startup_tasks(self):
        try:
            self._check_and_open_screen_dialog_if_needed()
            
            QTimer.singleShot(100, self._cleanup_orphaned_files)
            
            QTimer.singleShot(900, self.auto_discover_controllers)
            
            if not hasattr(self, '_auto_status_timer'):
                self._auto_status_timer = QTimer()
                self._auto_status_timer.timeout.connect(self._auto_check_connection_status)
                self._auto_status_timer.start(3000)
        except Exception as e:
            logger.error(f"Error in startup tasks: {e}", exc_info=True)
    
    def _check_and_open_screen_dialog_if_needed(self):
        try:
            if not self.program_manager:
                return
            
            if self._screen_dialog_opened:
                logger.info("Skipping screen dialog check - dialog already opened")
                return
            
            if hasattr(self, '_latest_file_loaded') and not self._latest_file_loaded:
                logger.info("Skipping screen dialog check - already handled by startup")
                return
            
            screen_names = ScreenManager.get_all_screen_names(self.program_manager.programs)
            
            if not screen_names:
                logger.info("No screens found, opening screen settings dialog")
                self._screen_dialog_opened = True
                self._create_new_screen_with_dialog()
        except Exception as e:
            logger.error(f"Error checking for screens: {e}", exc_info=True)
    
    def _cleanup_orphaned_files(self):
        try:
            if not self.program_manager:
                return
            
            current_screen_names = ScreenManager.get_all_screen_names(self.program_manager.programs)
            
            self.file_manager.cleanup_orphaned_files(current_screen_names)
        except Exception as e:
            logger.error(f"Error cleaning up orphaned files: {e}", exc_info=True)
    
    def on_time_power_brightness(self):
        try:
            from ui.time_power_brightness_dialog import TimePowerBrightnessDialog
            dialog = TimePowerBrightnessDialog(self, self.current_controller)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening time/power/brightness dialog: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error opening dialog: {str(e)}")
    
    def on_network_config(self):
        try:
            from ui.network_config_dialog import NetworkConfigDialog
            dialog = NetworkConfigDialog(self, self.current_controller)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening network config dialog: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error opening dialog: {str(e)}")
    
    def on_diagnostics(self):
        try:
            from ui.diagnostics_dialog import DiagnosticsDialog
            dialog = DiagnosticsDialog(self, self.current_controller)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening diagnostics dialog: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error opening dialog: {str(e)}")
    
    def on_import(self):
        try:
            if not self.current_controller:
                QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
                return
            
            reply = QMessageBox.question(
                self, "Import from Controller",
                "This will import all programs, media, schedules, network configurations, "
                "and settings from the controller and create a local database.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.on_download()
        except Exception as e:
            logger.error(f"Error importing from controller: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error importing: {str(e)}")
    
    def on_export(self):
        try:
            if not self.current_controller:
                QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
                return
            
            if not self.program_manager or not self.program_manager.current_program:
                QMessageBox.warning(self, "No Program", "No program selected. Please create or select a program first.")
                return
            
            reply = QMessageBox.question(
                self, "Export / Publish",
                "This will compare local database with controller and send only changes.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.on_upload()
        except Exception as e:
            logger.error(f"Error exporting/publishing: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error exporting: {str(e)}")
    
    def on_import_xml(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import XML (HDPlayer)", "",
                "XML Files (*.xml);;All Files (*.*)"
            )
            
            if file_path:
                program = self.file_manager.import_xml_file(file_path)
                if program:
                    QMessageBox.information(
                        self, "Import Successful",
                        f"Successfully imported program '{program.name}' from XML file."
                    )
                    self._update_ui_for_program(program)
                else:
                    QMessageBox.warning(
                        self, "Import Failed",
                        "Failed to import XML file. Please check the file format."
                    )
        except Exception as e:
            logger.error(f"Error importing XML: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error importing XML: {str(e)}")
    
    def on_export_xml(self):
        try:
            if not self.program_manager or not self.program_manager.current_program:
                QMessageBox.warning(
                    self, "No Program",
                    "No program selected. Please create or select a program first."
                )
                return
            
            program = self.program_manager.current_program
            default_name = f"{program.name}.xml"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export XML (HDPlayer)", default_name,
                "XML Files (*.xml);;All Files (*.*)"
            )
            
            if file_path:
                if not file_path.endswith('.xml'):
                    file_path += '.xml'
                
                success = self.file_manager.export_to_xml(program, file_path)
                if success:
                    QMessageBox.information(
                        self, "Export Successful",
                        f"Successfully exported program '{program.name}' to XML file:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(
                        self, "Export Failed",
                        "Failed to export program to XML file."
                    )
        except Exception as e:
            logger.error(f"Error exporting XML: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error exporting XML: {str(e)}")
