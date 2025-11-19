from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTimeEdit, QTableWidget,
                             QHeaderView, QAbstractItemView, QFrame,
                             QCheckBox, QSizePolicy)
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
            self.dropdown_arrow.setText("▼")
        finally:

            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, lambda: setattr(self, '_toggle_in_progress', False))
    
    def _create_time_tag(self, start_time_str, end_time_str):
        tag = QFrame()
        tag.setFrameShape(QFrame.Box)
        
        

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
                placeholder.setStyleSheet("color:
                self.tags_layout.insertWidget(0, placeholder)
        else:

            placeholder = QLabel("Click to add time ranges")
            placeholder.setStyleSheet("color:
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
        start_time_edit.timeChanged.connect(lambda checked, r=row: self._on_time_range_changed(r))
        start_time_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        start_time_edit.setStyleSheet("""
            QTimeEdit {
                border: none;
                border-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
            QTimeEdit:focus {
                border: 1px solid
                background-color:
            }
            QTimeEdit {
                border: none;
                border-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
            QTimeEdit:focus {
                border: 1px solid
                background-color:
            }
        self._emit_time_ranges_changed()
    
    
    def _on_selection_changed(self, current, previous):
        has_selection = self.time_table.currentRow() >= 0 or len(self.time_table.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection and self.time_table.rowCount() > 0)
    
    def _on_add_time_range(self):
        self._add_time_range_row()

        new_row = self.time_table.rowCount() - 1
        self.time_table.selectRow(new_row)
        self._update_tags()
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
        self._on_selection_changed(None, None)
    
    def _on_select_all(self):
        for row in range(self.time_table.rowCount()):
            checkbox_widget = self.time_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
        self._emit_time_ranges_changed()
    
    def _on_deselect_all(self):
        for row in range(self.time_table.rowCount()):
            checkbox_widget = self.time_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
        self._emit_time_ranges_changed()
    
    def _on_time_range_changed(self, row):
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
    
    def set_enabled(self, enabled: bool):
        self.selector_button.setEnabled(enabled)
        self.time_table.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled and self.time_table.rowCount() > 0)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)
        super().setEnabled(enabled)

