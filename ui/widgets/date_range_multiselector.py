from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QDateEdit, QTableWidget,
                             QHeaderView, QAbstractItemView, QFrame,
                             QCheckBox, QSizePolicy)
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
        

        self.selector_button = QPushButton()
        self.selector_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: 1px solid
                border-radius: 4px;
                background-color:
                min-height: 32px;
            }
            QPushButton:hover {
                border: 1px solid
                background-color:
            }
            QPushButton:pressed {
                background-color:
            }
            QTableWidget {
                border: 1px solid
                border-radius: 4px;
                background-color:
                gridline-color:
            }
            QTableWidget::item {
                padding: 0px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color:
                color:
            }
            QHeaderView::section {
                background-color:
                padding: 4px;
                border: 1px solid
                font-weight: bold;
            }
            QPushButton {
                background-color:
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color:
            }
            QPushButton:pressed {
                background-color:
            }
            QPushButton {
                background-color:
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color:
            }
            QPushButton:pressed {
                background-color:
            }
            QPushButton {
                background-color:
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color:
            }
            QPushButton:pressed {
                background-color:
            }
            QPushButton {
                background-color:
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color:
            }
            QPushButton:pressed {
                background-color:
            }

        if hasattr(self, '_toggle_in_progress') and self._toggle_in_progress:
            return
        
        self._toggle_in_progress = True
        try:
            self.table_expanded = not self.table_expanded
            self.table_widget.setVisible(self.table_expanded)
            

            if self.table_expanded:
                self.dropdown_arrow.setText("▲")
            else:
                self.dropdown_arrow.setText("▼")
        finally:

            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, lambda: setattr(self, '_toggle_in_progress', False))
    
    def _create_date_tag(self, start_date_str, end_date_str):
        tag = QFrame()
        tag.setFrameShape(QFrame.Box)
        tag.setStyleSheet("""
            QFrame {
                border: 1px solid;
                border-radius: 4px;
                background-color: transparent;
                padding: 0px;
                min-height: 20px;
            }""")

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
                placeholder.setStyleSheet("color:
                self.tags_layout.insertWidget(0, placeholder)
        else:

            placeholder = QLabel("Click to add date ranges")
            placeholder.setStyleSheet("color:
            self.tags_layout.insertWidget(0, placeholder)
            self.selector_button.setVisible(True)
    
    def _add_date_range_row(self, start_date_str="", end_date_str="", selected=False):
        row = self.date_table.rowCount()
        self.date_table.insertRow(row)
        

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
        start_date_edit.setCalendarPopup(True)

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
                border: 1px solid
                background-color:
            }
            QDateEdit {
                border: none;
                border-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
            QDateEdit:focus {
                border: 1px solid
                background-color:
            }
        self._emit_date_ranges_changed()
    
    def _on_selection_changed(self, current, previous):
        has_selection = self.date_table.currentRow() >= 0 or len(self.date_table.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection and self.date_table.rowCount() > 0)
    
    def _on_add_date_range(self):
        self._add_date_range_row()

        new_row = self.date_table.rowCount() - 1
        self.date_table.selectRow(new_row)
        self._update_tags()
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
        self._on_selection_changed(None, None)
    
    def _on_select_all(self):
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
        self._emit_date_ranges_changed()
    
    def _on_deselect_all(self):
        for row in range(self.date_table.rowCount()):
            checkbox_widget = self.date_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
        self._emit_date_ranges_changed()
    
    def _on_date_range_changed(self, row):
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
    
    def set_enabled(self, enabled: bool):
        self.selector_button.setEnabled(enabled)
        self.date_table.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled and self.date_table.rowCount() > 0)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)
        super().setEnabled(enabled)

