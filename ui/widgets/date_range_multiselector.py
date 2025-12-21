from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QDateEdit, QTableWidget,
                             QHeaderView, QAbstractItemView, QFrame,
                             QCheckBox, QSizePolicy, QTableWidgetItem)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from typing import List, Dict, Optional


class DateRangeMultiSelector(QWidget):
    
    date_ranges_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.date_ranges: List[Dict[str, str]] = []
        self.table_expanded = False
        self._updating_programmatically = False
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)
        
        self.selector_button = QPushButton()
        self.selector_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 14px;
                border: 1px solid #555555;
                color: #FFFFFF;
                border-radius: 4px;
                background-color: #3B3B3B;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #3B3B3B;
                color: #FFFFFF;
            }
        """)
        
        self.dropdown_arrow = QLabel("▼")
        self.dropdown_arrow.setStyleSheet("color: #666666; font-size: 10px;")
        self.dropdown_arrow.setFixedWidth(15)
        
        self.tags_container = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(4, 4, 4, 4)
        self.tags_layout.setSpacing(4)
        
        button_inner_layout = QHBoxLayout()
        button_inner_layout.setContentsMargins(4, 4, 4, 4)
        button_inner_layout.setSpacing(4)
        button_inner_layout.addWidget(self.tags_container)
        button_inner_layout.addWidget(self.dropdown_arrow)
        self.selector_button.setLayout(button_inner_layout)
        
        self.selector_button.clicked.connect(self._on_toggle_table)
        
        self.date_table = QTableWidget()
        self.date_table.setColumnCount(3)
        self.date_table.setHorizontalHeaderLabels(["", "Start", "End"])
        self.date_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.date_table.verticalHeader().setVisible(False)
        self.date_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.date_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.date_table.setAlternatingRowColors(True)
        self.date_table.setStyleSheet("""
            QTableWidget {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                color: #FFFFFF;
                gridline-color: #555555;
            }
            QTableWidget::item {
                color: #FFFFFF;
                border-bottom: 1px solid #555555;
                padding: 2px;
            }
            QTableWidget::item:hover {
                background-color: #2A60B2;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: #2A60B2;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QTableWidget::item:selected:hover {
                background-color: #2A60B2;
                border: 1px solid #4A90E2;
                outline: none;
            }
            QHeaderView {
                background-color: #3B3B3B;
            }
            QHeaderView::section {
                background-color: #3B3B3B;
                color: #FFFFFF;
                padding: 8px;
                border: 1px solid #555555;
            }
            QTableWidget QHeaderView::section:horizontal {
                background-color: #3B3B3B;
                color: #FFFFFF;
                padding: 8px;
                border: 1px solid #555555;
                border-top: none;
            }
            QTableCornerButton::section {
                background-color: #3B3B3B;
                border: 1px solid #555555;
            }
        """)
        self.date_table.setVisible(False)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(4)
        
        self.add_btn = QPushButton("➕")
        self.add_btn.setToolTip("Add date range")
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #555555;
                color: #FFFFFF;
                border-radius: 4px;
                background-color: #3B3B3B;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
            }
        """)
        self.add_btn.clicked.connect(self._on_add_date_range)
        
        self.remove_btn = QPushButton("🗑")
        self.remove_btn.setToolTip("Remove selected")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setEnabled(False)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #555555;
                color: #FFFFFF;
                border-radius: 4px;
                background-color: #3B3B3B;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
            }
            QPushButton:disabled {
                background-color: #2B2B2B;
                color: #666666;
            }
        """)
        self.remove_btn.clicked.connect(self._on_remove_selected)
        
        self.select_all_btn = QPushButton("☑️")
        self.select_all_btn.setToolTip("Select all")
        self.select_all_btn.setFixedSize(30, 30)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #555555;
                color: #FFFFFF;
                border-radius: 4px;
                background-color: #3B3B3B;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
            }
        """)
        self.select_all_btn.clicked.connect(self._on_select_all)
        
        self.deselect_all_btn = QPushButton("🟪")
        self.deselect_all_btn.setToolTip("Deselect all")
        self.deselect_all_btn.setFixedSize(30, 30)
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #555555;
                color: #FFFFFF;
                border-radius: 4px;
                background-color: #3B3B3B;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
            }
        """)
        self.deselect_all_btn.clicked.connect(self._on_deselect_all)
        
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.remove_btn)
        toolbar_layout.addWidget(self.select_all_btn)
        toolbar_layout.addWidget(self.deselect_all_btn)
        toolbar_layout.addStretch()
        
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)
        toolbar_widget.setVisible(False)
        
        button_layout.addWidget(self.selector_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.date_table)
        layout.addWidget(toolbar_widget)
        
        self.date_table.itemSelectionChanged.connect(self._on_selection_changed)
        self._update_tags()
    
    def _on_toggle_table(self):
        if hasattr(self, '_toggle_in_progress') and self._toggle_in_progress:
            return
        self._toggle_in_progress = True
        try:
            self.table_expanded = not self.table_expanded
            self.date_table.setVisible(self.table_expanded)
            toolbar_widget = self.layout().itemAt(2).widget()
            if toolbar_widget:
                toolbar_widget.setVisible(self.table_expanded)
            if self.table_expanded:
                self.dropdown_arrow.setText("▲")
            else:
                self.dropdown_arrow.setText("▼")
        finally:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, lambda: setattr(self, '_toggle_in_progress', False))
    
    def _create_date_tag(self, start_date_str: str, end_date_str: str) -> QFrame:
        tag = QFrame()
        tag.setFrameShape(QFrame.Box)
        tag.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 1px solid #90CAF9;
                border-radius: 3px;
                padding: 0;
            }
        """)
        
        tag_layout = QHBoxLayout(tag)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(4)
        
        date_label = QLabel(f"{start_date_str} - {end_date_str}")
        date_label.setStyleSheet("font-size: 12px; color: #1976D2;")
        tag_layout.addWidget(date_label)
        
        return tag
    
    def _update_tags(self):
        while self.tags_layout.count():
            child = self.tags_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for row in range(self.date_table.rowCount()):
            start_widget = self.date_table.cellWidget(row, 1)
            end_widget = self.date_table.cellWidget(row, 2)
            if start_widget and end_widget:
                start_date_str = start_widget.date().toString("yyyy-MM-dd")
                end_date_str = end_widget.date().toString("yyyy-MM-dd")
                tag = self._create_date_tag(start_date_str, end_date_str)
                self.tags_layout.addWidget(tag)
        
        self.tags_layout.addStretch()
        
        if self.date_table.rowCount() > 0:
            self.selector_button.setVisible(True)
            if self.tags_layout.count() == 1:
                placeholder = QLabel("Click to add date ranges")
                placeholder.setStyleSheet("color: #666666; font-size: 12px;")
                self.tags_layout.insertWidget(0, placeholder)
        else:
            placeholder = QLabel("Click to add date ranges")
            placeholder.setStyleSheet("color: #666666; font-size: 12px;")
            self.tags_layout.insertWidget(0, placeholder)
            self.selector_button.setVisible(True)
    
    def _add_date_range_row(self, start_date_str="", end_date_str="", selected=False):
        row = self.date_table.rowCount()
        self.date_table.insertRow(row)
        
        start_date = QDate.currentDate()
        end_date = QDate.currentDate()
        
        if start_date_str:
            try:
                start_parts = start_date_str.split("-")
                if len(start_parts) >= 3:
                    start_date = QDate(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
            except (ValueError, IndexError):
                start_date = QDate.currentDate()
        
        if end_date_str:
            try:
                end_parts = end_date_str.split("-")
                if len(end_parts) >= 3:
                    end_date = QDate(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))
            except (ValueError, IndexError):
                end_date = QDate.currentDate()
        
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox = QCheckBox()
        
        if self._updating_programmatically:
            checkbox.blockSignals(True)
        checkbox.setChecked(selected)
        if self._updating_programmatically:
            checkbox.blockSignals(False)
        checkbox.stateChanged.connect(lambda state, r=row: self._on_checkbox_changed(r, state))
        checkbox_layout.addWidget(checkbox)
        self.date_table.setCellWidget(row, 0, checkbox_widget)
        
        start_date_edit = QDateEdit()
        start_date_edit.setDisplayFormat("yyyy-MM-dd")
        start_date_edit.setCalendarPopup(True)
        if self._updating_programmatically:
            start_date_edit.blockSignals(True)
        start_date_edit.setDate(start_date)
        if self._updating_programmatically:
            start_date_edit.blockSignals(False)
        start_date_edit.dateChanged.connect(lambda date, r=row: self._on_date_range_changed(r))
        start_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        start_date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid #DDDDDD;
                border-radius: 2px;
                padding: 2px;
            }
            QDateEdit:focus {
                border: 1px solid #2196F3;
                background-color: #E3F2FD;
            }
        """)
        self.date_table.setCellWidget(row, 1, start_date_edit)
        
        end_date_edit = QDateEdit()
        end_date_edit.setDisplayFormat("yyyy-MM-dd")
        end_date_edit.setCalendarPopup(True)
        if self._updating_programmatically:
            end_date_edit.blockSignals(True)
        end_date_edit.setDate(end_date)
        if self._updating_programmatically:
            end_date_edit.blockSignals(False)
        end_date_edit.dateChanged.connect(lambda date, r=row: self._on_date_range_changed(r))
        end_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        end_date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid #DDDDDD;
                border-radius: 2px;
                padding: 2px;
            }
            QDateEdit:focus {
                border: 1px solid #2196F3;
                background-color: #E3F2FD;
            }
        """)
        self.date_table.setCellWidget(row, 2, end_date_edit)
        
        self._update_tags()
    
    def _on_checkbox_changed(self, row: int, state: int):
        self._emit_date_ranges_changed()
    
    def _on_selection_changed(self):
        has_selection = self.date_table.currentRow() >= 0 or len(self.date_table.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection and self.date_table.rowCount() > 0)
    
    def _on_add_date_range(self):
        self._add_date_range_row()
        new_row = self.date_table.rowCount() - 1
        self.date_table.selectRow(new_row)
        self._emit_date_ranges_changed()
    
    def _on_remove_selected(self):
        selected_rows = set()
        
        for item in self.date_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_rows.add(row)
        
        for row in sorted(selected_rows, reverse=True):
            self.date_table.removeRow(row)
        
        self._update_tags()
        self._emit_date_ranges_changed()
        self._on_selection_changed()
    
    def _on_select_all(self):
        self._updating_programmatically = True
        try:
            for row in range(self.date_table.rowCount()):
                checkbox_widget = self.date_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(True)
        finally:
            self._updating_programmatically = False
        self._emit_date_ranges_changed()
    
    def _on_deselect_all(self):
        self._updating_programmatically = True
        try:
            for row in range(self.date_table.rowCount()):
                checkbox_widget = self.date_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(False)
        finally:
            self._updating_programmatically = False
        self._emit_date_ranges_changed()
    
    def _on_date_range_changed(self, row: int):
        self._update_tags()
        self._emit_date_ranges_changed()
    
    def _emit_date_ranges_changed(self):
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
        self._updating_programmatically = True
        try:
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
            if date_ranges:
                self._emit_date_ranges_changed()
    
    def get_selected_date_ranges(self) -> List[Dict[str, str]]:
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
    
    def collapse(self):
        if self.table_expanded:
            self.table_expanded = False
            self.date_table.setVisible(False)
            toolbar_widget = self.layout().itemAt(2).widget()
            if toolbar_widget:
                toolbar_widget.setVisible(False)
            self.dropdown_arrow.setText("▼")
    
    def set_enabled(self, enabled: bool):
        self.selector_button.setEnabled(enabled)
        self.date_table.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled and self.date_table.rowCount() > 0)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)
        super().setEnabled(enabled)

