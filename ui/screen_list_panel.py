from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QToolButton, QHBoxLayout, QCheckBox, QMenu, QInputDialog, QShortcut)
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QTimer, QEvent
from PyQt5.QtGui import QMouseEvent, QContextMenuEvent, QKeyEvent, QKeySequence
from typing import TYPE_CHECKING, Optional, Dict, List
from datetime import datetime

if TYPE_CHECKING:
    from core.screen_manager import ScreenManager

from core.screen_manager import ScreenManager, Screen
from core.screen_config import get_screen_name, set_screen_name
from config.i18n import tr


class ScreenListPanel(QWidget):
    
    screen_selected = pyqtSignal(str)
    screen_renamed = pyqtSignal(str, str)
    screen_deleted = pyqtSignal(str)
    new_screen_requested = pyqtSignal()
    add_program_requested = pyqtSignal(str)
    screen_insert_requested = pyqtSignal(str)
    screen_send_requested = pyqtSignal(str)
    screen_close_requested = pyqtSignal(str)
    
    program_selected = pyqtSignal(str)
    program_renamed = pyqtSignal(str, str)
    delete_program_requested = pyqtSignal(str)
    program_deleted = pyqtSignal(str)
    program_copy_requested = pyqtSignal(str)
    program_paste_requested = pyqtSignal(str)
    program_moved = pyqtSignal(str, int)
    
    content_selected = pyqtSignal(str, str)
    content_renamed = pyqtSignal(str, str, str)
    delete_content_requested = pyqtSignal(str, str)
    content_deleted = pyqtSignal(str, str)
    content_add_requested = pyqtSignal(str, str)
    content_copy_requested = pyqtSignal(str, str)
    content_paste_requested = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.screen_manager: Optional[ScreenManager] = None
        self._refreshing = False
        self._last_selected_screen = None
        self._last_selected_program = None
        self._last_selected_content = None
        self._clipboard_data = None
        self._clipboard_type = None
        self._refresh_timer: Optional[QTimer] = None
        self.init_ui()
    
    def set_screen_manager(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager
        self.refresh_screens()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                border-right: 2px solid #555555;
            }
        """)
        
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                border-bottom: 2px solid #555555;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(4, 2, 4, 2)
        toolbar_layout.setSpacing(2)
        toolbar_layout.addStretch()
        
        TOOL_BUTTON_STYLE = """
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
        """
        
        self.up_btn = self._create_tool_button("🔼", tr("program_list.move_up") + " (Alt+↑)", self.on_move_up, TOOL_BUTTON_STYLE)
        toolbar_layout.addWidget(self.up_btn)
        
        self.down_btn = self._create_tool_button("🔽", tr("program_list.move_down") + " (Alt+↓)", self.on_move_down, TOOL_BUTTON_STYLE)
        toolbar_layout.addWidget(self.down_btn)
        
        self.close_btn = self._create_tool_button("❌", tr("program_list.delete") + " (Del)", self.on_delete_clicked, TOOL_BUTTON_STYLE)
        toolbar_layout.addWidget(self.close_btn)
        
        layout.addWidget(toolbar_widget)
        
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
        self.tree.setFocusPolicy(Qt.StrongFocus)
        
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #333333;
                border: none;
                padding: 2px;
                color: #FFFFFF;
            }
            QTreeWidget::item {
                padding: 4px 2px;
                height: 20px;
                color: #FFFFFF;
                outline: none;
            }
            QTreeWidget::item:selected {
                background-color: #3B3B3B;
                border: 1px solid #4A90E2;
                color: #FFFFFF;
                outline: none;
            }
            QTreeWidget::item:selected:hover {
                background-color: #3B3B3B;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QTreeWidget::item:hover {
                background-color: #3B3B3B;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QTreeWidget::item:focus {
                outline: none;
            }
        """)
        
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree, stretch=1)
        
        self._setup_keyboard_shortcuts()
    
    def keyPressEvent(self, event: Optional[QKeyEvent]):
        if event is None:
            return
        modifiers = event.modifiers()
        key = event.key()
        
        if key == Qt.Key_Delete:  # type: ignore
            self.on_delete_clicked()
            event.accept()
        elif modifiers == Qt.ControlModifier and key == Qt.Key_C:  # type: ignore
            self.on_copy_clicked()
            event.accept()
        elif modifiers == Qt.ControlModifier and key == Qt.Key_V:  # type: ignore
            self.on_paste_clicked()
            event.accept()
        elif key == Qt.Key_Up and modifiers == Qt.AltModifier:  # type: ignore
            self.on_move_up()
            event.accept()
        elif key == Qt.Key_Down and modifiers == Qt.AltModifier:  # type: ignore
            self.on_move_down()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def _setup_keyboard_shortcuts(self):
        copy_shortcut = QShortcut(QKeySequence.Copy, self.tree)
        copy_shortcut.activated.connect(self.on_copy_clicked)
        
        paste_shortcut = QShortcut(QKeySequence.Paste, self.tree)
        paste_shortcut.activated.connect(self.on_paste_clicked)
        
        delete_shortcut = QShortcut(QKeySequence.Delete, self.tree)
        delete_shortcut.activated.connect(self.on_delete_clicked)
        
        move_up_shortcut = QShortcut(QKeySequence("Alt+Up"), self.tree)
        move_up_shortcut.activated.connect(self.on_move_up)
        
        move_down_shortcut = QShortcut(QKeySequence("Alt+Down"), self.tree)
        move_down_shortcut.activated.connect(self.on_move_down)
    
    def refresh_screens(self, debounce: bool = True):
        if not self.screen_manager:
            return
        
        if debounce:
            if self._refresh_timer is not None:
                self._refresh_timer.stop()
            
            self._refresh_timer = QTimer()
            self._refresh_timer.setSingleShot(True)
            self._refresh_timer.timeout.connect(self._do_refresh_screens)
            self._refresh_timer.start(50)
        else:
            self._do_refresh_screens()
    
    def _do_refresh_screens(self):
        if not self.screen_manager:
            return
        
        self._refreshing = True
        self.tree.blockSignals(True)
        
        self.tree.clear()
        
        item_map = {}
        screen_item_map = {}
        
        for screen in self.screen_manager.screens:
            screen_name = screen.name
            screen_item = QTreeWidgetItem(self.tree)
            screen_item.setText(0, f"🖥 {screen_name}")
            screen_item.setData(0, Qt.UserRole, "screen")
            screen_item.setData(0, Qt.UserRole + 1, screen_name)
            screen_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            screen_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            screen_item_map[screen_name] = screen_item
            
            for program in screen.programs:
                program_item = QTreeWidgetItem(screen_item)
                program_item.setText(0, f"💽 {program.name}")
                program_item.setData(0, Qt.UserRole, "program")
                program_item.setData(0, Qt.UserRole + 1, program.id)
                program_item.setFlags(program_item.flags() | Qt.ItemIsEditable)
                program_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                item_map[program.id] = program_item
                
                for element in program.elements:
                    element_item = QTreeWidgetItem(program_item)
                    element_type = element.get("type", "unknown")
                    element_name = element.get("name", element_type)
                    element_id = element.get("id", "")
                    
                    icon_map = {
                        "video": "🎞",
                        "photo": "🌄",
                        "text": "🔠",
                        "singleline_text": "🔤",
                        "animation": "🎇",
                        "clock": "🕓",
                        "timing": "⌛️",
                        "weather": "🌦",
                        "sensor": "📎",
                        "html": "🌐",
                        "hdmi": "🔌"
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
        
        current_item = None
        
        if self._last_selected_content:
            target_program_id, target_element_id = self._last_selected_content
            current_item = item_map.get((target_program_id, target_element_id))
        
        if not current_item and self._last_selected_program:
            current_item = item_map.get(self._last_selected_program)
        
        if not current_item and self._last_selected_screen:
            current_item = screen_item_map.get(self._last_selected_screen)
        
        if not current_item:
            global_screen_name = get_screen_name()
            if global_screen_name:
                current_item = screen_item_map.get(global_screen_name)
                if current_item:
                    self._last_selected_screen = global_screen_name
        
        if not current_item:
            if self.tree.topLevelItemCount() > 0:
                first_screen_item = self.tree.topLevelItem(0)
                if first_screen_item and first_screen_item.childCount() > 0:
                    current_item = first_screen_item.child(0)
                    if first_screen_item:
                        screen_name = first_screen_item.data(0, Qt.UserRole + 1)
                        if screen_name:
                            self._last_selected_screen = screen_name
                            set_screen_name(screen_name)
                elif first_screen_item:
                    current_item = first_screen_item
                    if current_item:
                        screen_name = current_item.data(0, Qt.UserRole + 1)
                        if screen_name:
                            self._last_selected_screen = screen_name
                            set_screen_name(screen_name)
        
        if current_item:
            self.tree.setCurrentItem(current_item)
            current_item.setSelected(True)
            self.tree.scrollToItem(current_item)
            QTimer.singleShot(10, lambda: self._emit_item_signal(current_item))
        
    def _on_selection_changed(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        self._emit_item_signal(item)
    
    def _on_current_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        if current:
            if not current.isSelected():
                current.setSelected(True)
            QTimer.singleShot(0, lambda: self._emit_item_signal(current))
    
    def eventFilter(self, obj, event):
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
        if not item:
            return
        
        try:
            item_type = item.data(0, Qt.UserRole)  # type: ignore
            
            if item_type == "screen":
                screen_name = item.data(0, Qt.UserRole + 1)  # type: ignore
                self._last_selected_screen = screen_name
                self._last_selected_program = None
                self._last_selected_content = None
                set_screen_name(screen_name)
                self.screen_selected.emit(screen_name)
            elif item_type == "program":
                program_id = item.data(0, Qt.UserRole + 1)  # type: ignore
                self._last_selected_program = program_id
                self._last_selected_content = None
                parent = item.parent()
                if parent:
                    parent_screen_name = parent.data(0, Qt.UserRole + 1)  # type: ignore
                    if parent_screen_name:
                        self._last_selected_screen = parent_screen_name
                        set_screen_name(parent_screen_name)
                else:
                    self._last_selected_screen = None
                self.program_selected.emit(program_id)
            elif item_type == "content":
                program_id = item.data(0, Qt.UserRole + 1)  # type: ignore
                element_id = item.data(0, Qt.UserRole + 2)  # type: ignore
                self._last_selected_content = (program_id, element_id)
                self._last_selected_program = None
                parent = item.parent()
                if parent:
                    parent_parent = parent.parent()
                    if parent_parent:
                        parent_screen_name = parent_parent.data(0, Qt.UserRole + 1)  # type: ignore
                        if parent_screen_name:
                            self._last_selected_screen = parent_screen_name
                            set_screen_name(parent_screen_name)
                    else:
                        self._last_selected_screen = None
                else:
                    self._last_selected_screen = None
                self.content_selected.emit(program_id, element_id)
        except Exception as e:
            pass
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        if item is None:
            return
        
        item_type = item.data(0, Qt.UserRole) # type: ignore
        if item_type == "screen":
            item.setExpanded(not item.isExpanded())
    
    def _create_tool_button(self, text: str, tooltip: str, slot, style: str) -> QToolButton:
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(style)
        btn.clicked.connect(slot)
        return btn
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        if item is None:
            return
        
        self.tree.setCurrentItem(item)
        item.setSelected(True)
        self._emit_item_signal(item)
    
    def _on_context_menu(self, position: QPoint):
        item = self.tree.itemAt(position)
        if item is None:
            return
        
        item_type = item.data(0, Qt.UserRole) # type: ignore
        menu = QMenu(self)
        
        if item_type == "screen":
            screen_name = item.data(0, Qt.UserRole + 1) # type: ignore
            
            rename_action = menu.addAction(tr("program_list.rename"))
            if rename_action:
                rename_action.triggered.connect(lambda: self._on_screen_rename(screen_name))
            
            delete_action = menu.addAction(tr("program_list.delete"))
            if delete_action:
                delete_action.triggered.connect(lambda: self._on_screen_delete(screen_name))
            
            menu.addSeparator()
            
            new_screen_action = menu.addAction(tr("program_list.new_screen"))
            if new_screen_action:
                new_screen_action.triggered.connect(self._on_new_screen)
            
            add_program_action = menu.addAction(tr("program_list.add_program"))
            if add_program_action:
                add_program_action.triggered.connect(lambda: self._on_add_program(screen_name))
            
            insert_action = menu.addAction(tr("program_list.insert"))
            if insert_action:
                insert_action.triggered.connect(lambda: self._on_screen_insert(screen_name))
            
            close_action = menu.addAction(tr("program_list.close"))
            if close_action:
                close_action.triggered.connect(lambda: self._on_screen_close(screen_name))
        else:
            rename_action = menu.addAction(tr("program_list.rename"))
            delete_action = menu.addAction(tr("program_list.delete"))
            
            if item_type == "program":
                program_id = item.data(0, Qt.UserRole + 1)  # type: ignore
                if rename_action:
                    rename_action.triggered.connect(lambda: self._on_program_rename(program_id))
                if delete_action:
                    delete_action.triggered.connect(lambda: self._on_program_delete(program_id))
                
                menu.addSeparator()
                
                content_actions = [
                    (tr("program_list.add_video"), "video"),
                    (tr("program_list.add_photo"), "photo"),
                    (tr("program_list.add_text"), "text"),
                    (tr("program_list.add_singleline"), "singleline_text"),
                    (tr("program_list.add_animation"), "animation"),
                    (tr("program_list.add_clock"), "clock"),
                    (tr("program_list.add_timing"), "timing"),
                    (tr("program_list.add_weather"), "weather"),
                    (tr("program_list.add_sensor"), "sensor"),
                    (tr("program_list.add_html"), "html"),
                    (tr("program_list.add_hdmi"), "hdmi")
                ]
                
                for action_text, content_type in content_actions:
                    action = menu.addAction(action_text)
                    if action:
                        action.triggered.connect(lambda checked, pid=program_id, ct=content_type: 
                                               self.content_add_requested.emit(pid, ct))
                
                menu.addSeparator()
                
                copy_action = menu.addAction(tr("program_list.copy"))
                if copy_action:
                    copy_action.triggered.connect(lambda: self.program_copy_requested.emit(program_id))
            else:  # content
                program_id = item.data(0, Qt.UserRole + 1)  # type: ignore
                element_id = item.data(0, Qt.UserRole + 2)  # type: ignore
                if rename_action:
                    rename_action.triggered.connect(lambda: self._on_content_rename(program_id, element_id))
                if delete_action:
                    delete_action.triggered.connect(lambda: self._on_content_delete(program_id, element_id))
                
                menu.addSeparator()
                
                content_actions = [
                    (tr("program_list.add_video"), "video"),
                    (tr("program_list.add_photo"), "photo"),
                    (tr("program_list.add_text"), "text"),
                    (tr("program_list.add_singleline"), "singleline_text"),
                    (tr("program_list.add_animation"), "animation"),
                    (tr("program_list.add_clock"), "clock"),
                    (tr("program_list.add_timing"), "timing"),
                    (tr("program_list.add_weather"), "weather"),
                    (tr("program_list.add_sensor"), "sensor"),
                    (tr("program_list.add_html"), "html"),
                    (tr("program_list.add_hdmi"), "hdmi")
                ]
                
                for action_text, content_type in content_actions:
                    action = menu.addAction(action_text)
                    if action:
                        action.triggered.connect(lambda checked, pid=program_id, ct=content_type: 
                                               self.content_add_requested.emit(pid, ct))
                
                menu.addSeparator()
                
                copy_action = menu.addAction(tr("program_list.copy"))
                if copy_action:
                    copy_action.triggered.connect(lambda: self.content_copy_requested.emit(program_id, element_id))
        
        menu.exec_(self.tree.mapToGlobal(position))
    
    def _on_screen_rename(self, screen_name: str):
        new_name, ok = QInputDialog.getText(self, "Rename Screen", "Enter new screen name:", text=screen_name)
        if ok and new_name:
            self.screen_renamed.emit(screen_name, new_name)
    
    def _on_screen_delete(self, screen_name: str):
        self.screen_deleted.emit(screen_name)
    
    def _on_new_screen(self):
        self.new_screen_requested.emit()
    
    def _on_add_program(self, screen_name: str):
        self.add_program_requested.emit(screen_name)
    
    def add_new_screen(self):
        if not self.screen_manager:
            return None
        from core.screen_config import get_screen_config
        config = get_screen_config()
        width = config.get("width", 640) if config else 640
        height = config.get("height", 480) if config else 480
        
        import re
        existing_names = {s.name for s in self.screen_manager.screens}
        max_id = 0
        pattern = re.compile(r'^Screen(\d+)$')
        for name in existing_names:
            match = pattern.match(name)
            if match:
                screen_id = int(match.group(1))
                if screen_id > max_id:
                    max_id = screen_id
        
        screen_name = f"Screen{max_id + 1}"
        
        screen = self.screen_manager.create_screen(screen_name, width, height)
        from core.screen_config import set_screen_name
        set_screen_name(screen.name)
        
        self._last_selected_screen = screen.name
        self._last_selected_program = None
        self._last_selected_content = None
        
        self.refresh_screens(debounce=False)
        return screen.name
    
    def add_program_to_screen(self, screen_name: Optional[str] = None):
        if not self.screen_manager:
            return
        if not screen_name:
            screen_name = get_screen_name()
        if not screen_name:
            if not self.screen_manager.screens:
                self.add_new_screen()
                screen_name = get_screen_name()
            else:
                screen_name = self.screen_manager.screens[0].name
        if not screen_name:
            return
        screen = self.screen_manager.get_screen_by_name(screen_name)
        if not screen:
            self.add_new_screen()
            screen_name = get_screen_name()
            if screen_name:
                screen = self.screen_manager.get_screen_by_name(screen_name)
        if screen:
            from core.program_manager import ProgramManager
            from core.screen_config import get_screen_config
            import re
            config = get_screen_config()
            width = config.get("width", 640) if config else 640
            height = config.get("height", 480) if config else 480
            
            existing_program_names = [p.name for p in screen.programs]
            max_num = 0
            pattern = re.compile(r'^Program\s*(\d+)$', re.IGNORECASE)
            for name in existing_program_names:
                match = pattern.match(name.strip())
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)
            
            next_num = max_num + 1
            program_name = f"Program{next_num}"
            
            program_manager = None
            parent = self.parent()
            if parent and hasattr(parent, 'program_manager'):
                program_manager = parent.program_manager
            else:
                from core.program_manager import ProgramManager
                program_manager = ProgramManager()
            
            program = program_manager.create_program(program_name, width, height)
            screen.add_program(program)
            if hasattr(self.screen_manager, '_programs_by_id'):
                self.screen_manager._programs_by_id[program.id] = program
            self.refresh_screens(debounce=False)
    
    def _on_screen_insert(self, screen_name: str):
        self.screen_insert_requested.emit(screen_name)
    
    def _on_screen_close(self, screen_name: str):
        self.screen_close_requested.emit(screen_name)
    
    def _on_program_rename(self, program_id: str):
        if self.screen_manager:
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                new_name, ok = QInputDialog.getText(self, "Rename Program", "Enter new program name:", text=program.name)
                if ok and new_name:
                    self.program_renamed.emit(program_id, new_name)
    
    def _on_program_delete(self, program_id: str):
        self.delete_program_requested.emit(program_id)
    
    def _on_content_rename(self, program_id: str, element_id: str):
        if self.screen_manager:
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                element = next((e for e in program.elements if e.get("id") == element_id), None)
                if element:
                    current_name = element.get("name", element.get("type", "Content"))
                    new_name, ok = QInputDialog.getText(self, "Rename Content", "Enter new content name:", text=current_name)
                    if ok and new_name:
                        self.content_renamed.emit(program_id, element_id, new_name)
    
    def _on_content_delete(self, program_id: str, element_id: str):
        self.content_deleted.emit(program_id, element_id)
    
    def on_copy_clicked(self):
        current_item = self.tree.currentItem()
        if not current_item or not self.screen_manager:
            return
        
        item_type = current_item.data(0, Qt.UserRole)
        
        if item_type == "screen":
            screen_name = current_item.data(0, Qt.UserRole + 1)
            screen = self.screen_manager.get_screen_by_name(screen_name)
            if screen:
                import copy
                self._clipboard_data = {
                    "name": screen.name,
                    "width": screen.width,
                    "height": screen.height,
                    "programs": [p.to_dict() for p in screen.programs]
                }
                self._clipboard_type = "screen"
        elif item_type == "program":
            program_id = current_item.data(0, Qt.UserRole + 1)
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                import copy
                self._clipboard_data = program.to_dict()
                self._clipboard_type = "program"
        elif item_type == "content":
            program_id = current_item.data(0, Qt.UserRole + 1)
            element_id = current_item.data(0, Qt.UserRole + 2)
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                element = next((e for e in program.elements if e.get("id") == element_id), None)
                if element:
                    import copy
                    self._clipboard_data = copy.deepcopy(element)
                    self._clipboard_type = "content"
                    self._clipboard_program_id = program_id
    
    def on_paste_clicked(self):
        if not self._clipboard_data or not self._clipboard_type or not self.screen_manager:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        item_type = current_item.data(0, Qt.UserRole)
        
        if self._clipboard_type == "screen" and item_type == "screen":
            target_screen_name = current_item.data(0, Qt.UserRole + 1)
            target_screen = self.screen_manager.get_screen_by_name(target_screen_name)
            if target_screen:
                import uuid
                from core.program_manager import Program
                new_screen = self.screen_manager.create_screen(
                    f"{self._clipboard_data['name']}_Copy",
                    self._clipboard_data['width'],
                    self._clipboard_data['height']
                )
                for program_data in self._clipboard_data['programs']:
                    new_program = Program()
                    new_program.from_dict(program_data)
                    new_program.id = f"program_{uuid.uuid4().hex[:12]}"
                    for element in new_program.elements:
                        element["id"] = f"element_{uuid.uuid4().hex[:12]}"
                    new_screen.add_program(new_program)
                self.refresh_screens(debounce=False)
        elif self._clipboard_type == "program":
            if item_type == "screen":
                target_screen_name = current_item.data(0, Qt.UserRole + 1)
                target_screen = self.screen_manager.get_screen_by_name(target_screen_name)
                if target_screen:
                    import uuid
                    from core.program_manager import Program
                    new_program = Program()
                    new_program.from_dict(self._clipboard_data)
                    new_program.id = f"program_{uuid.uuid4().hex[:12]}"
                    new_program.name = f"{new_program.name}_Copy"
                    for element in new_program.elements:
                        element["id"] = f"element_{uuid.uuid4().hex[:12]}"
                    target_screen.add_program(new_program)
                    self.screen_manager.add_program_to_screen(target_screen_name, new_program)
                    self.refresh_screens(debounce=False)
            elif item_type == "program":
                target_program_id = current_item.data(0, Qt.UserRole + 1)
                target_program = self.screen_manager.get_program_by_id(target_program_id)
                if target_program:
                    screen = None
                    for s in self.screen_manager.screens:
                        if target_program in s.programs:
                            screen = s
                            break
                    if screen:
                        import uuid
                        from core.program_manager import Program
                        new_program = Program()
                        new_program.from_dict(self._clipboard_data)
                        new_program.id = f"program_{uuid.uuid4().hex[:12]}"
                        new_program.name = f"{new_program.name}_Copy"
                        for element in new_program.elements:
                            element["id"] = f"element_{uuid.uuid4().hex[:12]}"
                        program_index = screen.programs.index(target_program)
                        screen.programs.insert(program_index + 1, new_program)
                        self.screen_manager.add_program_to_screen(screen.name, new_program)
                        self.refresh_screens(debounce=False)
        elif self._clipboard_type == "content" and item_type == "program":
            target_program_id = current_item.data(0, Qt.UserRole + 1)
            target_program = self.screen_manager.get_program_by_id(target_program_id)
            if target_program:
                import uuid
                import copy
                new_element = copy.deepcopy(self._clipboard_data)
                new_element["id"] = f"element_{uuid.uuid4().hex[:12]}"
                new_element["name"] = f"{new_element.get('name', 'Element')}_Copy"
                target_program.elements.append(new_element)
                target_program.modified = datetime.now().isoformat()
                self.refresh_screens(debounce=False)
    
    def on_delete_clicked(self):
        current_item = self.tree.currentItem()
        if not current_item or not self.screen_manager:
            return
        
        item_type = current_item.data(0, Qt.UserRole)
        
        if item_type == "screen":
            screen_name = current_item.data(0, Qt.UserRole + 1)
            self.screen_deleted.emit(screen_name)
        elif item_type == "program":
            program_id = current_item.data(0, Qt.UserRole + 1)
            self.delete_program_requested.emit(program_id)
        elif item_type == "content":
            program_id = current_item.data(0, Qt.UserRole + 1)
            element_id = current_item.data(0, Qt.UserRole + 2)
            self.delete_content_requested.emit(program_id, element_id)
    
    def on_move_up(self):
        current_item = self.tree.currentItem()
        if not current_item or not self.screen_manager:
            return
        
        item_type = current_item.data(0, Qt.UserRole)
        
        if item_type == "program":
            program_id = current_item.data(0, Qt.UserRole + 1)
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                for screen in self.screen_manager.screens:
                    if program in screen.programs:
                        index = screen.programs.index(program)
                        if index > 0:
                            screen.programs[index], screen.programs[index - 1] = screen.programs[index - 1], screen.programs[index]
                            self.refresh_screens(debounce=False)
                        break
        elif item_type == "content":
            program_id = current_item.data(0, Qt.UserRole + 1)
            element_id = current_item.data(0, Qt.UserRole + 2)
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                element = next((e for e in program.elements if e.get("id") == element_id), None)
                if element:
                    index = program.elements.index(element)
                    if index > 0:
                        program.elements[index], program.elements[index - 1] = program.elements[index - 1], program.elements[index]
                        program.modified = datetime.now().isoformat()
                        self.refresh_screens(debounce=False)
    
    def on_move_down(self):
        current_item = self.tree.currentItem()
        if not current_item or not self.screen_manager:
            return
        
        item_type = current_item.data(0, Qt.UserRole)
        
        if item_type == "program":
            program_id = current_item.data(0, Qt.UserRole + 1)
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                for screen in self.screen_manager.screens:
                    if program in screen.programs:
                        index = screen.programs.index(program)
                        if index < len(screen.programs) - 1:
                            screen.programs[index], screen.programs[index + 1] = screen.programs[index + 1], screen.programs[index]
                            self.refresh_screens(debounce=False)
                        break
        elif item_type == "content":
            program_id = current_item.data(0, Qt.UserRole + 1)
            element_id = current_item.data(0, Qt.UserRole + 2)
            program = self.screen_manager.get_program_by_id(program_id)
            if program:
                element = next((e for e in program.elements if e.get("id") == element_id), None)
                if element:
                    index = program.elements.index(element)
                    if index < len(program.elements) - 1:
                        program.elements[index], program.elements[index + 1] = program.elements[index + 1], program.elements[index]
                        program.modified = datetime.now().isoformat()
                        self.refresh_screens(debounce=False)
    
    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        if self._refreshing:
            return
        
        if item is None:
            return
        
        item_type = item.data(0, Qt.UserRole) # type: ignore
        
        if item_type == "program":
            text = item.text(0)
            new_name = text.replace("💽 ", "").strip()
            if new_name:
                program_id = item.data(0, Qt.UserRole + 1) # type: ignore
                self.program_renamed.emit(program_id, new_name)
        elif item_type == "content":
            text = item.text(0)
            parts = text.split(" ", 1)
            if len(parts) > 1:
                new_name = parts[1]
                program_id = item.data(0, Qt.UserRole + 1) #type: ignore
                element_id = item.data(0, Qt.UserRole + 2) #type: ignore
                self.content_renamed.emit(program_id, element_id, new_name)
    
    def _get_selected_screen_item(self):
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
        
        if self.tree.topLevelItemCount() > 0:
            return self.tree.topLevelItem(0)
        return None
    

