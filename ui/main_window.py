"""
Main application window
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QDialog,
    QMessageBox, QInputDialog, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence
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
from ui.program_list_panel import ProgramListPanel
from ui.media_player_panel import MediaPlayerPanel
from ui.properties_panel import PropertiesPanel
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


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLPlayer")
        
        # Core managers
        self.program_manager = ProgramManager()
        self.file_manager = FileManager(self.program_manager)
        self.sync_manager = SyncManager()
        
        # Service layer
        self.program_service = ProgramService(self.program_manager)
        self.file_service = FileService(self.program_manager, self.file_manager)
        self.controller_service = ControllerService()
        
        # UI state
        self.clipboard_program: Optional[Dict] = None
        self._latest_file_loaded = False
        
        self.init_ui()
        self.connect_signals()
        self._connect_event_bus()
        
        # Load latest files
        self._latest_file_loaded = self.file_service.load_latest_files()
        
        # Auto-discover controllers on startup
        QTimer.singleShot(1000, self.auto_discover_controllers)
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.setVisible(True)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        main_splitter = QSplitter(Qt.Vertical)
        central_layout.addWidget(main_splitter)
        
        content_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(content_splitter)
        
        self.program_list_panel = ProgramListPanel(self)
        self.program_list_panel.set_program_manager(self.program_manager)
        self.program_list_panel.setMinimumWidth(250)
        self.program_list_panel.setMaximumWidth(400)
        content_splitter.addWidget(self.program_list_panel)
        
        self.media_player_panel = MediaPlayerPanel(self)
        content_splitter.addWidget(self.media_player_panel)
        
        content_splitter.setStretchFactor(0, 0)
        content_splitter.setStretchFactor(1, 1)
        content_splitter.setSizes([250, 800])
        
        self.properties_panel = PropertiesPanel(self)
        main_splitter.addWidget(self.properties_panel)
        
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        main_splitter.setSizes([600, 200])
        
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
        
        # Status bar
        self.status_bar = StatusBarWidget(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
    
    def connect_signals(self):
        """Connect signals and slots"""
        self.menu_bar.exit_requested.connect(self.close)
        self.menu_bar.screen_settings_requested.connect(self.on_display_settings)
        self.menu_bar.language_changed.connect(self.on_language_changed)
        self.menu_bar.save_program_requested.connect(self.on_save_program)
        self.menu_bar.open_program_requested.connect(self.on_open_program)
        self.menu_bar.new_program_requested.connect(self.on_new_program_from_menu)
        
        # Controller menu signals
        self.menu_bar.device_info_requested.connect(self.on_device_info)
        self.menu_bar.upload_requested.connect(self.on_upload)
        self.menu_bar.download_requested.connect(self.on_download)
        self.menu_bar.discover_controllers_requested.connect(self.on_discover_controllers)
        self.menu_bar.dashboard_requested.connect(self.on_dashboard)
        self.menu_bar.connect_requested.connect(self.on_connect_controller)
        self.menu_bar.disconnect_requested.connect(self.on_disconnect_controller)
        
        # Connect program list panel signals
        self._connect_program_list_signals()
    
    def _connect_event_bus(self):
        """Connect to event bus for decoupled communication"""
        # Program events
        event_bus.program_created.connect(self._on_program_created)
        event_bus.program_updated.connect(self._on_program_updated)
        event_bus.program_selected.connect(self._on_program_selected_event)
        event_bus.program_saved.connect(self._on_program_saved)
        
        # UI refresh events - connect to actual refresh handler
        event_bus.ui_program_list_refresh.connect(self._on_program_list_refresh_needed)
        
        # File events
        event_bus.file_loaded.connect(self._on_file_loaded)
        event_bus.file_error.connect(self._on_file_error)
        
        # Controller events
        event_bus.controller_connected.connect(self._on_controller_connected)
        event_bus.controller_disconnected.connect(self._on_controller_disconnected)
        event_bus.controller_error.connect(self._on_controller_error)
    
    def _on_program_created(self, program: Program):
        """Handle program created event"""
        if hasattr(self, 'program_list_panel'):
            self.program_list_panel.refresh_programs()
    
    def _on_program_updated(self, program: Program):
        """Handle program updated event"""
        if program == self.program_manager.current_program:
            self._update_ui_for_program(program)
    
    def _on_program_selected_event(self, program_id: str):
        """Handle program selected event from event bus"""
        program = self.program_manager.get_program_by_id(program_id)
        if program:
            self._update_ui_for_program(program)
    
    def _on_program_saved(self, program: Program, file_path: str):
        """Handle program saved event"""
        logger.debug(f"Program saved: {program.name} to {file_path}")
    
    def _on_file_loaded(self, file_path: str):
        """Handle file loaded event"""
        if hasattr(self, 'program_list_panel'):
            self.program_list_panel.refresh_programs()
    
    def _on_file_error(self, file_path: str, error: str):
        """Handle file error event"""
        QMessageBox.warning(self, "File Error", f"Error with file {file_path}:\n{error}")
    
    def _on_controller_connected(self, controller: BaseController):
        """Handle controller connected event"""
        self.current_controller = controller
        if hasattr(self, 'status_bar'):
            self.status_bar.set_connection_status(controller.get_connection_status())
    
    def _on_controller_disconnected(self):
        """Handle controller disconnected event"""
        self.current_controller = None
        if hasattr(self, 'status_bar'):
            from controllers.base_controller import ConnectionStatus
            self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
    
    def _on_controller_error(self, error: str):
        """Handle controller error event"""
        QMessageBox.warning(self, "Controller Error", error)
    
    def _on_program_list_refresh_needed(self):
        """Handle program list refresh request with throttling"""
        if hasattr(self, 'program_list_panel'):
            # Use throttled function call to avoid excessive updates
            self._throttled_refresh()
    
    def _do_program_list_refresh(self):
        """Actually perform the program list refresh"""
        if hasattr(self, 'program_list_panel'):
            self.program_list_panel.refresh_programs()
    
    def _throttled_refresh(self):
        """Throttled refresh using QTimer"""
        if not hasattr(self, '_refresh_timer'):
            self._refresh_timer = QTimer()
            self._refresh_timer.setSingleShot(True)
            self._refresh_timer.timeout.connect(self._do_program_list_refresh)
        
        # Stop existing timer and restart with delay
        self._refresh_timer.stop()
        self._refresh_timer.start(100)  # 100ms throttle
    
    def _connect_program_list_signals(self):
        """Connect program list panel signals"""
        if not hasattr(self, 'program_list_panel'):
            return
        
        self.program_list_panel.program_selected.connect(self.on_program_selected)
        self.program_list_panel.screen_selected.connect(self.on_screen_selected)
        self.program_list_panel.new_program_requested.connect(self.on_new_program)
        self.program_list_panel.delete_program_requested.connect(self.on_delete_program)
        self.program_list_panel.program_renamed.connect(self.on_program_renamed)
        self.program_list_panel.program_duplicated.connect(self.on_program_duplicated)
        self.program_list_panel.program_moved.connect(self.on_program_moved)
        self.program_list_panel.program_activated.connect(self.on_program_activated)
        self.program_list_panel.program_checked.connect(self.on_program_checked)
        
        self.program_list_panel.screen_renamed.connect(self.on_screen_renamed)
        self.program_list_panel.screen_deleted.connect(self.on_screen_deleted)
        self.program_list_panel.new_screen_requested.connect(self.on_new_screen)
        self.program_list_panel.add_program_requested.connect(self.on_add_program)
        self.program_list_panel.screen_insert_requested.connect(self.on_screen_insert)
        self.program_list_panel.screen_download_requested.connect(self.on_screen_download)
        self.program_list_panel.screen_close_requested.connect(self.on_screen_close)
        self.program_list_panel.screen_paste_requested.connect(self.on_screen_paste)
        
        self.program_list_panel.program_copy_requested.connect(self.on_program_copy)
        self.program_list_panel.program_paste_requested.connect(self.on_program_paste)
        self.program_list_panel.program_add_content_requested.connect(self.on_program_add_content)
        
        self.visible_content_toolbar.content_type_selected.connect(self.on_content_type_selected)
        self.playback_control_toolbar.action_triggered.connect(self.on_playback_action)
        self.control_toolbar.action_triggered.connect(self.on_control_action)
    
    def on_language_changed(self, language: str):
        """Handle language change"""
        set_language(language)
        if hasattr(self, 'menu_bar'):
            self.menu_bar.refresh_texts()
    
    def on_content_type_selected(self, content_type: str):
        """Handle content type selection from toolbar"""
        try:
            if self.program_manager and self.program_manager.current_program:
                from datetime import datetime
                element = {
                    "type": content_type,
                    "id": f"element_{datetime.now().timestamp()}",
                    "properties": {}
                }
                self.program_manager.current_program.elements.append(element)
                self.program_manager.current_program.modified = datetime.now().isoformat()
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.set_element(element, self.program_manager.current_program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error adding content: {e}")
    
    def on_playback_action(self, action_id: str):
        """Handle playback toolbar actions"""
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info(f"Playback action: {action_id}")
    
    def on_control_action(self, action_id: str):
        """Handle control toolbar actions"""
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info(f"Control action: {action_id}")
    
    def _update_ui_for_program(self, program: Program):
        """Update UI components for a program"""
        if hasattr(self, 'media_player_panel'):
            self.media_player_panel.set_program(program)
        if hasattr(self, 'properties_panel'):
            self.properties_panel.set_program(program)
        if hasattr(self, 'program_list_panel'):
            self.program_list_panel.refresh_programs()
        if hasattr(self, 'status_bar') and program:
            self.status_bar.set_program_name(program.name)
    
    def _save_and_refresh(self, program: Program, file_path: Optional[str] = None):
        """
        Save program to .soo file and refresh UI.
        Uses FileService for business logic and event bus for UI updates.
        """
        return self.file_service.save_file(program, file_path)
    
    def on_program_selected(self, program_id: str):
        """Handle program selection from program list panel"""
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
        """Handle screen selection from program list panel"""
        try:
            if not self.program_manager:
                return
            screen_programs = ScreenManager.get_programs_for_screen(
                self.program_manager.programs, screen_name
            )
            if hasattr(self, 'properties_panel'):
                self.properties_panel.set_screen(screen_name, screen_programs, self.program_manager)
        except Exception as e:
            logger.error(f"Error selecting screen: {e}")
    
    def on_new_program_from_menu(self):
        """Handle new program request from menu - opens screen settings dialog"""
        self._create_new_screen_with_dialog()
    
    def on_new_program(self):
        """Handle new program request from program list panel"""
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
            
            # Set screen properties for the new program
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            
            program.properties["screen"]["screen_name"] = screen_name
            
            # Copy screen dimensions from existing programs on the same screen
            # This ensures each screen maintains its own width/height independently
            screen_programs = ScreenManager.get_programs_for_screen(
                self.program_manager.programs, screen_name
            )
            
            # Find width/height from existing programs on this screen
            for existing_program in screen_programs:
                if existing_program.id != program.id:
                    existing_screen = existing_program.properties.get("screen", {})
                    if "width" in existing_screen and "height" in existing_screen:
                        program.properties["screen"]["width"] = existing_screen["width"]
                        program.properties["screen"]["height"] = existing_screen["height"]
                        # Also copy other screen properties
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
            self._update_ui_for_program(program)  # This will refresh program list panel
            if hasattr(self, 'auto_save_manager'):
                self.auto_save_manager.save_current_program()
        except Exception as e:
            logger.error(f"Error creating new program: {e}")
    
    def _create_new_screen_with_dialog(self):
        """Create a new screen by opening screen settings dialog"""
        try:
            from ui.screen_settings_dialog import ScreenSettingsDialog
            from pathlib import Path
            from utils.logger import get_logger
            import time
            logger = get_logger(__name__)
            
            dialog = ScreenSettingsDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                if self.program_manager:
                    w, h = dialog.selected_size()
                    rotate = dialog.selected_rotate()
                    series = dialog.selected_series()
                    model = dialog.selected_model()
                    ctrl_id = dialog.selected_controller_id()
                    
                    program = self.program_manager.create_program("New Program")
                    
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
                    
                    existing_screen_names = set()
                    for p in self.program_manager.programs:
                        if p.id != program.id:
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
                    
                    program.properties["screen"]["screen_name"] = screen_name
                    program.name = ScreenManager.generate_unique_program_name(self.program_manager.programs, screen_name)
                    
                    self.program_manager.current_program = program
                    self._save_and_refresh(program)
                    
                    logger.info(f"Created new screen: {screen_name}, program: {program.name}, width: {w}, height: {h}, rotate: {rotate}, programs count: {len(self.program_manager.programs)}")
                    
                    # Update UI - this will refresh program list panel
                    self._update_ui_for_program(program)
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error creating new screen: {e}", exc_info=True)
    
    def on_delete_program(self, program_id: str):
        """Handle delete program request"""
        try:
            if self.program_manager:
                program = self.program_manager.get_program_by_id(program_id)
            if program:
                self.program_manager.delete_program(program)
                if hasattr(self, 'program_list_panel'):
                    self.program_list_panel.refresh_programs()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error deleting program: {e}")
    
    def on_program_renamed(self, program_id: str, new_name: str):
        """Handle program rename"""
        from datetime import datetime
        try:
            if self.program_manager:
                program = self.program_manager.get_program_by_id(program_id)
            if program:
                old_name = program.name
                program.name = new_name
                program.modified = datetime.now().isoformat()
                self._save_and_refresh(program)
                # Update UI - this will refresh program list panel
                self._update_ui_for_program(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error renaming program: {e}")
    
    def on_program_duplicated(self, program_id: str):
        """Handle program duplication"""
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
                    if hasattr(self, 'media_player_panel'):
                        self.media_player_panel.set_program(new_program)
                    if hasattr(self, 'properties_panel'):
                        self.properties_panel.set_program(new_program)
                    if hasattr(self, 'program_list_panel'):
                        self.program_list_panel.refresh_programs()
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error duplicating program: {e}")
    
    def on_program_moved(self, program_id: str, direction: int):
        """Handle program move (up/down)"""
        try:
            if self.program_manager:
                programs = self.program_manager.programs
                current_index = next((i for i, p in enumerate(programs) if p.id == program_id), None)
                if current_index is not None:
                    new_index = current_index + direction
                    if 0 <= new_index < len(programs):
                        programs[current_index], programs[new_index] = programs[new_index], programs[current_index]
                        if hasattr(self, 'program_list_panel'):
                            self.program_list_panel.refresh_programs()
                        if hasattr(self, 'auto_save_manager'):
                            self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error moving program: {e}")
    
    def on_program_activated(self, program_id: str, enabled: bool):
        """Handle program activation/deactivation"""
        from datetime import datetime
        try:
            if self.program_manager:
                program = self.program_manager.get_program_by_id(program_id)
                if program:
                    if "activation" not in program.properties:
                        program.properties["activation"] = {}
                    program.properties["activation"]["enabled"] = enabled
                    program.modified = datetime.now().isoformat()
                    if hasattr(self, 'program_list_panel'):
                        self.program_list_panel.refresh_programs()
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error activating/deactivating program: {e}")
    
    def on_program_checked(self, program_id: str, checked: bool):
        """Handle program checkbox toggle"""
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
        """Handle display settings menu action"""
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
                    
                    # Save screen dimensions (controller screen, not PC canvas)
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
                    
                    # Update all programs on the same screen with the new dimensions
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
        """Load a .soo file (delegates to FileManager)"""
        result = self.file_manager.load_soo_file(file_path, clear_existing)
        if result:
            # Refresh program list panel to show loaded programs
            if hasattr(self, 'program_list_panel'):
                self.program_list_panel.refresh_programs()
            if self.program_manager.current_program:
                self._update_ui_for_program(self.program_manager.current_program)
        return result
    
    def on_open_program(self, file_path: str = ""):
        """Handle open program request from menu"""
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
        """Handle save program request from menu"""
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
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error saving program: {e}")
    
    def on_screen_renamed(self, screen_name: str, new_name: str):
        """Handle screen rename from context menu"""
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
        """Handle screen delete from context menu"""
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
                    
                    if hasattr(self, 'program_list_panel'):
                        self.program_list_panel.refresh_programs()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error deleting screen: {e}")
    
    def on_new_screen(self):
        """Handle new screen from context menu - opens screen settings dialog"""
        self._create_new_screen_with_dialog()
    
    def on_add_program(self, screen_name: str):
        """Handle add program request for a screen"""
        try:
            if not self.program_manager:
                return
            
            program_name = ScreenManager.generate_unique_program_name(
                self.program_manager.programs, screen_name
            )
            program = self.program_manager.create_program(program_name)
            
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            
            program.properties["screen"]["screen_name"] = screen_name
            
            # Copy screen dimensions from existing programs on the same screen
            # This ensures each screen maintains its own width/height independently
            screen_programs = ScreenManager.get_programs_for_screen(
                self.program_manager.programs, screen_name
            )
            
            for existing_program in screen_programs:
                if existing_program.id != program.id:
                    existing_screen = existing_program.properties.get("screen", {})
                    if "width" in existing_screen and "height" in existing_screen:
                        program.properties["screen"]["width"] = existing_screen["width"]
                        program.properties["screen"]["height"] = existing_screen["height"]
                        # Also copy other screen properties
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
        """Handle screen insert request from context menu"""
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
                program.properties["screen"]["screen_name"] = screen_name
                
                self.program_manager.programs.append(program)
                self.program_manager.current_program = program
                self._save_and_refresh(program)
                if hasattr(self, 'media_player_panel'):
                    self.media_player_panel.set_program(program)
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.set_program(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error inserting program: {e}")
    
    def on_screen_download(self, screen_name: str):
        """Handle screen download request from context menu"""
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
        """Handle screen close request from context menu"""
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
                    
                    if hasattr(self, 'program_list_panel'):
                        self.program_list_panel.refresh_programs()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error closing screen: {e}")
    
    def on_screen_paste(self, screen_name: str):
        """Handle screen paste request from context menu"""
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
                    program.properties["screen"]["screen_name"] = screen_name
                
                self.program_manager.programs.append(program)
                self.program_manager.current_program = program
                if hasattr(self, 'media_player_panel'):
                    self.media_player_panel.set_program(program)
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.set_program(program)
                self._save_and_refresh(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error pasting program: {e}")
    
    def on_program_copy(self, program_id: str):
        """Handle program copy request"""
        try:
            if self.program_manager:
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
        """Handle program paste request"""
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
                    if hasattr(self, 'properties_panel'):
                        self.properties_panel.set_program(target_program)
                    if hasattr(self, 'auto_save_manager'):
                        self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error pasting elements: {e}")
    
    def on_program_add_content(self, program_id: str, content_type: str):
        """Handle program add content request from context menu"""
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

    def open_screen_settings_on_startup(self):
        """Show the Screen Parameters Setting dialog by default when window initializes."""
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
                    
                    # Save screen dimensions (controller screen, not PC canvas)
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
                    
                    if hasattr(self, 'media_player_panel'):
                        self.media_player_panel.set_program(program)
                    if hasattr(self, 'properties_panel'):
                        self.properties_panel.set_program(program)
                self._save_and_refresh(program)
                if hasattr(self, 'auto_save_manager'):
                    self.auto_save_manager.save_current_program()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error opening screen settings: {e}")
    
    def closeEvent(self, event):
        """Handle window close event - autosave all screens"""
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
    
    # Controller management methods
    def auto_discover_controllers(self):
        """Auto-discover controllers on startup"""
        try:
            from core.controller_discovery import ControllerDiscovery
            discovery = ControllerDiscovery(self)
            discovery.discovery_finished.connect(lambda: self.on_discovery_finished(discovery))
            discovery.start_scan()
        except Exception as e:
            logger.error(f"Error in auto-discovery: {e}")
    
    def on_discovery_finished(self, discovery):
        """Handle discovery finished"""
        controllers = discovery.get_discovered_controllers()
        if controllers:
            logger.info(f"Auto-discovered {len(controllers)} controller(s)")
            # Auto-connect to first controller if available
            if len(controllers) == 1:
                ctrl = controllers[0]
                self.connect_to_controller(ctrl.ip, ctrl.port, ctrl.controller_type)
    
    def on_discover_controllers(self):
        """Handle discover controllers menu action"""
        try:
            from ui.dashboard_dialog import DashboardDialog
            dialog = DashboardDialog(self)
            dialog.controller_selected.connect(self.on_controller_selected_from_dashboard)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Error in discover controllers: {e}")
            QMessageBox.warning(self, "Error", f"Error discovering controllers: {e}")
    
    def on_controller_selected_from_dashboard(self, ip: str, port: int, controller_type: str):
        """Handle controller selection from dashboard"""
        self.connect_to_controller(ip, port, controller_type)
    
    def on_dashboard(self):
        """Handle dashboard menu action"""
        self.on_discover_controllers()
    
    def connect_to_controller(self, ip: str, port: int, controller_type: str):
        """Connect to a controller"""
        try:
            # Disconnect existing controller
            if self.current_controller:
                self.current_controller.disconnect()
            
            # Create new controller
            if controller_type == "novastar":
                self.current_controller = NovaStarController(ip, port)
            elif controller_type == "huidu":
                self.current_controller = HuiduController(ip, port)
            else:
                QMessageBox.warning(self, "Error", f"Unknown controller type: {controller_type}")
                return
            
            # Connect
            self.status_bar.set_connection_status(ConnectionStatus.CONNECTING)
            if self.current_controller.connect():
                device_info = self.current_controller.get_device_info()
                device_name = device_info.get("name", "") if device_info else ""
                self.status_bar.set_connection_status(ConnectionStatus.CONNECTED, device_name)
                logger.info(f"Connected to {controller_type} controller at {ip}:{port}")
                
                # Update current program with controller info AND screen resolution
                if self.program_manager.current_program:
                    if "screen" not in self.program_manager.current_program.properties:
                        self.program_manager.current_program.properties["screen"] = {}
                    
                    # Set controller ID and type
                    self.program_manager.current_program.properties["screen"]["controller_id"] = self.current_controller.get_controller_id()
                    self.program_manager.current_program.properties["screen"]["controller_type"] = controller_type
                    
                    # CRITICAL: Read actual controller screen resolution from device_info
                    if device_info:
                        # Try to get resolution from various possible fields
                        resolution = (
                            device_info.get("display_resolution") or
                            device_info.get("resolution") or
                            device_info.get("screen_resolution") or
                            device_info.get("screen_size")
                        )
                        
                        if resolution:
                            # Parse resolution string like "1920x1080" or dict with width/height
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
                                ctrl_width = resolution.get("width") or resolution.get("w")
                                ctrl_height = resolution.get("height") or resolution.get("h")
                                if ctrl_width and ctrl_height:
                                    self.program_manager.current_program.properties["screen"]["width"] = int(ctrl_width)
                                    self.program_manager.current_program.properties["screen"]["height"] = int(ctrl_height)
                                    logger.info(f"Set controller screen resolution from device_info dict: {ctrl_width}x{ctrl_height}")
                        
                        # Also try direct width/height fields
                        if "width" not in self.program_manager.current_program.properties["screen"]:
                            ctrl_width = device_info.get("width") or device_info.get("screen_width")
                            ctrl_height = device_info.get("height") or device_info.get("screen_height")
                            if ctrl_width and ctrl_height:
                                self.program_manager.current_program.properties["screen"]["width"] = int(ctrl_width)
                                self.program_manager.current_program.properties["screen"]["height"] = int(ctrl_height)
                                logger.info(f"Set controller screen resolution from direct fields: {ctrl_width}x{ctrl_height}")
                        
                        # Update brand and model if available
                        if "brand" not in self.program_manager.current_program.properties["screen"]:
                            brand = device_info.get("brand") or device_info.get("manufacturer")
                            if brand:
                                self.program_manager.current_program.properties["screen"]["brand"] = brand
                        
                        if "model" not in self.program_manager.current_program.properties["screen"]:
                            model = device_info.get("model") or device_info.get("model_number") or device_info.get("device_model")
                            if model:
                                self.program_manager.current_program.properties["screen"]["model"] = model
                    
                    # Save the updated screen properties
                    self._save_and_refresh(self.program_manager.current_program)
            else:
                self.status_bar.set_connection_status(ConnectionStatus.ERROR)
                QMessageBox.warning(self, "Connection Failed", f"Failed to connect to controller at {ip}:{port}")
        except Exception as e:
            logger.error(f"Error connecting to controller: {e}")
            self.status_bar.set_connection_status(ConnectionStatus.ERROR)
            QMessageBox.critical(self, "Error", f"Error connecting to controller: {e}")
    
    def on_connect_controller(self):
        """Handle connect controller menu action"""
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
        """Handle disconnect controller menu action"""
        if self.current_controller:
            self.current_controller.disconnect()
            self.current_controller = None
            self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
            logger.info("Disconnected from controller")
    
    def on_device_info(self):
        """Handle device info menu action"""
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
        """Handle upload menu action"""
        if not self.current_controller:
            QMessageBox.warning(self, "No Controller", "No controller connected. Please connect to a controller first.")
            return
        
        if not self.program_manager.current_program:
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
        """Handle download menu action"""
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
                
                # Use sync manager to import
                imported_data = self.sync_manager.import_from_controller(self.current_controller)
                
                if imported_data:
                    # CRITICAL: Get controller screen resolution from imported data
                    screen_resolution = imported_data.get("screen_resolution", {})
                    ctrl_width = screen_resolution.get("width")
                    ctrl_height = screen_resolution.get("height")
                    
                    # Load programs into program manager
                    for program_id, program_info in imported_data.get("programs", {}).items():
                        program_data = program_info.get("data", {})
                        if program_data:
                            program = Program()
                            program.from_dict(program_data)
                            
                            # CRITICAL: Set controller screen resolution in screen_properties
                            # This is the actual LED display resolution, NOT PC canvas size
                            if "screen" not in program.properties:
                                program.properties["screen"] = {}
                            
                            # Set screen resolution from imported data
                            if ctrl_width and ctrl_height:
                                program.properties["screen"]["width"] = ctrl_width
                                program.properties["screen"]["height"] = ctrl_height
                                logger.info(f"Set screen resolution for program {program.name}: {ctrl_width}x{ctrl_height}")
                            
                            # Set controller info if available
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
                            
                            # Check if program already exists
                            existing = self.program_manager.get_program_by_id(program.id)
                            if not existing:
                                self.program_manager.programs.append(program)
                    
                    self.program_list_panel.refresh_programs()
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
