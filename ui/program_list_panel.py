"""
Left sidebar - Program list panel
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QToolButton, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QFont
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.program_manager import ProgramManager

from core.program_manager import ProgramManager


class ProgramListPanel(QWidget):
    """Program list panel with management tools"""
    
    program_selected = pyqtSignal(str)
    new_program_requested = pyqtSignal()
    delete_program_requested = pyqtSignal(str)
    program_renamed = pyqtSignal(str, str)  # Emits old_id, new_name
    program_duplicated = pyqtSignal(str)  # Emits program_id
    program_moved = pyqtSignal(str, int)  # Emits program_id, direction (-1 up, 1 down)
    program_activated = pyqtSignal(str, bool)  # Emits program_id, enabled
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program_manager: ProgramManager = None
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
        
        # Toolbar at the top
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet("""
            QWidget {
                background-color: #D6D6D6;
                border-top: 1px solid #777777;
                border-bottom: 1px solid #777777;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(2)
        
        # Add stretch to push buttons to the right
        toolbar_layout.addStretch()
        
        # Toolbar buttons
        self.check_btn = QToolButton()
        self.check_btn.setCheckable(True)
        self.check_btn.setChecked(True)  # Default checked state
        self.check_btn.setText("☑️")  # Checked emoji
        self.check_btn.toggled.connect(self.on_checkbox_toggled)
        self.check_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #C5C5C5;
            }
        """)
        toolbar_layout.addWidget(self.check_btn)
        
        self.doc_btn = QToolButton()
        self.doc_btn.setText("📑")
        self.doc_btn.setToolTip("New")
        self.doc_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #C5C5C5;
            }
        """)
        self.doc_btn.clicked.connect(self.new_program_requested.emit)
        toolbar_layout.addWidget(self.doc_btn)
        
        self.docs_btn = QToolButton()
        self.docs_btn.setText("📋")
        self.docs_btn.setToolTip("Duplicate")
        self.docs_btn.clicked.connect(self.on_duplicate_program)
        self.docs_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #C5C5C5;
            }
        """)
        toolbar_layout.addWidget(self.docs_btn)
        
        self.up_btn = QToolButton()
        self.up_btn.setText("🔼")
        self.up_btn.setToolTip("Move Up")
        self.up_btn.clicked.connect(self.on_move_up)
        self.up_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #C5C5C5;
            }
        """)
        toolbar_layout.addWidget(self.up_btn)
        
        self.down_btn = QToolButton()
        self.down_btn.setText("🔽")
        self.down_btn.setToolTip("Move Down")
        self.down_btn.clicked.connect(self.on_move_down)
        self.down_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #C5C5C5;
            }
        """)
        toolbar_layout.addWidget(self.down_btn)
        
        self.close_btn = QToolButton()
        self.close_btn.setText("❌")
        self.close_btn.setToolTip("Delete")
        self.close_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 1px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #C5C5C5;
            }
        """)
        self.close_btn.clicked.connect(self.on_delete_clicked)
        toolbar_layout.addWidget(self.close_btn)
        
        layout.addWidget(toolbar_widget)
        
        # Program tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)  # Hide header to remove "Programs" text
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
                background-color: #E0E0E0;
                color: #000000;
            }
            QTreeWidget::item:hover {
                background-color: #F5F5F5;
            }
            QTreeWidget::branch {
                background-color: #FFFFFF;
            }
            QTreeWidget::branch:has-siblings:!adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:has-siblings:adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:has-children:!expanded:adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
            }
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
            }
        """)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree, stretch=1)
    
    def refresh_programs(self):
        """Refresh the program list"""
        if not self.program_manager:
            return
        
        self.tree.clear()
        
        # Group programs by screen (for now, create sample screens)
        # In a real implementation, this would come from the program manager
        screens = {}
        for program in self.program_manager.programs:
            # For now, assign to Screen4 or Screen5 based on program ID
            screen_name = "Screen4" if hash(program.id) % 2 == 0 else "Screen5"
            if screen_name not in screens:
                screens[screen_name] = []
            screens[screen_name].append(program)
        
        # Create screen items with monitor icons
        for screen_name, programs in screens.items():
            screen_item = QTreeWidgetItem(self.tree)
            screen_item.setText(0, f"🖥 {screen_name}")
            screen_item.setData(0, Qt.ItemDataRole.UserRole, None)  # Screen items don't have program IDs
            screen_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            
            # Add program items under each screen
            for program in programs:
                program_item = QTreeWidgetItem(screen_item)
                # Check if program is activated
                is_activated = program.properties.get("activation", {}).get("enabled", True)
                checkbox = "☑" if is_activated else "⬜"
                program_item.setText(0, f"{checkbox} ▶ {program.name}")
                program_item.setData(0, Qt.ItemDataRole.UserRole, program.id)
                program_item.setFlags(program_item.flags() | Qt.ItemFlag.ItemIsEditable)
                program_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicator)
                # Connect item changed for rename - use a closure to capture the item
                def make_handler(item):
                    return lambda: self.on_item_changed(item)
                program_item.itemChanged.connect(make_handler(program_item))
        
        # Expand all items
        self.tree.expandAll()
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        program_id = item.data(0, Qt.ItemDataRole.UserRole)
        if program_id:
            self.program_selected.emit(program_id)
    
    def on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if program_id:
                self.delete_program_requested.emit(program_id)
    
    def on_checkbox_toggled(self, checked: bool):
        """Handle checkbox toggle"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if program_id:
                self.program_activated.emit(program_id, checked)
        
        if checked:
            self.check_btn.setText("☑️")
        else:
            self.check_btn.setText("⬜️")
    
    def on_duplicate_program(self):
        """Handle duplicate program"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if program_id:
                self.program_duplicated.emit(program_id)
    
    def on_move_up(self):
        """Handle move program up"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if program_id:
                self.program_moved.emit(program_id, -1)
    
    def on_move_down(self):
        """Handle move program down"""
        current_item = self.tree.currentItem()
        if current_item:
            program_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if program_id:
                self.program_moved.emit(program_id, 1)
    
    def on_item_changed(self, item: QTreeWidgetItem = None):
        """Handle item change (rename)"""
        if item is None:
            item = self.tree.currentItem()
        if item:
            program_id = item.data(0, Qt.ItemDataRole.UserRole)
            if program_id:
                # Extract name from text (remove checkbox and play icon)
                text = item.text(0)
                new_name = text.replace("☑ ", "").replace("⬜ ", "").replace("▶ ", "").strip()
                if new_name:
                    self.program_renamed.emit(program_id, new_name)

