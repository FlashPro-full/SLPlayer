from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QToolButton, QHBoxLayout, QCheckBox, QMenu, QInputDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QTimer, QEvent
from PyQt5.QtGui import QMouseEvent, QContextMenuEvent, QKeyEvent
from typing import TYPE_CHECKING, Optional, Dict, List
from datetime import datetime

if TYPE_CHECKING:
    from core.screen_manager import ScreenManager

from core.screen_manager import ScreenManager, Screen
from core.screen_config import get_controller_display_name, get_screen_name, set_screen_name
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
    program_checked = pyqtSignal(str, bool)
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
        self.init_ui()
    
    def set_screen_manager(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager
        self.refresh_screens()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
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
        
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.setToolTip(tr("program_list.select_all_tooltip"))
        self.select_all_checkbox.setTristate(True)
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        self.select_all_checkbox.setStyleSheet("""
            QCheckBox {
                margin-top: 2px;
            }
        """)
        toolbar_layout.addWidget(self.select_all_checkbox)
        
        TOOL_BUTTON_STYLE = """
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
        """
        
        self.copy_btn = self._create_tool_button("📑", tr("program_list.copy"), self.on_copy_clicked, TOOL_BUTTON_STYLE)
        toolbar_layout.addWidget(self.copy_btn)
        
        self.paste_btn = self._create_tool_button("📋", tr("program_list.paste"), self.on_paste_clicked, TOOL_BUTTON_STYLE)
        toolbar_layout.addWidget(self.paste_btn)
        
        self.up_btn = self._create_tool_button("🔼", tr("program_list.move_up"), self.on_move_up, TOOL_BUTTON_STYLE)
        toolbar_layout.addWidget(self.up_btn)
        
        self.down_btn = self._create_tool_button("🔽", tr("program_list.move_down"), self.on_move_down, TOOL_BUTTON_STYLE)
        toolbar_layout.addWidget(self.down_btn)
        
        self.close_btn = self._create_tool_button("❌", tr("program_list.delete"), self.on_delete_clicked, TOOL_BUTTON_STYLE)
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
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.on_copy_clicked
            event.accept()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.on_paste_clicked()
            event.accept()
        elif event.key() == Qt.Key_Delete:
            self.on_delete_clicked()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def refresh_screens(self, debounce: bool = True):
        if not self.screen_manager:
            return
        
        if debounce:
            if hasattr(self, '_refresh_timer'):
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
        
        self._update_select_all_checkbox()
    
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
            item_type = item.data(0, Qt.UserRole)
            
            if item_type == "screen":
                screen_name = item.data(0, Qt.UserRole + 1)
                self._last_selected_screen = screen_name
                self._last_selected_program = None
                self._last_selected_content = None
                set_screen_name(screen_name)
                self.screen_selected.emit(screen_name)
                self._update_select_all_checkbox()
            elif item_type == "program":
                program_id = item.data(0, Qt.UserRole + 1)
                self._last_selected_program = program_id
                self._last_selected_content = None
                parent = item.parent()
                if parent:
                    parent_screen_name = parent.data(0, Qt.UserRole + 1)
                    if parent_screen_name:
                        self._last_selected_screen = parent_screen_name
                        set_screen_name(parent_screen_name)
                else:
                    self._last_selected_screen = None
                self.program_selected.emit(program_id)
                self._update_select_all_checkbox()
            elif item_type == "content":
                program_id = item.data(0, Qt.UserRole + 1)
                element_id = item.data(0, Qt.UserRole + 2)
                self._last_selected_content = (program_id, element_id)
                self._last_selected_program = None
                parent = item.parent()
                if parent:
                    parent_parent = parent.parent()
                    if parent_parent:
                        parent_screen_name = parent_parent.data(0, Qt.UserRole + 1)
                        if parent_screen_name:
                            self._last_selected_screen = parent_screen_name
                            set_screen_name(parent_screen_name)
                    else:
                        self._last_selected_screen = None
                else:
                    self._last_selected_screen = None
                self.content_selected.emit(program_id, element_id)
                self._update_select_all_checkbox()
        except Exception as e:
            pass
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        if item is None:
            return
        
        item_type = item.data(0, Qt.UserRole)
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
        
        item_type = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        
        if item_type == "screen":
            screen_name = item.data(0, Qt.UserRole + 1)
            
            rename_action = menu.addAction(tr("program_list.rename"))
            rename_action.triggered.connect(lambda: self._on_screen_rename(screen_name))
            
            delete_action = menu.addAction(tr("program_list.delete"))
            delete_action.triggered.connect(lambda: self._on_screen_delete(screen_name))
            
            menu.addSeparator()
            
            new_screen_action = menu.addAction(tr("program_list.new_screen"))
            new_screen_action.triggered.connect(self._on_new_screen)
            
            add_program_action = menu.addAction(tr("program_list.add_program"))
            add_program_action.triggered.connect(lambda: self._on_add_program(screen_name))
            
            insert_action = menu.addAction(tr("program_list.insert"))
            insert_action.triggered.connect(lambda: self._on_screen_insert(screen_name))
            
            close_action = menu.addAction(tr("program_list.close"))
            close_action.triggered.connect(lambda: self._on_screen_close(screen_name))
        else:
            rename_action = menu.addAction(tr("program_list.rename"))
            delete_action = menu.addAction(tr("program_list.delete"))
            
            if item_type == "program":
                program_id = item.data(0, Qt.UserRole + 1)
                rename_action.triggered.connect(lambda: self._on_program_rename(program_id))
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
                    action.triggered.connect(lambda checked, pid=program_id, ct=content_type: 
                                           self.content_add_requested.emit(pid, ct))
                
                menu.addSeparator()
                
                copy_action = menu.addAction(tr("program_list.copy"))
                copy_action.triggered.connect(lambda: self.program_copy_requested.emit(program_id))
            else:  # content
                program_id = item.data(0, Qt.UserRole + 1)
                element_id = item.data(0, Qt.UserRole + 2)
                rename_action.triggered.connect(lambda: self._on_content_rename(program_id, element_id))
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
                    action.triggered.connect(lambda checked, pid=program_id, ct=content_type: 
                                           self.content_add_requested.emit(pid, ct))
                
                menu.addSeparator()
                
                copy_action = menu.addAction(tr("program_list.copy"))
                copy_action.triggered.connect(lambda: self.program_copy_requested.emit(program_id))
        
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
            return
        from core.screen_config import get_screen_config, get_controller_display_name
        config = get_screen_config()
        width = config.get("width", 640) if config else 640
        height = config.get("height", 480) if config else 480
        
        controller_name = get_controller_display_name()
        if controller_name:
            screen_name = controller_name
        else:
            screen_name = "New Screen"
        
        screen = self.screen_manager.create_screen(screen_name, width, height)
        from core.screen_config import set_screen_name
        set_screen_name(screen.name)
        self.refresh_screens(debounce=False)
    
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
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_copy_requested.emit(program_id)
    
    def on_paste_clicked(self):
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_paste_requested.emit(program_id)
    
    def on_delete_clicked(self):
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
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_moved.emit(program_id, -1)
    
    def on_move_down(self):
        current_item = self.tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "program":
                program_id = current_item.data(0, Qt.UserRole + 1)
                self.program_moved.emit(program_id, 1)
    
    def on_item_changed(self, item: QTreeWidgetItem, column: int):
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
                
                if self.screen_manager:
                    program_id = item.data(0, Qt.UserRole + 1)
                    program = self.screen_manager.get_program_by_id(program_id)
                    if program:
                        program.properties["checked"] = checked
                
                program_id = item.data(0, Qt.UserRole + 1)
                self.program_checked.emit(program_id, checked)
                self._update_select_all_checkbox()
            else:
                text = item.text(0)
                new_name = text.replace("💽 ", "").strip()
                if new_name:
                    program_id = item.data(0, Qt.UserRole + 1)
                    self.program_renamed.emit(program_id, new_name)
        elif item_type == "content":
            text = item.text(0)
            parts = text.split(" ", 1)
            if len(parts) > 1:
                new_name = parts[1]
                program_id = item.data(0, Qt.UserRole + 1)
                element_id = item.data(0, Qt.UserRole + 2)
                self.content_renamed.emit(program_id, element_id, new_name)
    
    def on_select_all_changed(self, state):
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        checked = (state == Qt.Checked)
        item_type = current_item.data(0, Qt.UserRole)
        
        self.tree.blockSignals(True)
        self.select_all_checkbox.blockSignals(True)
        
        if item_type == "program":
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
    
    def _update_select_all_checkbox(self):
        current_item = self.tree.currentItem()
        if not current_item:
            self.select_all_checkbox.blockSignals(True)
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
            self.select_all_checkbox.blockSignals(False)
            return
        
        item_type = current_item.data(0, Qt.UserRole)
        self.select_all_checkbox.blockSignals(True)
        
        if item_type == "program":
            program_item = current_item
            if program_item.checkState(0) == Qt.Checked:
                self.select_all_checkbox.setCheckState(Qt.Checked)
            else:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif item_type == "screen":
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
            program_item = current_item.parent()
            if program_item and program_item.data(0, Qt.UserRole) == "program":
                if program_item.checkState(0) == Qt.Checked:
                    self.select_all_checkbox.setCheckState(Qt.Checked)
                else:
                    self.select_all_checkbox.setCheckState(Qt.Unchecked)
            else:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
        
        self.select_all_checkbox.blockSignals(False)

