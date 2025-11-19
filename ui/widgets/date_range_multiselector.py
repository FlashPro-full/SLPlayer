"""
Date Range Multi-Selector Component
Allows selecting multiple start date and end date groups
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QDateEdit, QTableWidget,
                             QHeaderView, QAbstractItemView, QFrame,
                             QCheckBox, QSizePolicy)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from typing import List, Dict, Optional


class DateRangeMultiSelector(QWidget):
    """Multi-selector component for selecting multiple date ranges"""
    
    # Signal emitted when date ranges change
    date_ranges_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.date_ranges: List[Dict[str, str]] = []
        self.table_expanded = False
        self._updating_programmatically = False  # Flag to prevent feedback loops
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Clickable selector (shows tags and dropdown arrow)
        self.selector_button = QPushButton()
        self.selector_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #FFFFFF;
                min-height: 32px;
            }
            QPushButton:hover {
                border: 1px solid #4A90E2;
                background-color: #F5F5F5;
            }
            QPushButton:pressed {
                background-color: #E3F2FD;
            }
        """)
        self.selector_button.clicked.connect(self._toggle_table)
        
        selector_layout = QHBoxLayout(self.selector_button)
        selector_layout.setContentsMargins(4, 4, 4, 4)
        selector_layout.setSpacing(8)
        
        # Summary tags container (blue-bordered tags showing date ranges)
        self.tags_container = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(8)
        selector_layout.addWidget(self.tags_container)
        
        # Dropdown arrow
        self.dropdown_arrow = QLabel("▼")
        self.dropdown_arrow.setStyleSheet("color: #666666; font-size: 10px; padding-left: 3px;")
        self.dropdown_arrow.setFixedWidth(20)
        selector_layout.addWidget(self.dropdown_arrow)
        
        layout.addWidget(self.selector_button)
        
        # Date ranges table with add/remove buttons (initially hidden)
        self.table_widget = QWidget()
        self.table_widget.setVisible(False)
        table_container = QHBoxLayout(self.table_widget)
        table_container.setContentsMargins(0, 4, 0, 0)
        
        self.date_table = QTableWidget()
        self.date_table.setColumnCount(3)  # Checkbox, Start date, End date
        self.date_table.setHorizontalHeaderLabels(["", "Start date", "End date"])
        self.date_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.date_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.date_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.date_table.setColumnWidth(0, 30)  # Checkbox column
        self.date_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.date_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.date_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.date_table.verticalHeader().setVisible(False)
        self.date_table.setMinimumHeight(100)
        self.date_table.setMaximumHeight(300)
        self.date_table.setAlternatingRowColors(True)
        self.date_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #FFFFFF;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 0px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 4px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        table_container.addWidget(self.date_table)
        
        # Add/Remove buttons (vertical layout)
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(4)
        
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2E6DA4;
            }
        """)
        self.add_btn.clicked.connect(self._on_add_date_range)
        buttons_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("🗑")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self._on_remove_selected)
        buttons_layout.addWidget(self.remove_btn)
        
        # Select All / Deselect All buttons
        self.select_all_btn = QPushButton("✓ All")
        self.select_all_btn.setFixedSize(30, 30)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        self.select_all_btn.clicked.connect(self._on_select_all)
        buttons_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("✗ All")
        self.deselect_all_btn.setFixedSize(30, 30)
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
            QPushButton:pressed {
                background-color: #6C7A7B;
            }
        """)
        self.deselect_all_btn.clicked.connect(self._on_deselect_all)
        buttons_layout.addWidget(self.deselect_all_btn)
        
        buttons_layout.addStretch()
        table_container.addLayout(buttons_layout)
        
        layout.addWidget(self.table_widget)
        
        # Connect selection model
        self.date_table.selectionModel().currentChanged.connect(self._on_selection_changed)
        
        # Initialize with placeholder
        self._update_tags()
    
    def _toggle_table(self):
        """Toggle table visibility"""
        # Prevent rapid toggles
        if hasattr(self, '_toggle_in_progress') and self._toggle_in_progress:
            return
        
        self._toggle_in_progress = True
        try:
            self.table_expanded = not self.table_expanded
            self.table_widget.setVisible(self.table_expanded)
            
            # Update dropdown arrow
            if self.table_expanded:
                self.dropdown_arrow.setText("▲")
            else:
                self.dropdown_arrow.setText("▼")
        finally:
            # Use QTimer to reset flag after a short delay
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, lambda: setattr(self, '_toggle_in_progress', False))
    
    def _create_date_tag(self, start_date_str, end_date_str):
        """Create a blue-bordered tag showing date range"""
        tag = QFrame()
        tag.setFrameShape(QFrame.Box)
        tag.setStyleSheet("""
            QFrame {
                border: 1px solid #4A90E2;
                border-radius: 4px;
                background-color: transparent;
                padding: 0px;
                min-height: 20px;
            }
        """)
        tag_layout = QHBoxLayout(tag)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(4)
        
        tag_label = QLabel(f"{start_date_str} - {end_date_str}")
        tag_label.setStyleSheet("color: #1976D2; font-size: 11px;")
        tag_layout.addWidget(tag_label)
        
        return tag
    
    def _update_tags(self):
        """Update summary tags based on current date ranges"""
        # Clear existing tags
        while self.tags_layout.count():
            child = self.tags_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create tags for each date range
        for row in range(self.date_table.rowCount()):
            start_widget = self.date_table.cellWidget(row, 1)
            end_widget = self.date_table.cellWidget(row, 2)
            if start_widget and end_widget:
                start_date_str = start_widget.date().toString("yyyy-MM-dd")
                end_date_str = end_widget.date().toString("yyyy-MM-dd")
                tag = self._create_date_tag(start_date_str, end_date_str)
                self.tags_layout.addWidget(tag)
        
        self.tags_layout.addStretch()
        
        # Show selector if there are date ranges, otherwise show placeholder
        if self.date_table.rowCount() > 0:
            self.selector_button.setVisible(True)
            # Update button text if no tags
            if self.tags_layout.count() == 1:  # Only stretch
                placeholder = QLabel("Click to add date ranges")
                placeholder.setStyleSheet("color: #999999; font-style: italic;")
                self.tags_layout.insertWidget(0, placeholder)
        else:
            # Show placeholder when empty
            placeholder = QLabel("Click to add date ranges")
            placeholder.setStyleSheet("color: #999999; font-style: italic;")
            self.tags_layout.insertWidget(0, placeholder)
            self.selector_button.setVisible(True)
    
    def _add_date_range_row(self, start_date_str="", end_date_str="", selected=False):
        """Add a date range row to the table"""
        row = self.date_table.rowCount()
        self.date_table.insertRow(row)
        
        # Parse date strings
        start_date = QDate.currentDate()
        end_date = QDate.currentDate()
        
        if start_date_str:
            parsed_start = QDate.fromString(start_date_str, "yyyy-MM-dd")
            if parsed_start.isValid():
                start_date = parsed_start
        if end_date_str:
            parsed_end = QDate.fromString(end_date_str, "yyyy-MM-dd")
            if parsed_end.isValid():
                end_date = parsed_end
        
        # Checkbox (column 0) - centered in cell
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox = QCheckBox()
        # Block signals during programmatic updates
        if self._updating_programmatically:
            checkbox.blockSignals(True)
        checkbox.setChecked(selected)
        if self._updating_programmatically:
            checkbox.blockSignals(False)
        checkbox.stateChanged.connect(lambda state, r=row: self._on_checkbox_changed(r, state))
        checkbox_layout.addWidget(checkbox)
        self.date_table.setCellWidget(row, 0, checkbox_widget)
        
        # Start date widget (column 1)
        start_date_edit = QDateEdit()
        start_date_edit.setCalendarPopup(True)
        # Block signals during programmatic updates
        if self._updating_programmatically:
            start_date_edit.blockSignals(True)
        start_date_edit.setDate(start_date)
        if self._updating_programmatically:
            start_date_edit.blockSignals(False)
        start_date_edit.dateChanged.connect(lambda date, r=row: self._on_date_range_changed(r))
        start_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        start_date_edit.setStyleSheet("""
            QDateEdit {
                border: none;
                border-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
            QDateEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #FFFFFF;
            }
        """)
        self.date_table.setCellWidget(row, 1, start_date_edit)
        
        # End date widget (column 2)
        end_date_edit = QDateEdit()
        end_date_edit.setCalendarPopup(True)
        # Block signals during programmatic updates
        if self._updating_programmatically:
            end_date_edit.blockSignals(True)
        end_date_edit.setDate(end_date)
        if self._updating_programmatically:
            end_date_edit.blockSignals(False)
        end_date_edit.dateChanged.connect(lambda date, r=row: self._on_date_range_changed(r))
        end_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        end_date_edit.setStyleSheet("""
            QDateEdit {
                border: none;
                border-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
            QDateEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #FFFFFF;
            }
        """)
        self.date_table.setCellWidget(row, 2, end_date_edit)
    
    def _on_checkbox_changed(self, row, state):
        """Handle checkbox state change"""
        self._emit_date_ranges_changed()
    
    def _on_selection_changed(self, current, previous):
        """Handle table selection change - update remove button state"""
        has_selection = self.date_table.currentRow() >= 0 or len(self.date_table.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection and self.date_table.rowCount() > 0)
    
    def _on_add_date_range(self):
        """Add a new date range"""
        self._add_date_range_row()
        # Select the newly added row
        new_row = self.date_table.rowCount() - 1
        self.date_table.selectRow(new_row)
        self._update_tags()
        self._emit_date_ranges_changed()
    
    def _on_remove_selected(self):
        """Remove selected date ranges"""
        selected_rows = set()
        
        # Get selected rows from selection
        for item in self.date_table.selectedItems():
            selected_rows.add(item.row())
        
        # Get checked rows
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_rows.add(row)
        
        # Remove rows in reverse order to maintain indices
        for row in sorted(selected_rows, reverse=True):
            self.date_table.removeRow(row)
        
        self._update_tags()
        self._emit_date_ranges_changed()
        self._on_selection_changed(None, None)
    
    def _on_select_all(self):
        """Select all checkboxes"""
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
        self._emit_date_ranges_changed()
    
    def _on_deselect_all(self):
        """Deselect all checkboxes"""
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
        self._emit_date_ranges_changed()
    
    def _on_date_range_changed(self, row):
        """Handle date range change"""
        self._update_tags()
        self._emit_date_ranges_changed()
    
    def _emit_date_ranges_changed(self):
        """Emit signal with current selected date ranges"""
        # Don't emit during programmatic updates to prevent feedback loops
        if self._updating_programmatically:
            return
        
        selected_ranges = []
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    start_widget = self.date_table.cellWidget(row, 1)
                    end_widget = self.date_table.cellWidget(row, 2)
                    if start_widget and end_widget:
                        start_date_str = start_widget.date().toString("yyyy-MM-dd")
                        end_date_str = end_widget.date().toString("yyyy-MM-dd")
                        selected_ranges.append({
                            "start": start_date_str,
                            "end": end_date_str
                        })
        self.date_ranges_changed.emit(selected_ranges)
    
    def set_date_ranges(self, date_ranges: List[Dict[str, str]], selected_indices: Optional[List[int]] = None):
        """Set date ranges in the table"""
        self._updating_programmatically = True
        try:
            # Block signals on date edits to prevent intermediate updates
            self.date_table.blockSignals(True)
            self.date_table.setRowCount(0)
            selected_indices = selected_indices or []
            
            for idx, date_range in enumerate(date_ranges):
                start_date_str = date_range.get("start", "")
                end_date_str = date_range.get("end", "")
                is_selected = idx in selected_indices
                self._add_date_range_row(start_date_str, end_date_str, is_selected)
            
            self.date_table.blockSignals(False)
            self._update_tags()
        finally:
            self._updating_programmatically = False
            # Emit signal after update is complete (only if not empty)
            if date_ranges:
                self._emit_date_ranges_changed()
    
    def get_selected_date_ranges(self) -> List[Dict[str, str]]:
        """Get currently selected date ranges"""
        selected_ranges = []
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    start_widget = self.date_table.cellWidget(row, 1)
                    end_widget = self.date_table.cellWidget(row, 2)
                    if start_widget and end_widget:
                        start_date_str = start_widget.date().toString("yyyy-MM-dd")
                        end_date_str = end_widget.date().toString("yyyy-MM-dd")
                        selected_ranges.append({
                            "start": start_date_str,
                            "end": end_date_str
                        })
        return selected_ranges
    
    def get_all_date_ranges(self) -> List[Dict[str, str]]:
        """Get all date ranges (selected and unselected)"""
        all_ranges = []
        for row in range(self.date_table.rowCount()):
            start_widget = self.date_table.cellWidget(row, 1)
            end_widget = self.date_table.cellWidget(row, 2)
            if start_widget and end_widget:
                start_date_str = start_widget.date().toString("yyyy-MM-dd")
                end_date_str = end_widget.date().toString("yyyy-MM-dd")
                all_ranges.append({
                    "start": start_date_str,
                    "end": end_date_str
                })
        return all_ranges
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the component"""
        self.selector_button.setEnabled(enabled)
        self.date_table.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled and self.date_table.rowCount() > 0)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)
        super().setEnabled(enabled)

