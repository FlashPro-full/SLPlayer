from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTimeEdit, QTableWidget,
                             QHeaderView, QAbstractItemView, QFrame,
                             QCheckBox, QSizePolicy, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTime, pyqtSignal
from typing import List, Dict, Optional


class TimeRangeMultiSelector(QWidget):
    
    time_ranges_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time_ranges: List[Dict[str, str]] = []
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
        
        self.time_table = QTableWidget()
        self.time_table.setColumnCount(3)
        self.time_table.setHorizontalHeaderLabels(["", "Start", "End"])
        self.time_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.time_table.verticalHeader().setVisible(False)
        self.time_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.time_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.time_table.setAlternatingRowColors(True)
        self.time_table.setStyleSheet("""
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
        self.time_table.setVisible(False)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(4)
        
        self.add_btn = QPushButton("➕")
        self.add_btn.setToolTip("Add time range")
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
        self.add_btn.clicked.connect(self._on_add_time_range)
        
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
        layout.addWidget(self.time_table)
        layout.addWidget(toolbar_widget)
        
        self.time_table.itemSelectionChanged.connect(self._on_selection_changed)
        self._update_tags()
    
    def _on_toggle_table(self):
        if hasattr(self, '_toggle_in_progress') and self._toggle_in_progress:
            return
        self._toggle_in_progress = True
        try:
            self.table_expanded = not self.table_expanded
            self.time_table.setVisible(self.table_expanded)
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
    
    def _create_time_tag(self, start_time_str: str, end_time_str: str) -> QFrame:
        tag = QFrame()
        tag.setFrameShape(QFrame.Box)
        tag.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 1px solid #90CAF9;
                border-radius: 3px;
                padding: 0px;
            }
        """)
        
        tag_layout = QHBoxLayout(tag)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(4)
        
        time_label = QLabel(f"{start_time_str} - {end_time_str}")
        time_label.setStyleSheet("font-size: 12px; color: #1976D2;")
        tag_layout.addWidget(time_label)
        
        return tag
    
    def _update_tags(self):
        while self.tags_layout.count():
            child = self.tags_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for row in range(self.time_table.rowCount()):
            start_widget = self.time_table.cellWidget(row, 1)
            end_widget = self.time_table.cellWidget(row, 2)
            if start_widget and end_widget:
                start_time_str = start_widget.time().toString("HH:mm:ss")
                end_time_str = end_widget.time().toString("HH:mm:ss")
                tag = self._create_time_tag(start_time_str, end_time_str)
                self.tags_layout.addWidget(tag)
        
        self.tags_layout.addStretch()
        
        if self.time_table.rowCount() > 0:
            self.selector_button.setVisible(True)
            if self.tags_layout.count() == 1:
                placeholder = QLabel("Click to add time ranges")
                placeholder.setStyleSheet("color: #666666; font-size: 12px;")
                self.tags_layout.insertWidget(0, placeholder)
        else:
            placeholder = QLabel("Click to add time ranges")
            placeholder.setStyleSheet("color: #666666; font-size: 12px;")
            self.tags_layout.insertWidget(0, placeholder)
            self.selector_button.setVisible(True)
    
    def _add_time_range_row(self, start_time_str="00:00:00", end_time_str="23:59:59", selected=False):
        row = self.time_table.rowCount()
        self.time_table.insertRow(row)
        
        start_parts = start_time_str.split(":")
        end_parts = end_time_str.split(":")
        
        start_time = QTime(0, 0, 0)
        end_time = QTime(23, 59, 59)
        
        if len(start_parts) >= 2:
            start_time = QTime(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]) if len(start_parts) > 2 else 0)
        if len(end_parts) >= 2:
            end_time = QTime(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]) if len(end_parts) > 2 else 0)
        
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
        self.time_table.setCellWidget(row, 0, checkbox_widget)
        
        start_time_edit = QTimeEdit()
        start_time_edit.setDisplayFormat("HH:mm:ss")
        if self._updating_programmatically:
            start_time_edit.blockSignals(True)
        start_time_edit.setTime(start_time)
        if self._updating_programmatically:
            start_time_edit.blockSignals(False)
        start_time_edit.timeChanged.connect(lambda time, r=row: self._on_time_range_changed(r))
        start_time_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        start_time_edit.setStyleSheet("""
            QTimeEdit {
                border: 1px solid #DDDDDD;
                border-radius: 2px;
                padding: 2px;
            }
            QTimeEdit:focus {
                border: 1px solid #2196F3;
                background-color: #E3F2FD;
            }
        """)
        self.time_table.setCellWidget(row, 1, start_time_edit)
        
        end_time_edit = QTimeEdit()
        end_time_edit.setDisplayFormat("HH:mm:ss")
        if self._updating_programmatically:
            end_time_edit.blockSignals(True)
        end_time_edit.setTime(end_time)
        if self._updating_programmatically:
            end_time_edit.blockSignals(False)
        end_time_edit.timeChanged.connect(lambda time, r=row: self._on_time_range_changed(r))
        end_time_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        end_time_edit.setStyleSheet("""
            QTimeEdit {
                border: 1px solid #DDDDDD;
                border-radius: 2px;
                padding: 2px;
            }
            QTimeEdit:focus {
                border: 1px solid #2196F3;
                background-color: #E3F2FD;
            }
        """)
        self.time_table.setCellWidget(row, 2, end_time_edit)
        
        self._update_tags()
    
    def _on_checkbox_changed(self, row: int, state: int):
        self._emit_time_ranges_changed()
    
    def _on_selection_changed(self):
        has_selection = self.time_table.currentRow() >= 0 or len(self.time_table.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection and self.time_table.rowCount() > 0)
    
    def _on_add_time_range(self):
        self._add_time_range_row()
        new_row = self.time_table.rowCount() - 1
        self.time_table.selectRow(new_row)
        self._emit_time_ranges_changed()
    
    def _on_remove_selected(self):
        selected_rows = set()
        
        for item in self.time_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in range(self.time_table.rowCount()):
            checkbox_widget = self.time_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_rows.add(row)
        
        for row in sorted(selected_rows, reverse=True):
            self.time_table.removeRow(row)
        
        self._update_tags()
        self._emit_time_ranges_changed()
        self._on_selection_changed()
    
    def _on_select_all(self):
        self._updating_programmatically = True
        try:
            for row in range(self.time_table.rowCount()):
                checkbox_widget = self.time_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(True)
        finally:
            self._updating_programmatically = False
        self._emit_time_ranges_changed()
    
    def _on_deselect_all(self):
        self._updating_programmatically = True
        try:
            for row in range(self.time_table.rowCount()):
                checkbox_widget = self.time_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(False)
        finally:
            self._updating_programmatically = False
        self._emit_time_ranges_changed()
    
    def _on_time_range_changed(self, row: int):
        self._update_tags()
        self._emit_time_ranges_changed()
    
    def _emit_time_ranges_changed(self):
        if self._updating_programmatically:
            return
        
        selected_ranges = []
        for row in range(self.time_table.rowCount()):
            checkbox_widget = self.time_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    start_widget = self.time_table.cellWidget(row, 1)
                    end_widget = self.time_table.cellWidget(row, 2)
                    if start_widget and end_widget:
                        start_time_str = start_widget.time().toString("HH:mm:ss")
                        end_time_str = end_widget.time().toString("HH:mm:ss")
                        selected_ranges.append({
                            "start": start_time_str,
                            "end": end_time_str
                        })
        self.time_ranges_changed.emit(selected_ranges)
    
    def set_time_ranges(self, time_ranges: List[Dict[str, str]], selected_indices: Optional[List[int]] = None):
        self._updating_programmatically = True
        try:
            self.time_table.blockSignals(True)
            self.time_table.setRowCount(0)
            selected_indices = selected_indices or []
            
            for idx, time_range in enumerate(time_ranges):
                start_time_str = time_range.get("start", "00:00:00")
                end_time_str = time_range.get("end", "23:59:59")
                is_selected = idx in selected_indices
                self._add_time_range_row(start_time_str, end_time_str, is_selected)
            
            self.time_table.blockSignals(False)
            self._update_tags()
        finally:
            self._updating_programmatically = False
            if time_ranges:
                self._emit_time_ranges_changed()
    
    def get_selected_time_ranges(self) -> List[Dict[str, str]]:
        selected_ranges = []
        for row in range(self.time_table.rowCount()):
            checkbox_widget = self.time_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    start_widget = self.time_table.cellWidget(row, 1)
                    end_widget = self.time_table.cellWidget(row, 2)
                    if start_widget and end_widget:
                        start_time_str = start_widget.time().toString("HH:mm:ss")
                        end_time_str = end_widget.time().toString("HH:mm:ss")
                        selected_ranges.append({
                            "start": start_time_str,
                            "end": end_time_str
                        })
        return selected_ranges
    
    def get_all_time_ranges(self) -> List[Dict[str, str]]:
        all_ranges = []
        for row in range(self.time_table.rowCount()):
            start_widget = self.time_table.cellWidget(row, 1)
            end_widget = self.time_table.cellWidget(row, 2)
            if start_widget and end_widget:
                start_time_str = start_widget.time().toString("HH:mm:ss")
                end_time_str = end_widget.time().toString("HH:mm:ss")
                all_ranges.append({
                    "start": start_time_str,
                    "end": end_time_str
                })
        return all_ranges
    
    def collapse(self):
        if self.table_expanded:
            self.table_expanded = False
            self.time_table.setVisible(False)
            toolbar_widget = self.layout().itemAt(2).widget()
            if toolbar_widget:
                toolbar_widget.setVisible(False)
            self.dropdown_arrow.setText("▼")
    
    def set_enabled(self, enabled: bool):
        self.selector_button.setEnabled(enabled)
        self.time_table.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled and self.time_table.rowCount() > 0)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)
        super().setEnabled(enabled)

