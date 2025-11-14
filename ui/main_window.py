"""
Main application window
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QStatusBar, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeyEvent

from ui.menu_bar import MenuBar
from ui.toolbar import Toolbar
from ui.program_list_panel import ProgramListPanel
from ui.canvas import Canvas
from ui.properties_panel import PropertiesPanel
from ui.status_bar import StatusBarWidget
from core.program_manager import ProgramManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.program_manager = ProgramManager()
        # Enable keyboard focus for shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # Initialize undo/redo manager
        from core.undo_redo import UndoRedoManager
        self.undo_manager = UndoRedoManager()
        # Clipboard for copy/paste
        self.clipboard_element: Optional[Dict] = None
        # Controller connection
        self.current_controller = None
        # Preview window
        self.preview_window = None
        # Dashboard window
        self.dashboard_window = None
        # Auto-save manager
        from core.auto_save import AutoSaveManager
        from config.settings import settings
        self.auto_save_manager = AutoSaveManager(self.program_manager)
        if settings.get("auto_save", True):
            self.auto_save_manager.start()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("SLPlayer")
        self.setMinimumSize(1200, 800)
        
        # Set window icon (ensures taskbar icon is correct)
        # Use absolute path for better compatibility
        icon_path = Path(__file__).parent.parent / "resources" / "app.ico"
        if icon_path.exists():
            icon = QIcon(str(icon_path.absolute()))
            self.setWindowIcon(icon)
        else:
            # Try alternative names
            for alt_name in ["icon.ico", "app_icon.ico", "SLPlayer.ico", "icon.png"]:
                alt_path = Path(__file__).parent.parent / "resources" / alt_name
                if alt_path.exists():
                    icon = QIcon(str(alt_path.absolute()))
                    self.setWindowIcon(icon)
                    break
        
        # Set titlebar/window background color to distinguish it
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Create toolbar with scrollable container to show ALL items
        from PyQt6.QtWidgets import QScrollArea
        self.toolbar = Toolbar(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.toolbar)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(32)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #D6D6D6;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: #E0E0E0;
            }
            QScrollBar::handle:horizontal {
                background: #BDBDBD;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #9E9E9E;
            }
        """)
        main_layout.addWidget(scroll_area)
        
        # Create horizontal splitter for Program List Panel and Canvas (left-right)
        main_vertical_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left sidebar - Program list panel
        self.program_list_panel = ProgramListPanel(self)
        # Set minimum width (allows splitter to resize) and add border on the right side
        self.program_list_panel.setMinimumWidth(180)  # Minimum width
        self.program_list_panel.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-right: 2px solid #BDBDBD;
            }
        """)
        main_vertical_splitter.addWidget(self.program_list_panel)
        
        # Right side - Canvas
        self.canvas = Canvas(self)
        self.canvas.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border: 1px solid #000000;
            }
        """)
        main_vertical_splitter.addWidget(self.canvas)
        
        # Set horizontal splitter sizes (left sidebar: 220px, right: rest)
        main_vertical_splitter.setSizes([220, 1200])
        # Allow the splitter to resize both panels
        main_vertical_splitter.setChildrenCollapsible(False)
        main_vertical_splitter.setCollapsible(0, False)
        main_vertical_splitter.setCollapsible(1, False)
        # Set splitter handle style
        main_vertical_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
                width: 2px;
                border-left: 1px solid #777777;
                border-right: 1px solid #777777;
                border-top: none;
                border-bottom: none;
            }
            QSplitter::handle:horizontal {
                background-color: #E0E0E0;
                width: 2px;
                border-left: 1px solid #777777;
                border-right: 1px solid #777777;
                border-top: none;
                border-bottom: none;
            }
        """)
        main_layout.addWidget(main_vertical_splitter)
        
        # Create vertical splitter for main content area and properties panel (top-bottom)
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Add the horizontal splitter (Program List + Canvas) to vertical splitter (top part)
        main_splitter.addWidget(main_vertical_splitter)
        
        # Properties panel (full-width, same as toolbar) - bottom part of vertical splitter
        self.properties_panel = PropertiesPanel(self)
        self.properties_panel.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
            }
        """)
        main_splitter.addWidget(self.properties_panel)
        
        # Set vertical splitter sizes (main content: most space, properties: fixed height)
        main_splitter.setSizes([800, 250])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        # Set vertical splitter handle style
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
                height: 1px;
            }
            QSplitter::handle:vertical {
                background-color: #E0E0E0;
                height: 1px;
            }
        """)
        main_layout.addWidget(main_splitter)
        
        # Create status bar
        self.status_bar = StatusBarWidget(self)
        self.setStatusBar(self.status_bar)
        
        # Set program manager for components
        self.program_list_panel.set_program_manager(self.program_manager)
        
        # Apply pixel-perfect styling after all widgets are created
        from ui.styles import Styles
        self.setStyleSheet(Styles.MAIN_WINDOW)
        self.menu_bar.setStyleSheet(Styles.MENUBAR)
        self.program_list_panel.tree.setStyleSheet(Styles.TREE_WIDGET)
        self.status_bar.setStyleSheet(Styles.STATUS_BAR)
        
        # Connect signals
        self.connect_signals()
    
    def connect_signals(self):
        """Connect UI signals"""
        # Program list panel signals
        self.program_list_panel.program_selected.connect(self.on_program_selected)
        self.program_list_panel.new_program_requested.connect(self.on_new_program)
        self.menu_bar.new_from_template_requested.connect(self.on_new_from_template)
        self.program_list_panel.delete_program_requested.connect(self.on_delete_program)
        self.program_list_panel.program_renamed.connect(self.on_program_renamed)
        self.program_list_panel.program_duplicated.connect(self.on_program_duplicated)
        self.program_list_panel.program_moved.connect(self.on_program_moved)
        self.program_list_panel.program_activated.connect(self.on_program_activated)
        
        # Toolbar signals
        self.toolbar.content_type_selected.connect(self.on_content_type_selected)
        
        # Canvas signals
        self.canvas.canvas_widget.element_selected.connect(self.on_element_selected)
        self.canvas.canvas_widget.element_moved.connect(self.on_element_moved)
        self.canvas.canvas_widget.element_changed.connect(self.on_element_changed)
        
        # Menu bar signals
        self.menu_bar.new_program_requested.connect(self.on_new_program)
        self.menu_bar.new_from_template_requested.connect(self.on_new_from_template)
        self.menu_bar.open_program_requested.connect(self.on_open_program)
        self.menu_bar.save_program_requested.connect(self.on_save_program)
        self.menu_bar.connect_requested.connect(self.on_connect_controller)
        self.menu_bar.disconnect_requested.connect(self.on_disconnect_controller)
        self.menu_bar.discover_controllers_requested.connect(self.on_discover_controllers)
        self.menu_bar.upload_requested.connect(self.on_upload_program)
        self.menu_bar.download_requested.connect(self.on_download_program)
        self.menu_bar.preview_requested.connect(self.on_preview)
        self.menu_bar.dashboard_requested.connect(self.on_dashboard)
        
    
    def on_program_selected(self, program_id: str):
        """Handle program selection"""
        program = self.program_manager.get_program_by_id(program_id)
        if program:
            self.program_manager.current_program = program
            self.canvas.set_program(program)
            self.properties_panel.set_program(program)
            self.status_bar.set_program_name(program.name)
    
    def on_new_program(self):
        """Handle new program creation"""
        program = self.program_manager.create_program()
        self.program_list_panel.refresh_programs()
        self.canvas.set_program(program)
        self.properties_panel.set_program(program)
        self.status_bar.set_program_name(program.name)
        # Clear undo history for new program
        self.undo_manager.clear()
    
    def on_new_from_template(self, template_name: str):
        """Handle new program from template"""
        from core.templates import TemplateManager
        
        program = TemplateManager.create_from_template(template_name)
        self.program_manager.add_program(program)
        self.program_manager.current_program = program
        self.program_list_panel.refresh_programs()
        self.canvas.set_program(program)
        self.properties_panel.set_program(program)
        self.status_bar.set_program_name(program.name)
        # Clear undo history for new program
        self.undo_manager.clear()
    
    def on_delete_program(self, program_id: str):
        """Handle program deletion"""
        program = self.program_manager.get_program_by_id(program_id)
        if program:
            self.program_manager.delete_program(program)
            self.program_list_panel.refresh_programs()
            if self.program_manager.current_program:
                self.canvas.set_program(self.program_manager.current_program)
                self.properties_panel.set_program(self.program_manager.current_program)
    
    def on_open_program(self, file_path: str = None):
        """Handle open program"""
        from PyQt6.QtWidgets import QFileDialog
        
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Program", "", 
                "SLPlayer Files (*.slp);;JSON Files (*.json);;All Files (*)"
            )
        
        if file_path:
            program = self.program_manager.load_program(file_path)
            if program:
                self.program_list_panel.refresh_programs()
                self.canvas.set_program(program)
                self.properties_panel.set_program(program)
                self.status_bar.set_program_name(program.name)
                self.program_manager.current_program = program
                # Add to recent files
                self.menu_bar.add_to_recent_files(file_path)
    
    def on_save_program(self, file_path: str = None):
        """Handle save program"""
        from PyQt6.QtWidgets import QFileDialog
        
        if not self.program_manager.current_program:
            return
        
        program = self.program_manager.current_program
        
        if not file_path:
            # Suggest filename based on program name
            suggested_name = program.name.replace(" ", "_") + ".slp"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Program", suggested_name,
                "SLPlayer Files (*.slp);;JSON Files (*.json);;All Files (*)"
            )
        
        if file_path:
            success = self.program_manager.save_program(program, file_path)
            if success:
                self.status_bar.set_program_name(program.name)
                # Update program list to reflect saved state
                self.program_list_panel.refresh_programs()
                # Add to recent files
                self.menu_bar.add_to_recent_files(file_path)
    
    def on_content_type_selected(self, content_type: str):
        """Handle content type selection from toolbar"""
        from config.constants import ContentType
        from core.content_element import create_element
        
        # Get current program
        if not self.program_manager.current_program:
            # Create a new program if none exists
            self.on_new_program()
        
        program = self.program_manager.current_program
        if not program:
            return
        
        # Convert string to ContentType enum
        try:
            content_type_enum = ContentType(content_type)
        except ValueError:
            print(f"Unknown content type: {content_type}")
            return
        
        # Get screen center position for new element (in screen resolution coordinates)
        screen_width = program.width
        screen_height = program.height
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Create new element (positioned at screen center)
        element = create_element(content_type_enum, center_x, center_y)
        element_dict = element.to_dict()
        
        # Add element to program using undo/redo
        from core.undo_redo import ElementCommand
        command = ElementCommand(
            program, element_dict["id"], "add",
            old_data=None,
            new_data=element_dict
        )
        self.undo_manager.execute_command(command)
        
        # Select new element
        self.canvas.canvas_widget.set_selected_element(element_dict["id"])
        self.canvas.canvas_widget.update()
        self.on_element_selected(element_dict["id"])
    
    def on_element_selected(self, element_id: str):
        """Handle element selection from canvas"""
        if element_id and self.program_manager.current_program:
            # Find element and update properties panel
            for element_data in self.program_manager.current_program.elements:
                if element_data.get("id") == element_id:
                    # Update properties panel with element data
                    self.properties_panel.set_selected_element(element_data)
                    break
        else:
            # Clear selection
            self.properties_panel.set_selected_element(None)
    
    def on_element_moved(self, element_id: str, x: int, y: int):
        """Handle element movement"""
        if self.program_manager.current_program:
            program = self.program_manager.current_program
            # Find element and create move command
            for elem in program.elements:
                if elem.get("id") == element_id:
                    # Note: This is called during drag, so we'll batch undo commands
                    # For now, just update the program
                    program.modified = datetime.now().isoformat()
                    break
    
    def on_element_changed(self, element_id: str):
        """Handle element property changes (e.g., resize)"""
        if element_id and self.program_manager.current_program:
            # Find element and update properties panel
            for element_data in self.program_manager.current_program.elements:
                if element_data.get("id") == element_id:
                    # Update properties panel with latest element data
                    self.properties_panel.set_selected_element(element_data)
                    break
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        from PyQt6.QtGui import QKeySequence
        
        # Delete key - delete selected element
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_element()
        # Ctrl+Z - Undo
        elif event.matches(QKeySequence.StandardKey.Undo):
            self.undo()
        # Ctrl+Y or Ctrl+Shift+Z - Redo
        elif event.matches(QKeySequence.StandardKey.Redo):
            self.redo()
        # Ctrl+C - Copy
        elif event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selected_element()
        # Ctrl+V - Paste
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste_element()
        # Ctrl+D - Duplicate
        elif event.matches(QKeySequence("Ctrl+D")):
            self.duplicate_selected_element()
        # Arrow keys - Move element
        elif event.key() == Qt.Key.Key_Left:
            self.move_selected_element(-10, 0)
        elif event.key() == Qt.Key.Key_Right:
            self.move_selected_element(10, 0)
        elif event.key() == Qt.Key.Key_Up:
            self.move_selected_element(0, -10)
        elif event.key() == Qt.Key.Key_Down:
            self.move_selected_element(0, 10)
        else:
            super().keyPressEvent(event)
    
    def delete_selected_element(self):
        """Delete the currently selected element"""
        if not self.program_manager.current_program:
            return
        
        selected_id = self.canvas.canvas_widget.selected_element_id
        if not selected_id:
            return
        
        # Find element data
        program = self.program_manager.current_program
        element_data = None
        for elem in program.elements:
            if elem.get("id") == selected_id:
                element_data = elem.copy()
                break
        
        if element_data:
            # Create undo command
            from core.undo_redo import ElementCommand
            command = ElementCommand(
                program, selected_id, "delete",
                old_data=element_data,
                new_data=None
            )
            self.undo_manager.execute_command(command)
            
            # Clear selection and update canvas
            self.canvas.canvas_widget.set_selected_element(None)
            self.canvas.canvas_widget.update()
            self.properties_panel.set_selected_element(None)
    
    def undo(self):
        """Undo last action"""
        if self.undo_manager.undo():
            self.canvas.canvas_widget.update()
            # Refresh properties panel if element is selected
            if self.canvas.canvas_widget.selected_element_id:
                self.on_element_selected(self.canvas.canvas_widget.selected_element_id)
    
    def redo(self):
        """Redo last undone action"""
        if self.undo_manager.redo():
            self.canvas.canvas_widget.update()
            # Refresh properties panel if element is selected
            if self.canvas.canvas_widget.selected_element_id:
                self.on_element_selected(self.canvas.canvas_widget.selected_element_id)
    
    def copy_selected_element(self):
        """Copy selected element to clipboard"""
        if not self.program_manager.current_program:
            return
        
        selected_id = self.canvas.canvas_widget.selected_element_id
        if not selected_id:
            return
        
        # Find and copy element
        program = self.program_manager.current_program
        for elem in program.elements:
            if elem.get("id") == selected_id:
                from copy import deepcopy
                self.clipboard_element = deepcopy(elem)
                break
    
    def paste_element(self):
        """Paste element from clipboard"""
        if not self.clipboard_element or not self.program_manager.current_program:
            return
        
        program = self.program_manager.current_program
        
        # Create new element with new ID
        from copy import deepcopy
        from datetime import datetime
        new_element = deepcopy(self.clipboard_element)
        new_element["id"] = f"element_{datetime.now().timestamp()}_{id(new_element)}"
        # Offset position slightly
        new_element["x"] = new_element.get("x", 0) + 20
        new_element["y"] = new_element.get("y", 0) + 20
        
        # Create undo command
        from core.undo_redo import ElementCommand
        command = ElementCommand(
            program, new_element["id"], "add",
            old_data=None,
            new_data=new_element
        )
        self.undo_manager.execute_command(command)
        
        # Select new element
        self.canvas.canvas_widget.set_selected_element(new_element["id"])
        self.canvas.canvas_widget.update()
        self.on_element_selected(new_element["id"])
    
    def move_selected_element(self, dx: int, dy: int):
        """Move selected element by offset"""
        if not self.program_manager.current_program:
            return
        
        selected_id = self.canvas.canvas_widget.selected_element_id
        if not selected_id:
            return
        
        program = self.program_manager.current_program
        for elem in program.elements:
            if elem.get("id") == selected_id:
                old_data = elem.copy()
                elem["x"] = max(0, elem.get("x", 0) + dx)
                elem["y"] = max(0, elem.get("y", 0) + dy)
                new_data = elem.copy()
                
                # Create undo command for move
                from core.undo_redo import ElementCommand
                command = ElementCommand(
                    program, selected_id, "move",
                    old_data=old_data,
                    new_data=new_data
                )
                self.undo_manager.execute_command(command)
                
                self.canvas.canvas_widget.update()
                break
    
    def duplicate_selected_element(self):
        """Duplicate selected element"""
        if not self.program_manager.current_program:
            return
        
        selected_id = self.canvas.canvas_widget.selected_element_id
        if not selected_id:
            return
        
        program = self.program_manager.current_program
        for elem in program.elements:
            if elem.get("id") == selected_id:
                from copy import deepcopy
                from datetime import datetime
                new_element = deepcopy(elem)
                new_element["id"] = f"element_{datetime.now().timestamp()}_{id(new_element)}"
                new_element["x"] = new_element.get("x", 0) + 20
                new_element["y"] = new_element.get("y", 0) + 20
                
                # Create undo command
                from core.undo_redo import ElementCommand
                command = ElementCommand(
                    program, new_element["id"], "add",
                    old_data=None,
                    new_data=new_element
                )
                self.undo_manager.execute_command(command)
                
                # Select new element
                self.canvas.canvas_widget.set_selected_element(new_element["id"])
                self.canvas.canvas_widget.update()
                self.on_element_selected(new_element["id"])
                break
    
    def align_selected_elements(self, alignment: str):
        """Align selected elements"""
        if not self.program_manager.current_program:
            return
        
        selected_ids = self.canvas.canvas_widget.selected_element_ids
        if len(selected_ids) < 1:
            return
        
        program = self.program_manager.current_program
        elements = [e for e in program.elements if e.get("id") in selected_ids]
        
        if not elements:
            return
        
        from ui.alignment_tools import AlignmentTools
        
        # Store old state for undo
        old_states = {e.get("id"): (e.get("x", 0), e.get("y", 0)) for e in elements}
        
        # Perform alignment
        if alignment == "left":
            AlignmentTools.align_left(elements)
        elif alignment == "right":
            AlignmentTools.align_right(elements)
        elif alignment == "center_h":
            AlignmentTools.align_center_horizontal(elements)
        elif alignment == "top":
            AlignmentTools.align_top(elements)
        elif alignment == "bottom":
            AlignmentTools.align_bottom(elements)
        elif alignment == "center_v":
            AlignmentTools.align_center_vertical(elements)
        elif alignment == "distribute_h":
            AlignmentTools.distribute_horizontal(elements)
        elif alignment == "distribute_v":
            AlignmentTools.distribute_vertical(elements)
        
        # Create undo commands for each element
        for elem in elements:
            elem_id = elem.get("id")
            old_x, old_y = old_states.get(elem_id, (0, 0))
            old_data = {"id": elem_id, "x": old_x, "y": old_y, "width": elem.get("width", 200), "height": elem.get("height", 100), "type": elem.get("type", ""), "properties": elem.get("properties", {})}
            new_data = elem.copy()
            
            from core.undo_redo import ElementCommand
            command = ElementCommand(
                program, elem_id, "move",
                old_data=old_data,
                new_data=new_data
            )
            self.undo_manager.execute_command(command)
        
        self.canvas.canvas_widget.update()
    
    def on_discover_controllers(self):
        """Handle discover controllers request"""
        from ui.controller_dialog import ControllerDialog
        dialog = ControllerDialog(self)
        dialog.exec()
    
    def on_connect_controller(self):
        """Handle connect to controller"""
        from ui.controller_dialog import ControllerDialog
        from controllers.base_controller import ConnectionStatus
        
        dialog = ControllerDialog(self)
        if dialog.exec():
            controller = dialog.get_controller()
            if controller:
                if controller.connect():
                    self.current_controller = controller
                    # Set up callbacks
                    controller.on_status_changed = lambda s: self.update_connection_status(s)
                    controller.on_progress = lambda p, m: self.update_progress(p, m)
                    
                    # Auto-read brightness at startup (as per functional spec)
                    if hasattr(self, 'dashboard_window') and self.dashboard_window:
                        from ui.dashboard import Dashboard
                        dashboard_widget = self.dashboard_window.findChild(Dashboard)
                        if dashboard_widget:
                            dashboard_widget.set_controller(controller)
                    
                    # Check license for this controller
                    controller_id = controller.get_controller_id()
                    if controller_id:
                        try:
                            from core.license_manager import LicenseManager
                            license_manager = LicenseManager()
                            
                            if not license_manager.has_valid_license(controller_id):
                                from PyQt6.QtWidgets import QMessageBox
                                reply = QMessageBox.question(
                                    self, "License Required",
                                    f"License not activated for controller {controller_id}.\n\n"
                                    "Would you like to activate now?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                )
                                if reply == QMessageBox.StandardButton.Yes:
                                    # Open license activation dialog
                                    from ui.login_dialog import LoginDialog
                                    activation_dialog = LoginDialog(self, controller_id=controller_id)
                                    activation_dialog.exec()
                        except Exception as e:
                            from utils.logger import get_logger
                            logger = get_logger(__name__)
                            logger.warning(f"License check error: {e}")
                    
                    # Get device info
                    device_info = controller.get_device_info()
                    device_name = device_info.get("name", "Controller") if device_info else "Controller"
                    self.status_bar.set_connection_status(ConnectionStatus.CONNECTED, device_name)
                    
                    # Update dashboard if open
                    if self.dashboard_window:
                        from ui.dashboard import Dashboard
                        dashboard_widget = self.dashboard_window.findChild(Dashboard)
                        if dashboard_widget:
                            dashboard_widget.set_controller(controller)
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Connection Failed", 
                                      "Could not connect to controller. Please check the IP address and port.")
    
    def on_disconnect_controller(self):
        """Handle disconnect from controller"""
        if self.current_controller:
            self.current_controller.disconnect()
            self.current_controller = None
            from controllers.base_controller import ConnectionStatus
            self.status_bar.set_connection_status(ConnectionStatus.DISCONNECTED)
    
    def on_upload_program(self):
        """Handle upload program to controller (with sync comparison)"""
        if not self.current_controller:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Not Connected", "Please connect to a controller first.")
            return
        
        if not self.program_manager.current_program:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Program", "Please create or open a program first.")
            return
        
        # Use sync manager for intelligent upload (only send changes)
        try:
            from core.sync_manager import SyncManager
            sync_manager = SyncManager()
            
            # Export with diff comparison
            if sync_manager.export_to_controller(self.current_controller, self.program_manager):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Success", "Program synchronized successfully!")
                self.status_bar.clear_progress()
            else:
                # Fallback to direct upload
                program = self.program_manager.current_program
                program_dict = program.to_dict()
                if self.current_controller.upload_program(program_dict):
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Success", "Program uploaded successfully!")
                    self.status_bar.clear_progress()
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Upload Failed", "Failed to upload program to controller.")
        except Exception as e:
            # Fallback to direct upload on error
            program = self.program_manager.current_program
            program_dict = program.to_dict()
            if self.current_controller.upload_program(program_dict):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Success", "Program uploaded successfully!")
                self.status_bar.clear_progress()
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Upload Failed", "Failed to upload program to controller.")
    
    def on_download_program(self):
        """Handle download program from controller (full import)"""
        if not self.current_controller:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Not Connected", "Please connect to a controller first.")
            return
        
        # Use sync manager for full import
        try:
            from core.sync_manager import SyncManager
            from core.media_library import MediaLibrary
            sync_manager = SyncManager()
            media_library = MediaLibrary()
            
            # Import all data from controller
            imported_data = sync_manager.import_from_controller(self.current_controller)
            
            if imported_data.get("programs"):
                # Load first program or let user select
                program_ids = list(imported_data["programs"].keys())
                if program_ids:
                    program_data = imported_data["programs"][program_ids[0]]["data"]
                    from core.program_manager import Program
                    program = Program.from_dict(program_data)
                    self.program_manager.add_program(program)
                    self.program_manager.current_program = program
                    self.program_list_panel.refresh_programs()
                    self.canvas.set_program(program)
                    self.properties_panel.set_program(program)
                    self.status_bar.set_program_name(program.name)
                    self.status_bar.clear_progress()
                    
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Success", 
                        f"Imported {len(program_ids)} program(s) from controller successfully!")
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "No Programs", "No programs found on controller.")
            else:
                # Fallback to single program download
                program_dict = self.current_controller.download_program()
                if program_dict:
                    from core.program_manager import Program
                    program = Program.from_dict(program_dict.get("program", program_dict))
                    self.program_manager.add_program(program)
                    self.program_manager.current_program = program
                    self.program_list_panel.refresh_programs()
                    self.canvas.set_program(program)
                    self.properties_panel.set_program(program)
                    self.status_bar.set_program_name(program.name)
                    self.status_bar.clear_progress()
                    
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Success", "Program downloaded successfully!")
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Download Failed", "Failed to download program from controller.")
        except Exception as e:
            # Fallback to direct download on error
            program_dict = self.current_controller.download_program()
            if program_dict:
                from core.program_manager import Program
                program = Program.from_dict(program_dict.get("program", program_dict))
                self.program_manager.add_program(program)
                self.program_manager.current_program = program
                self.program_list_panel.refresh_programs()
                self.canvas.set_program(program)
                self.properties_panel.set_program(program)
                self.status_bar.set_program_name(program.name)
                self.status_bar.clear_progress()
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Success", "Program downloaded successfully!")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Download Failed", "Failed to download program from controller.")
    
    def update_connection_status(self, status):
        """Update connection status in status bar"""
        from controllers.base_controller import ConnectionStatus
        
        # Auto "Get network" if no device detected (as per functional spec)
        if status == ConnectionStatus.DISCONNECTED:
            # Try to discover controllers automatically
            try:
                from core.controller_discovery import ControllerDiscovery
                discovery = ControllerDiscovery()
                discovery.start_scan()
            except Exception as e:
                from utils.logger import get_logger
                logger = get_logger(__name__)
                logger.warning(f"Auto-discovery failed: {e}")
        
        device_name = ""
        if self.current_controller and self.current_controller.device_info:
            device_name = self.current_controller.device_info.get("name", "")
        self.status_bar.set_connection_status(status, device_name)
    
    def update_progress(self, progress: int, message: str):
        """Update progress in status bar"""
        self.status_bar.set_progress(f"{message} ({progress}%)")
    
    def on_preview(self):
        """Open preview window"""
        if not self.program_manager.current_program:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Program", "Please create or open a program first.")
            return
        
        from ui.preview_window import PreviewWindow
        
        if self.preview_window is None or not self.preview_window.isVisible():
            self.preview_window = PreviewWindow(self)
            self.preview_window.closed.connect(lambda: setattr(self, 'preview_window', None))
        
        self.preview_window.set_program(self.program_manager.current_program)
        self.preview_window.show()
        self.preview_window.raise_()
        self.preview_window.activateWindow()
    
    def on_dashboard(self):
        """Open dashboard window"""
        from ui.dashboard import Dashboard
        
        if self.dashboard_window is None or not self.dashboard_window.isVisible():
            dialog = QDialog(self)
            dialog.setWindowTitle("Dashboard - Time / Power / Lux / Network / Diagnostics")
            dialog.setMinimumSize(800, 600)
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            
            dashboard = Dashboard()
            dashboard.set_controller(self.current_controller)
            layout.addWidget(dashboard)
            
            self.dashboard_window = dialog
        
        # Update controller reference when opening
        if self.dashboard_window:
            dashboard_widget = self.dashboard_window.findChild(Dashboard)
            if dashboard_widget:
                dashboard_widget.set_controller(self.current_controller)
        
        self.dashboard_window.show()
        self.dashboard_window.raise_()
        self.dashboard_window.activateWindow()
    
    def on_program_renamed(self, program_id: str, new_name: str):
        """Handle program rename"""
        program = self.program_manager.get_program_by_id(program_id)
        if program:
            program.name = new_name
            program.modified = datetime.now().isoformat()
            self.program_list_panel.refresh_programs()
            self.status_bar.set_program_name(program.name)
    
    def on_program_duplicated(self, program_id: str):
        """Handle program duplication"""
        from core.program_manager import Program
        from copy import deepcopy
        
        program = self.program_manager.get_program_by_id(program_id)
        if program:
            new_program = Program()
            new_program.from_dict(deepcopy(program.to_dict()))
            new_program.id = f"program_{datetime.now().timestamp()}"
            new_program.name = f"{program.name} (Copy)"
            new_program.created = datetime.now().isoformat()
            new_program.modified = datetime.now().isoformat()
            
            self.program_manager.add_program(new_program)
            self.program_list_panel.refresh_programs()
    
    def on_program_moved(self, program_id: str, direction: int):
        """Handle program move up/down"""
        programs = self.program_manager.programs
        for i, prog in enumerate(programs):
            if prog.id == program_id:
                new_index = i + direction
                if 0 <= new_index < len(programs):
                    programs[i], programs[new_index] = programs[new_index], programs[i]
                    self.program_list_panel.refresh_programs()
                break
    
    def on_program_activated(self, program_id: str, enabled: bool):
        """Handle program activate/deactivate"""
        program = self.program_manager.get_program_by_id(program_id)
        if program:
            # Store activation state in program properties
            if "activation" not in program.properties:
                program.properties["activation"] = {}
            program.properties["activation"]["enabled"] = enabled
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop auto-save
        self.auto_save_manager.stop()
        
        # Save window position and size
        from config.settings import settings
        settings.set("window.width", self.width())
        settings.set("window.height", self.height())
        settings.set("window.x", self.x())
        settings.set("window.y", self.y())
        settings.save_settings()
        event.accept()

