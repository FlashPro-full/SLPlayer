"""
Program list panel with three-level hierarchy: Screen -> Program -> Content
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QToolButton, QHBoxLayout, QCheckBox, QMenu, QInputDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QTimer, QEvent
from PyQt5.QtGui import QMouseEvent, QContextMenuEvent
from typing import TYPE_CHECKING, Optional, Dict, List
from datetime import datetime

if TYPE_CHECKING:
    from core.program_manager import ProgramManager

from core.program_manager import ProgramManager
from core.screen_manager import ScreenManager
from config.i18n import tr


class ProgramListPanel(QWidget):
    """Program list panel with three-level hierarchy: Screen -> Program -> Content"""
    
    # Screen signals
    screen_selected = pyqtSignal(str)
    screen_renamed = pyqtSignal(str, str)
    screen_deleted = pyqtSignal(str)
    new_screen_requested = pyqtSignal()
    add_program_requested = pyqtSignal(str)
    screen_insert_requested = pyqtSignal(str)
    screen_download_requested = pyqtSignal(str)
    screen_close_requested = pyqtSignal(str)
    screen_paste_requested = pyqtSignal(str)
    
    # Program signals
    program_selected = pyqtSignal(str)
    new_program_requested = pyqtSignal()  # For creating new program without screen context
    program_renamed = pyqtSignal(str, str)
    delete_program_requested = pyqtSignal(str)
    program_deleted = pyqtSignal(str)  # Alias for compatibility
    program_duplicated = pyqtSignal(str)
    program_moved = pyqtSignal(str, int)
    program_activated = pyqtSignal(str, bool)
    program_checked = pyqtSignal(str, bool)
    program_copy_requested = pyqtSignal(str)
    program_paste_requested = pyqtSignal(str)
    program_add_content_requested = pyqtSignal(str, str)  # program_id, content_type
    
    # Content signals
    content_selected = pyqtSignal(str, str)  # program_id, element_id
    content_renamed = pyqtSignal(str, str, str)  # program_id, element_id, new_name
    content_deleted = pyqtSignal(str, str)  # program_id, element_id
    content_add_requested = pyqtSignal(str, str)  # program_id, content_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program_manager: Optional[ProgramManager] = None
        self._refreshing = False
        self._last_selected_screen = None
        self._last_selected_program = None
        self._last_selected_content = None
        self.init_ui()
    
    def set_program_manager(self, program_manager: ProgramManager):
        """Set the program manager"""
        self.program_manager = program_manager
        self.refresh_programs()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet("""
            QWidget {
                background-color: #D6D6D6;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(4, 2, 4, 2)
        toolbar_layout.setSpacing(2)
        toolbar_layout.addStretch()
        
        # Select all checkbox
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.setToolTip("Select/Deselect active program or all programs in active screen")
        self.select_all_checkbox.setTristate(True)
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        self.select_all_checkbox.setStyleSheet("""
            QCheckBox {
                margin-top: 2px;
            }
        """)
        toolbar_layout.addWidget(self.select_all_checkbox)
        
        # Toolbar buttons
        self.copy_btn = QToolButton()
        self.copy_btn.setText("📑")
        self.copy_btn.setToolTip("Copy")
        self.copy_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
        """)
        self.copy_btn.clicked.connect(self.on_copy_clicked)
        toolbar_layout.addWidget(self.copy_btn)
        
        self.paste_btn = QToolButton()
        self.paste_btn.setText("📋")
        self.paste_btn.setToolTip("Paste")
        self.paste_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
        """)
        self.paste_btn.clicked.connect(self.on_paste_clicked)
        toolbar_layout.addWidget(self.paste_btn)
        
        self.up_btn = QToolButton()
        self.up_btn.setText("🔼")
        self.up_btn.setToolTip(tr("program_list.move_up"))
        self.up_btn.clicked.connect(self.on_move_up)
        self.up_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
        """)
        toolbar_layout.addWidget(self.up_btn)
        
        self.down_btn = QToolButton()
        self.down_btn.setText("🔽")
        self.down_btn.setToolTip(tr("program_list.move_down"))
        self.down_btn.clicked.connect(self.on_move_down)
        self.down_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
        """)
        toolbar_layout.addWidget(self.down_btn)
        
        self.close_btn = QToolButton()
        self.close_btn.setText("❌")
        self.close_btn.setToolTip(tr("program_list.delete"))
        self.close_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
        """)
        self.close_btn.clicked.connect(self.on_delete_clicked)
        toolbar_layout.addWidget(self.close_btn)
        
        layout.addWidget(toolbar_widget)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        self.tree.setItemsExpandable(True)
        self.tree.setSelectionBehavior(QTreeWidget.SelectItems)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.currentItemChanged.connect(self._on_current_item_changed)
        self.tree.installEventFilter(self)
        
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #FFFFFF;
                border: none;
                padding: 2px;
            }
            QTreeWidget::item {
                padding: 4px 2px;
                height: 20px;
            }
            QTreeWidget::item:selected {
                background-color: #E8E8E8;
                color: #000000;
            }
            QTreeWidget::item:selected:hover {
                background-color: #E0E0E0;
            }
            QTreeWidget::item:hover {
                background-color: #F5F5F5;
            }
        """)
        
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree, stretch=1)
    
    def refresh_programs(self):
        """Refresh the program list with performance optimizations"""
        if not self.program_manager:
            return
        
        if hasattr(self, '_refresh_timer'):
            self._refresh_timer.stop()
        
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_refresh_programs)
        self._refresh_timer.start(50)  # 50ms debounce
    
    def _do_refresh_programs(self):
        """Internal method to perform the actual refresh"""
        if not self.program_manager:
            return
        
        self._refreshing = True
        self.tree.blockSignals(True)
        
        # Build screen structure
        screens = {}
        for program in self.program_manager.programs:
            screen_name = ScreenManager.get_screen_name_from_program(program)
            if screen_name not in screens:
                screens[screen_name] = []
            screens[screen_name].append(program)
        
        # Clear and rebuild tree
        self.tree.clear()
        
        # Build a map of items for easy lookup
        item_map = {}  # {program_id: program_item, (program_id, element_id): element_item}
        screen_item_map = {}  # {screen_name: screen_item}
        
        for screen_name, programs in screens.items():
            # Level 1: Screen
            screen_item = QTreeWidgetItem(self.tree)
            screen_item.setText(0, f"🖥 {screen_name}")
            screen_item.setData(0, Qt.UserRole, "screen")
            screen_item.setData(0, Qt.UserRole + 1, screen_name)  # Store screen name
            screen_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            screen_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            screen_item_map[screen_name] = screen_item
            
            for program in programs:
                # Level 2: Program
                program_item = QTreeWidgetItem(screen_item)
                is_checked = program.properties.get("checked", True)
                program.properties["checked"] = is_checked
                program_item.setText(0, f"💽 {program.name}")
                program_item.setData(0, Qt.UserRole, "program")
                program_item.setData(0, Qt.UserRole + 1, program.id)
                program_item.setData(0, Qt.UserRole + 2, is_checked)
                program_item.setCheckState(0, Qt.Checked if is_checked else Qt.Unchecked)
                program_item.setFlags(program_item.flags() | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
                program_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                item_map[program.id] = program_item
                
                # Level 3: Content elements
                for element in program.elements:
                    element_item = QTreeWidgetItem(program_item)
                    element_type = element.get("type", "unknown")
                    element_name = element.get("name", element_type)
                    element_id = element.get("id", "")
                    
                    # Icon based on content type
                    icon_map = {
                        "video": "🎞",
                        "image": "🌄",
                        "picture": "🌄",
                        "photo": "🌄",
                        "text": "🔠",
                        "singleline_text": "🔤",
                        "animation": "🎇",
                        "3d_text": "🧊",
                        "clock": "🕓",
                        "calendar": "🗓",
                        "timing": "⌛️",
                        "weather": "🌦",
                        "neon": "🪄",
                        "wps": "📚",
                        "table": "📅",
                        "office": "🗃",
                        "digital_watch": "📟",
                        "html": "🌐",
                        "livestream": "🎥",
                        "qrcode": "🧿"
                    }
                    icon = icon_map.get(element_type, "📄")
                    element_item.setText(0, f"{icon} {element_name}")
                    element_item.setData(0, Qt.UserRole, "content")
                    element_item.setData(0, Qt.UserRole + 1, program.id)
                    element_item.setData(0, Qt.UserRole + 2, element_id)
                    element_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                    element_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicator)
                    item_map[(program.id, element_id)] = element_item
        
        self.tree.expandAll()
        self.tree.blockSignals(False)
        self._refreshing = False
        
        # Restore selection based on user's last selection (not current_program_id)
        current_item = None
        
        # Priority 1: Restore previously selected content
        if self._last_selected_content:
            target_program_id, target_element_id = self._last_selected_content
            current_item = item_map.get((target_program_id, target_element_id))
        
        # Priority 2: Restore previously selected program
        if not current_item and self._last_selected_program:
            current_item = item_map.get(self._last_selected_program)
        
        # Priority 3: Restore previously selected screen
        if not current_item and self._last_selected_screen:
            current_item = screen_item_map.get(self._last_selected_screen)
        
        # Priority 4: If no previous selection, select the top program in the first screen
        if not current_item:
            # Find the first screen
            if self.tree.topLevelItemCount() > 0:
                first_screen_item = self.tree.topLevelItem(0)
                # Find the first program under the first screen
                if first_screen_item and first_screen_item.childCount() > 0:
                    current_item = first_screen_item.child(0)
        
        # Set selection if we have an item
        if current_item:
            self.tree.setCurrentItem(current_item)
            current_item.setSelected(True)
            self.tree.scrollToItem(current_item)
            QTimer.singleShot(10, lambda: self._emit_item_signal(current_item))
        
        self._update_select_all_checkbox()
    
    def _on_selection_changed(self):
        """Handle selection change"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        self._emit_item_signal(item)
    
    def _on_current_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        """Handle current item change"""
        if current:
            if not current.isSelected():
                current.setSelected(True)
            QTimer.singleShot(0, lambda: self._emit_item_signal(current))
    
    def eventFilter(self, obj, event):
        """Event filter to handle mouse clicks"""
        if obj == self.tree and event.type() == QEvent.MouseButtonPress:
            mouse_event = event
            item = self.tree.itemAt(mouse_event.pos())
            if item:
                item_type = item.data(0, Qt.UserRole)
                if item_type == "screen":
                    visual_rect = self.tree.visualItemRect(item)
                    arrow_width = 20
                    item_x = visual_rect.x()
                    click_x = mouse_event.pos().x()
                    
                    if not (item.childCount() > 0 and click_x >= item_x and click_x <= item_x + arrow_width):
                        self.tree.setCurrentItem(item)
                        item.setSelected(True)
                        return False
        return super().eventFilter(obj, event)
    
    def _emit_item_signal(self, item: QTreeWidgetItem):
        """Emit the appropriate signal for the item"""
        if not item:
            return
        
        try:
            item_type = item.data(0, Qt.UserRole)
            
            if item_type == "screen":
                screen_name = item.data(0, Qt.UserRole + 1)
                self._last_selected_screen = screen_name
                self._last_selected_program = None
                self._last_selected_content = None
                self.screen_selected.emit(screen_name)
                self._update_select_all_checkbox()
            elif item_type == "program":
                program_id = item.data(0, Qt.UserRole + 1)
                self._last_selected_program = program_id
                self._last_selected_screen = None
                self._last_selected_content = None
                self.program_selected.emit(program_id)
                self._update_select_all_checkbox()
            elif item_type == "content":
                program_id = item.data(0, Qt.UserRole + 1)
                element_id = item.data(0, Qt.UserRole + 2)
                self._last_selected_content = (program_id, element_id)
                self._last_selected_screen = None
                self._last_selected_program = None
                self.content_selected.emit(program_id, element_id)
                self._update_select_all_checkbox()
        except Exception as e:
            pass
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double click - expand/collapse"""
        if item is None:
            return
        
        item_type = item.data(0, Qt.UserRole)
        if item_type == "screen":
            item.setExpanded(not item.isExpanded())
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        if item is None:
            return
        
        self.tree.setCurrentItem(item)
        item.setSelected(True)
        self._emit_item_signal(item)
    
    def _on_context_menu(self, position: QPoint):
        """Handle context menu request"""
        item = self.tree.itemAt(position)
        if item is None:
            return
        
        item_type = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        
        if item_type == "screen":
            # Screen context menu
            screen_name = item.data(0, Qt.UserRole + 1)
            
            rename_action = menu.addAction("📝 Rename")
            rename_action.triggered.connect(lambda: self._on_screen_rename(screen_name))
            
            delete_action = menu.addAction("❌ Delete")
            delete_action.triggered.connect(lambda: self._on_screen_delete(screen_name))
            
            menu.addSeparator()
            
            new_screen_action = menu.addAction("🖥 New Screen")
            new_screen_action.triggered.connect(self._on_new_screen)
            
            add_program_action = menu.addAction("💽 Add program")
            add_program_action.triggered.connect(lambda: self._on_add_program(screen_name))
            
            insert_action = menu.addAction("📲 Insert")
            insert_action.triggered.connect(lambda: self._on_screen_insert(screen_name))
            
            download_action = menu.addAction("⬇️ Download")
            download_action.triggered.connect(lambda: self._on_screen_download(screen_name))
            
            close_action = menu.addAction("✖️ Close")
            close_action.triggered.connect(lambda: self._on_screen_close(screen_name))
        else:
            # Program or Content context menu
            rename_action = menu.addAction("📝 Rename")
            delete_action = menu.addAction("❌ Delete")
            
            if item_type == "program":
                program_id = item.data(0, Qt.UserRole + 1)
                rename_action.triggered.connect(lambda: self._on_program_rename(program_id))
                delete_action.triggered.connect(lambda: self._on_program_delete(program_id))
                
                menu.addSeparator()
                
                # Content type actions
                content_actions = [
                    ("🎞 Add Video", "video"),
                    ("🌄 Add Photo", "photo"),
                    ("🔠 Add Text", "text"),
                    ("🔤 Add SingleLineText", "singleline_text"),
                    ("🎇 Add Animation", "animation"),
                    ("🧊 Add 3D Text", "3d_text"),
                    ("🕓 Add Clock", "clock"),
                    ("🗓 Add Calendar", "calendar"),
                    ("⌛️ Add Timing", "timing"),
                    ("🌦 Add Weather", "weather"),
                    ("🪄 Add Neon", "neon"),
                    ("📚 Add WPS", "wps"),
                    ("📅 Add Table", "table"),
                    ("🗃 Add Office", "office"),
                    ("📟 Add Digital Watch", "digital_watch"),
                    ("🌐 Add HTML", "html"),
                    ("🎥 Add LiveStream", "livestream"),
                    ("🧿 Add QR code", "qrcode")
                ]
                
                for action_text, content_type in content_actions:
                    action = menu.addAction(action_text)
                    action.triggered.connect(lambda checked, pid=program_id, ct=content_type: 
                                           self.content_add_requested.emit(pid, ct))
                
                menu.addSeparator()
                
                copy_action = menu.addAction("📑 Copy")
                copy_action.triggered.connect(lambda: self.program_copy_requested.emit(program_id))
            else:  # content
                program_id = item.data(0, Qt.UserRole + 1)
                element_id = item.data(0, Qt.UserRole + 2)
                rename_action.triggered.connect(lambda: self._on_content_rename(program_id, element_id))
                delete_action.triggered.connect(lambda: self._on_content_delete(program_id, element_id))
                
                menu.addSeparator()
                
                # Content type actions (same as program)
                content_actions = [
                    ("🎞 Add Video", "video"),
                    ("🌄 Add Photo", "photo"),
                    ("🔠 Add Text", "text"),
                    ("🔤 Add SingleLineText", "singleline_text"),
                    ("🎇 Add Animation", "animation"),
                    ("🧊 Add 3D Text", "3d_text"),
                    ("🕓 Add Clock", "clock"),
                    ("🗓 Add Calendar", "calendar"),
                    ("⌛️ Add Timing", "timing"),
                    ("🌦 Add Weather", "weather"),
                    ("🪄 Add Neon", "neon"),
                    ("📚 Add WPS", "wps"),
                    ("📅 Add Table", "table"),
                    ("🗃 Add Office", "office"),
                    ("📟 Add Digital Watch", "digital_watch"),
                    ("🌐 Add HTML", "html"),
                    ("🎥 Add LiveStream", "livestream"),
                    ("🧿 Add QR code", "qrcode")
                ]
                
                for action_text, content_type in content_actions:
                    action = menu.addAction(action_text)
                    action.triggered.connect(lambda checked, pid=program_id, ct=content_type: 
                                           self.content_add_requested.emit(pid, ct))
                
                menu.addSeparator()
                
                copy_action = menu.addAction("📑 Copy")
                copy_action.triggered.connect(lambda: self.program_copy_requested.emit(program_id))
        
        menu.exec_(self.tree.mapToGlobal(position))
    
    # Screen handlers
    def _on_screen_rename(self, screen_name: str):
        """Handle screen rename"""
        new_name, ok = QInputDialog.getText(self, "Rename Screen", "Enter new screen name:", text=screen_name)
        if ok and new_name:
            self.screen_renamed.emit(screen_name, new_name)
    
    def _on_screen_delete(self, screen_name: str):
        """Handle screen delete"""
        self.screen_deleted.emit(screen_name)
    
    def _on_new_screen(self):
        """Handle new screen"""
        self.new_screen_requested.emit()
    
    def _on_add_program(self, screen_name: str):
        """Handle add program"""
        self.add_program_requested.emit(screen_name)
    
    def _on_screen_insert(self, screen_name: str):
        """Handle screen insert"""
        self.screen_insert_requested.emit(screen_name)
    
    def _on_screen_download(self, screen_name: str):
        """Handle screen download"""
        self.screen_download_requested.emit(screen_name)
    
    def _on_screen_close(self, screen_name: str):
        """Handle screen close"""
        self.screen_close_requested.emit(screen_name)
    
    # Program handlers
    def _on_program_rename(self, program_id: str):
        """Handle program rename"""
        if self.program_manager:
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                new_name, ok = QInputDialog.getText(self, "Rename Program", "Enter new program name:", text=program.name)
                if ok and new_name:
                    self.program_renamed.emit(program_id, new_name)
    
    def _on_program_delete(self, program_id: str):
        """Handle program delete"""
        self.delete_program_requested.emit(program_id)
    
    # Content handlers
    def _on_content_rename(self, program_id: str, element_id: str):
        """Handle content rename"""
        if self.program_manager:
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                element = next((e for e in program.elements if e.get("id") == element_id), None)
                if element:
                    current_name = element.get("name", element.get("type", "Content"))
                    new_name, ok = QInputDialog.getText(self, "Rename Content", "Enter new content name:", text=current_name)
                    if ok and new_name:
                        self.content_renamed.emit(program_id, element_id, new_name)
    
    def _on_content_delete(self, program_id: str, element_id: str):
        """Handle content delete"""
        self.content_deleted.emit(program_id, element_id)
    
    # Toolbar handlers
    def on_copy_clicked(self):
        """Handle copy button click"""
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_copy_requested.emit(program_id)
    
    def on_paste_clicked(self):
        """Handle paste button click"""
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_paste_requested.emit(program_id)
    
    def on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.delete_program_requested.emit(program_id)
            elif item_type == "content":
                program_id = current_item.data(0, Qt.UserRole + 1)
                element_id = current_item.data(0, Qt.UserRole + 2)
                self.content_deleted.emit(program_id, element_id)
    
    def on_move_up(self):
        """Handle move up"""
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_moved.emit(program_id, -1)
    
    def on_move_down(self):
        """Handle move down"""
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_moved.emit(program_id, 1)
    
    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item change (rename or checkbox)"""
        if self._refreshing:
            return
        
        if item is None:
            return
        
        item_type = item.data(0, Qt.UserRole)
        
        if item_type == "program":
            checked = (item.checkState(0) == Qt.Checked)
            old_checked = item.data(0, Qt.UserRole + 2)
            if old_checked is None or old_checked != checked:
                self.tree.blockSignals(True)
                item.setData(0, Qt.UserRole + 2, checked)
                self.tree.blockSignals(False)
                
                if self.program_manager:
                    program_id = item.data(0, Qt.UserRole + 1)
                    program = self.program_manager.get_program_by_id(program_id)
                    if program:
                        program.properties["checked"] = checked
                
                program_id = item.data(0, Qt.UserRole + 1)
                self.program_checked.emit(program_id, checked)
                self._update_select_all_checkbox()
            else:
                # Handle rename
                text = item.text(0)
                new_name = text.replace("💽 ", "").strip()
                if new_name:
                    program_id = item.data(0, Qt.UserRole + 1)
                    self.program_renamed.emit(program_id, new_name)
        elif item_type == "content":
            # Handle content rename
            text = item.text(0)
            # Extract name after icon
            parts = text.split(" ", 1)
            if len(parts) > 1:
                new_name = parts[1]
                program_id = item.data(0, Qt.UserRole + 1)
                element_id = item.data(0, Qt.UserRole + 2)
                self.content_renamed.emit(program_id, element_id, new_name)
    
    def on_select_all_changed(self, state):
        """Handle select all checkbox - toggles active program or all programs in active screen"""
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        checked = (state == Qt.Checked)
        item_type = current_item.data(0, Qt.UserRole)
        
        self.tree.blockSignals(True)
        self.select_all_checkbox.blockSignals(True)
        
        if item_type == "program":
            # If a program is selected, toggle only that program
            program_item = current_item
            program_item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
            program_item.setData(0, Qt.UserRole + 2, checked)
            
            self.select_all_checkbox.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            self.select_all_checkbox.blockSignals(False)
            self.tree.blockSignals(False)
            
            if not self._refreshing:
                program_id = program_item.data(0, Qt.UserRole + 1)
                self.program_checked.emit(program_id, checked)
                self._update_select_all_checkbox()
        elif item_type == "screen":
            # If a screen is selected, toggle all programs in that screen
            screen_item = current_item
            for j in range(screen_item.childCount()):
                program_item = screen_item.child(j)
                if program_item.data(0, Qt.UserRole) == "program":
                    program_item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
                    program_item.setData(0, Qt.UserRole + 2, checked)
            
            self.select_all_checkbox.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            self.select_all_checkbox.blockSignals(False)
            self.tree.blockSignals(False)
            
            if not self._refreshing:
                for j in range(screen_item.childCount()):
                    program_item = screen_item.child(j)
                    if program_item.data(0, Qt.UserRole) == "program":
                        program_id = program_item.data(0, Qt.UserRole + 1)
                        self.program_checked.emit(program_id, checked)
                self._update_select_all_checkbox()
        else:
            # For content items, toggle the parent program
            program_item = current_item.parent()
            if program_item and program_item.data(0, Qt.UserRole) == "program":
                program_item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
                program_item.setData(0, Qt.UserRole + 2, checked)
                
                self.select_all_checkbox.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                self.select_all_checkbox.blockSignals(False)
                self.tree.blockSignals(False)
                
                if not self._refreshing:
                    program_id = program_item.data(0, Qt.UserRole + 1)
                    self.program_checked.emit(program_id, checked)
                    self._update_select_all_checkbox()
            else:
                self.select_all_checkbox.blockSignals(False)
                self.tree.blockSignals(False)
    
    def _get_selected_screen_item(self):
        """Get the selected screen item"""
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "screen":
                return current_item
            elif item_type == "program":
                return current_item.parent()
            elif item_type == "content":
                parent = current_item.parent()
                if parent:
                    return parent.parent()
        
        # Fallback to first screen
        if self.tree.topLevelItemCount() > 0:
            return self.tree.topLevelItem(0)
        return None
    
    def _update_select_all_checkbox(self):
        """Update the select all checkbox based on active item"""
        current_item = self.tree.currentItem()
        if not current_item:
            self.select_all_checkbox.blockSignals(True)
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
            self.select_all_checkbox.blockSignals(False)
            return
        
        item_type = current_item.data(0, Qt.UserRole)
        self.select_all_checkbox.blockSignals(True)
        
        if item_type == "program":
            # If a program is selected, show that program's state
            program_item = current_item
            if program_item.checkState(0) == Qt.Checked:
                self.select_all_checkbox.setCheckState(Qt.Checked)
            else:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif item_type == "screen":
            # If a screen is selected, show aggregate state of all programs
            screen_item = current_item
            checked_count = 0
            total_count = 0
            
            for j in range(screen_item.childCount()):
                program_item = screen_item.child(j)
                if program_item.data(0, Qt.UserRole) == "program":
                    total_count += 1
                    if program_item.checkState(0) == Qt.Checked:
                        checked_count += 1
            
            if total_count == 0:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
            elif checked_count == 0:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
            elif checked_count == total_count:
                self.select_all_checkbox.setCheckState(Qt.Checked)
            else:
                self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        else:
            # For content items, show the parent program's state
            program_item = current_item.parent()
            if program_item and program_item.data(0, Qt.UserRole) == "program":
                if program_item.checkState(0) == Qt.Checked:
                    self.select_all_checkbox.setCheckState(Qt.Checked)
                else:
                    self.select_all_checkbox.setCheckState(Qt.Unchecked)
            else:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
        
        self.select_all_checkbox.blockSignals(False)

