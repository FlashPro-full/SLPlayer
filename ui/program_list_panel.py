"""
Program list panel with checkboxes for multi-selection
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QToolButton, QHBoxLayout, QCheckBox, QMenu)
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QTimer
from PyQt5.QtGui import QMouseEvent, QContextMenuEvent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.program_manager import ProgramManager

from core.program_manager import ProgramManager
from config.i18n import tr


class ProgramListPanel(QWidget):
    """Program list panel with management tools and checkboxes"""
    
    program_selected = pyqtSignal(str)
    screen_selected = pyqtSignal(str)
    new_program_requested = pyqtSignal()
    delete_program_requested = pyqtSignal(str)
    program_renamed = pyqtSignal(str, str)
    program_duplicated = pyqtSignal(str)
    program_moved = pyqtSignal(str, int)
    program_activated = pyqtSignal(str, bool)
    program_checked = pyqtSignal(str, bool)
    
    screen_renamed = pyqtSignal(str, str)
    screen_deleted = pyqtSignal(str)
    new_screen_requested = pyqtSignal()
    add_program_requested = pyqtSignal(str)
    screen_insert_requested = pyqtSignal(str)
    screen_download_requested = pyqtSignal(str)
    screen_close_requested = pyqtSignal(str)
    screen_paste_requested = pyqtSignal(str)
    
    program_copy_requested = pyqtSignal(str)
    program_paste_requested = pyqtSignal(str)
    program_add_content_requested = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program_manager: ProgramManager = None
        self._refreshing = False
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
        self.select_all_checkbox.setToolTip("Select/Deselect all programs in selected screen")
        self.select_all_checkbox.setTristate(True)
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        self.select_all_checkbox.setStyleSheet("""
            QCheckBox {
                margin-top: 2px;
            }
        """)
        toolbar_layout.addWidget(self.select_all_checkbox)
        
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
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        self._original_mouse_press_event = self.tree.mousePressEvent
        self.tree.mousePressEvent = self._tree_mouse_press_event
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
        layout.addWidget(self.tree, stretch=1)
    
    def refresh_texts(self):
        """Refresh localized tooltips/texts."""
        self.copy_btn.setToolTip("Copy")
        self.paste_btn.setToolTip("Paste")
        self.up_btn.setToolTip(tr("program_list.move_up"))
        self.down_btn.setToolTip(tr("program_list.move_down"))
        self.close_btn.setToolTip(tr("program_list.delete"))
    
    def refresh_programs(self):
        """Refresh the program list with performance optimizations"""
        if not self.program_manager:
            return
        
        # Use throttling to avoid excessive refreshes
        if hasattr(self, '_refresh_timer'):
            self._refresh_timer.stop()
        
        # Schedule refresh with small delay to batch multiple calls
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_refresh_programs)
        self._refresh_timer.start(50)  # 50ms debounce
    
    def _do_refresh_programs(self):
        """Internal method to perform the actual refresh"""
        if not self.program_manager:
            return
        
        current_program_id = None
        if self.program_manager.current_program:
            current_program_id = self.program_manager.current_program.id
        
        self._refreshing = True
        self.tree.blockSignals(True)
        
        # Use cache for screen name lookups
        from core.screen_manager import ScreenManager
        from core.cache import cache
        
        # Check if we can use cached screen structure
        programs_hash = hash(tuple(p.id for p in self.program_manager.programs))
        cache_key = f"program_list_structure:{programs_hash}"
        cached_structure = cache.get(cache_key)
        
        if cached_structure and cached_structure.get('programs_hash') == programs_hash:
            # Use cached structure
            screens = cached_structure.get('screens', {})
        else:
            # Build screen structure
            screens = {}
            for program in self.program_manager.programs:
                # Use ScreenManager to get screen name - handles all cases properly
                screen_name = ScreenManager.get_screen_name_from_program(program)
                
                if screen_name not in screens:
                    screens[screen_name] = []
                screens[screen_name].append(program)
            
            # Cache the structure
            cache.set(cache_key, {
                'screens': screens,
                'programs_hash': programs_hash
            }, ttl=60)  # Cache for 60 seconds
        
        # Clear and rebuild tree
        self.tree.clear()
        
        current_item = None
        for screen_name, programs in screens.items():
            screen_item = QTreeWidgetItem(self.tree)
            screen_item.setText(0, f"🖥 {screen_name}")
            screen_item.setData(0, Qt.UserRole, None)
            screen_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            
            for program in programs:
                program_item = QTreeWidgetItem(screen_item)
                is_activated = program.properties.get("activation", {}).get("enabled", True)
                program.properties["checked"] = True
                is_checked = True
                program_item.setText(0, f"💽 {program.name}")
                program_item.setData(0, Qt.UserRole, program.id)
                program_item.setData(0, Qt.UserRole + 1, is_checked)
                program_item.setCheckState(0, Qt.Checked)
                program_item.setFlags(program_item.flags() | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
                program_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicator)
                
                if program.id == current_program_id:
                    current_item = program_item
        
        self.tree.expandAll()
        self.tree.blockSignals(False)
        self._refreshing = False
        
        if not current_item and self.program_manager.programs:
            first_program = self.program_manager.programs[0]
            for i in range(self.tree.topLevelItemCount()):
                screen_item = self.tree.topLevelItem(i)
                for j in range(screen_item.childCount()):
                    program_item = screen_item.child(j)
                    if program_item.data(0, Qt.UserRole) == first_program.id:
                        current_item = program_item
                        break
                if current_item:
                    break
        
        if current_item:
            self.tree.setCurrentItem(current_item)
            current_item.setSelected(True)
            self.tree.scrollToItem(current_item)
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                QTimer.singleShot(10, lambda pid=program_id: self.program_selected.emit(pid))
        
        self._update_select_all_checkbox()
    
    def _tree_mouse_press_event(self, event: QMouseEvent):
        """Custom mouse press event to handle arrow clicks for screen items"""
        item = self.tree.itemAt(event.pos())
        if item:
            program_id = item.data(0, Qt.UserRole)
            if not program_id:
                visual_rect = self.tree.visualItemRect(item)
                indent = self.tree.indentation()
                arrow_width = indent + 10
                item_x = visual_rect.x()
                click_x = event.pos().x()
                if click_x >= item_x and click_x <= item_x + arrow_width:
                    self._original_mouse_press_event(event)
                else:
                    self.tree.setCurrentItem(item)
                    item.setSelected(True)
                    self.tree.scrollToItem(item)
                    screen_name = item.text(0).replace("🖥 ", "")
                    self.screen_selected.emit(screen_name)
                    return
            else:
                self._original_mouse_press_event(event)
        else:
            self._original_mouse_press_event(event)
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        if item is None:
            return
        
        program_id = item.data(0, Qt.UserRole)
        if program_id:
            self.tree.setCurrentItem(item)
            item.setSelected(True)
            self.tree.scrollToItem(item)
            self.program_selected.emit(program_id)
            self._update_select_all_checkbox()
        else:
            self.tree.setCurrentItem(item)
            item.setSelected(True)
            self.tree.scrollToItem(item)
            screen_name = item.text(0).replace("🖥 ", "")
            self.screen_selected.emit(screen_name)
    
    def _on_context_menu(self, position: QPoint):
        """Handle context menu request"""
        item = self.tree.itemAt(position)
        if item is None:
            return
        
        program_id = item.data(0, Qt.UserRole)
        if program_id:
            menu = QMenu(self)
            
            rename_action = menu.addAction("📝 Rename")
            rename_action.triggered.connect(lambda: self._on_program_rename_context(program_id))
            
            delete_action = menu.addAction("❌ Delete")
            delete_action.triggered.connect(lambda: self._on_program_delete_context(program_id))
            
            menu.addSeparator()
            
            add_program_action = menu.addAction("💽 Add Program")
            add_program_action.triggered.connect(lambda: self._on_program_add_program(program_id))
            
            menu.addSeparator()
            
            add_text_action = menu.addAction("🔠 Add Text")
            add_text_action.triggered.connect(lambda: self._on_program_add_content(program_id, "text"))
            
            add_singleline_action = menu.addAction("🔤 Add SingleLineText")
            add_singleline_action.triggered.connect(lambda: self._on_program_add_content(program_id, "singleline_text"))
            
            add_animation_action = menu.addAction("🎇 Add Animation")
            add_animation_action.triggered.connect(lambda: self._on_program_add_content(program_id, "animation"))
            
            add_clock_action = menu.addAction("🕓 Add Clock")
            add_clock_action.triggered.connect(lambda: self._on_program_add_content(program_id, "clock"))
            
            add_calendar_action = menu.addAction("🗓 Add Calendar")
            add_calendar_action.triggered.connect(lambda: self._on_program_add_content(program_id, "calendar"))
            
            add_timing_action = menu.addAction("⌛️ Add Timing")
            add_timing_action.triggered.connect(lambda: self._on_program_add_content(program_id, "timing"))
            
            add_html_action = menu.addAction("🌐 Add HTML")
            add_html_action.triggered.connect(lambda: self._on_program_add_content(program_id, "html"))
            
            add_livestream_action = menu.addAction("🎥 LiveStream")
            add_livestream_action.triggered.connect(lambda: self._on_program_add_content(program_id, "livestream"))
            
            add_weather_action = menu.addAction("🌦 Add Weather")
            add_weather_action.triggered.connect(lambda: self._on_program_add_content(program_id, "weather"))
            
            add_neon_action = menu.addAction("🪄 Add Neon")
            add_neon_action.triggered.connect(lambda: self._on_program_add_content(program_id, "neon"))
            
            add_qrcode_action = menu.addAction("🧿 QR code")
            add_qrcode_action.triggered.connect(lambda: self._on_program_add_content(program_id, "qrcode"))
            
            add_digitalwatch_action = menu.addAction("📟 Digital Watch")
            add_digitalwatch_action.triggered.connect(lambda: self._on_program_add_content(program_id, "digital_watch"))
            
            menu.addSeparator()
            
            copy_action = menu.addAction("📑 Copy")
            copy_action.triggered.connect(lambda: self._on_program_copy(program_id))
            
            paste_action = menu.addAction("📋 Paste")
            paste_action.triggered.connect(lambda: self._on_program_paste(program_id))
            
            menu.exec_(self.tree.mapToGlobal(position))
        else:
            screen_name = item.text(0).replace("🖥 ", "")
            
            menu = QMenu(self)
            
            rename_action = menu.addAction("📝 Rename")
            rename_action.triggered.connect(lambda: self._on_screen_rename(screen_name))
            
            delete_action = menu.addAction("❌ Delete")
            delete_action.triggered.connect(lambda: self._on_screen_delete(screen_name))
            
            menu.addSeparator()
            
            new_screen_action = menu.addAction("🖥 New screen")
            new_screen_action.triggered.connect(self._on_new_screen)
            
            add_program_action = menu.addAction("💽 Add program")
            add_program_action.triggered.connect(lambda: self._on_add_program(screen_name))
            
            insert_action = menu.addAction("📲 Insert")
            insert_action.triggered.connect(lambda: self._on_screen_insert(screen_name))
            
            download_action = menu.addAction("⬇️ Download")
            download_action.triggered.connect(lambda: self._on_screen_download(screen_name))
            
            close_action = menu.addAction("✖️ Close")
            close_action.triggered.connect(lambda: self._on_screen_close(screen_name))
            
            paste_action = menu.addAction("📋 Paste")
            paste_action.triggered.connect(lambda: self._on_screen_paste(screen_name))
            
            menu.exec_(self.tree.mapToGlobal(position))
    
    def _on_screen_rename(self, screen_name: str):
        """Handle screen rename from context menu"""
        self.screen_renamed.emit(screen_name, "")
    
    def _on_screen_delete(self, screen_name: str):
        """Handle screen delete from context menu"""
        self.screen_deleted.emit(screen_name)
    
    def _on_new_screen(self):
        """Handle new screen from context menu"""
        self.new_screen_requested.emit()
    
    def _on_add_program(self, screen_name: str):
        """Handle add program from context menu"""
        self.add_program_requested.emit(screen_name)
    
    def _on_screen_insert(self, screen_name: str):
        """Handle screen insert from context menu"""
        self.screen_insert_requested.emit(screen_name)
    
    def _on_screen_download(self, screen_name: str):
        """Handle screen download from context menu"""
        self.screen_download_requested.emit(screen_name)
    
    def _on_screen_close(self, screen_name: str):
        """Handle screen close from context menu"""
        self.screen_close_requested.emit(screen_name)
    
    def _on_screen_paste(self, screen_name: str):
        """Handle screen paste from context menu"""
        self.screen_paste_requested.emit(screen_name)
    
    def _on_program_rename_context(self, program_id: str):
        """Handle program rename from context menu"""
        if self.program_manager:
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                from PyQt5.QtWidgets import QInputDialog
                new_name, ok = QInputDialog.getText(self, "Rename Program", "Enter new program name:", text=program.name)
                if ok and new_name:
                    self.program_renamed.emit(program_id, new_name)
    
    def _on_program_delete_context(self, program_id: str):
        """Handle program delete from context menu"""
        self.delete_program_requested.emit(program_id)
    
    def _on_program_add_program(self, program_id: str):
        """Handle add program from program context menu"""
        self.new_program_requested.emit()
    
    def _on_program_add_content(self, program_id: str, content_type: str):
        """Handle add content from program context menu"""
        self.program_add_content_requested.emit(program_id, content_type)
    
    def _on_program_copy(self, program_id: str):
        """Handle program copy from context menu"""
        self.program_copy_requested.emit(program_id)
    
    def _on_program_paste(self, program_id: str):
        """Handle program paste from context menu"""
        self.program_paste_requested.emit(program_id)
    
    def on_copy_clicked(self):
        """Handle copy button click"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                self.program_copy_requested.emit(program_id)
    
    def on_paste_clicked(self):
        """Handle paste button click"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                self.program_paste_requested.emit(program_id)
    
    def on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                self.delete_program_requested.emit(program_id)
    
    def on_checkbox_toggled(self, checked: bool):
        """Handle checkbox toggle"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                self.program_activated.emit(program_id, checked)
        
        if checked:
            self.check_btn.setText("☑️")
        else:
            self.check_btn.setText("⬜️")
    
    def on_select_all_changed(self, state):
        """Handle select all checkbox - only affects programs in the selected screen"""
        screen_item = self._get_selected_screen_item()
        if not screen_item:
            return
        
        checked_count = 0
        total_count = 0
        for j in range(screen_item.childCount()):
            program_item = screen_item.child(j)
            program_id = program_item.data(0, Qt.UserRole)
            if program_id:
                total_count += 1
                if program_item.checkState(0) == Qt.Checked:
                    checked_count += 1
        
        if total_count == 0:
            return
        
        if state == Qt.PartiallyChecked:
            checked = (checked_count == 0)
        else:
            checked = (state == Qt.Checked)
        
        self.tree.blockSignals(True)
        self.select_all_checkbox.blockSignals(True)
        for j in range(screen_item.childCount()):
            program_item = screen_item.child(j)
            program_id = program_item.data(0, Qt.UserRole)
            if program_id:
                program_item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
                program_item.setData(0, Qt.UserRole + 1, checked)
        self.select_all_checkbox.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.select_all_checkbox.blockSignals(False)
        self.tree.blockSignals(False)
        
        if not self._refreshing:
            for j in range(screen_item.childCount()):
                program_item = screen_item.child(j)
                program_id = program_item.data(0, Qt.UserRole)
                if program_id:
                    self.program_checked.emit(program_id, checked)
    
    def on_duplicate_program(self):
        """Handle duplicate program"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                self.program_duplicated.emit(program_id)
    
    def on_move_up(self):
        """Handle move program up"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                self.program_moved.emit(program_id, -1)
    
    def on_move_down(self):
        """Handle move program down"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.UserRole)
            if program_id:
                self.program_moved.emit(program_id, 1)
    
    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item change (rename or checkbox)"""
        if self._refreshing:
            return
        
        if item is None:
            return
        
        program_id = item.data(0, Qt.UserRole)
        if not program_id:
            return
        
        if column == 0:
            checked = (item.checkState(0) == Qt.Checked)
            old_checked = item.data(0, Qt.UserRole + 1)
            if old_checked is None or old_checked != checked:
                self.tree.blockSignals(True)
                item.setData(0, Qt.UserRole + 1, checked)
                self.tree.blockSignals(False)
                self.program_checked.emit(program_id, checked)
                self._update_select_all_checkbox()
            else:
                text = item.text(0)
                new_name = text.replace("☑ ", "").replace("⬜ ", "").replace("✓ ", "").replace("▶ ", "").strip()
                if new_name:
                    self.program_renamed.emit(program_id, new_name)
    
    def _get_selected_screen_item(self):
        """Get the screen item that contains the currently selected program, or the first expanded screen"""
        current_item = self.tree.currentItem()
        if current_item:
            parent = current_item.parent()
            if parent:
                return parent
            elif current_item.data(0, Qt.UserRole) is None:
                return current_item
        
        for i in range(self.tree.topLevelItemCount()):
            screen_item = self.tree.topLevelItem(i)
            if screen_item.isExpanded() or screen_item.childCount() > 0:
                return screen_item
        
        if self.tree.topLevelItemCount() > 0:
            return self.tree.topLevelItem(0)
        return None
    
    def _update_select_all_checkbox(self):
        """Update the select all checkbox based on the state of programs in the selected screen"""
        screen_item = self._get_selected_screen_item()
        if not screen_item:
            self.select_all_checkbox.blockSignals(True)
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
            self.select_all_checkbox.blockSignals(False)
            return
        
        checked_count = 0
        total_count = 0
        for j in range(screen_item.childCount()):
            program_item = screen_item.child(j)
            program_id = program_item.data(0, Qt.UserRole)
            if program_id:
                total_count += 1
                if program_item.checkState(0) == Qt.Checked:
                    checked_count += 1
        
        self.select_all_checkbox.blockSignals(True)
        if total_count == 0:
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif checked_count == 0:
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif checked_count == total_count:
            self.select_all_checkbox.setCheckState(Qt.Checked)
        else:
            self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        self.select_all_checkbox.blockSignals(False)

