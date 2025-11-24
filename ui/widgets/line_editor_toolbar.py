from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QToolButton, QComboBox,
                             QSpinBox, QPushButton, QColorDialog, QLabel, QFrame,
                             QCheckBox, QLineEdit, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QColor, QFont
from typing import Optional


class LineEditorToolbar(QWidget):
    
    format_changed = pyqtSignal(dict)
    
    def __init__(self, line_edit: Optional[QLineEdit] = None, parent=None):
        super().__init__(parent)
        self.line_edit = line_edit
        self._horizontal_alignment = Qt.AlignHCenter
        self._vertical_alignment = Qt.AlignVCenter
        self.font_color = QColor(Qt.white)
        self.text_bg_color = None
        self.init_ui()
        self._connect_line_edit()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                font-size: 12px;
            }
            QToolButton {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 8px;
                min-width: 32px;
                min-height: 24px;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #E8F4F8;
                border: 1px solid #4A90E2;
            }
            QToolButton:pressed {
                background-color: #D0E8F2;
                border: 1px solid #2E5C8A;
            }
            QToolButton:checked {
                background-color: #4A90E2;
                color: #FFFFFF;
                border: 1px solid #2E5C8A;
            }
            QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #FFFFFF;
                font-size: 12px;
                min-width: 80px;
            }
            QComboBox:hover {
                border: 1px solid #999999;
            }
            QComboBox:focus {
                border: 1px solid #4A90E2;
            }
            QSpinBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #FFFFFF;
                font-size: 12px;
                min-width: 60px;
            }
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E8F4F8;
                border: 1px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #D0E8F2;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
            }
        """)
        
        row1 = QHBoxLayout()
        row1.setSpacing(4)
        row1.setContentsMargins(4, 4, 4, 4)
        
        font_family_label = QLabel("Font:")
        row1.addWidget(font_family_label)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Arial", "Times New Roman", "Courier New", "Verdana", "Georgia",
            "Palatino", "Garamond", "Bookman", "Comic Sans MS", "Trebuchet MS",
            "Arial Black", "Impact", "Tahoma", "Lucida Console", "Monaco"
        ])
        self.font_family_combo.currentTextChanged.connect(self._on_font_family_changed)
        row1.addWidget(self.font_family_combo)
        
        font_size_label = QLabel("Size:")
        row1.addWidget(font_size_label)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(6)
        self.font_size_spin.setMaximum(200)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        row1.addWidget(self.font_size_spin)
        
        row1.addWidget(self._create_separator())
        
        self.bold_btn = QToolButton()
        self.bold_btn.setText("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("Bold")
        font = self.bold_btn.font()
        font.setBold(True)
        self.bold_btn.setFont(font)
        self.bold_btn.clicked.connect(self._on_bold_clicked)
        row1.addWidget(self.bold_btn)
        
        self.italic_btn = QToolButton()
        self.italic_btn.setText("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setToolTip("Italic")
        font = self.italic_btn.font()
        font.setItalic(True)
        self.italic_btn.setFont(font)
        self.italic_btn.clicked.connect(self._on_italic_clicked)
        row1.addWidget(self.italic_btn)
        
        self.underline_btn = QToolButton()
        self.underline_btn.setText("U")
        self.underline_btn.setCheckable(True)
        self.underline_btn.setToolTip("Underline")
        font = self.underline_btn.font()
        font.setUnderline(True)
        self.underline_btn.setFont(font)
        self.underline_btn.clicked.connect(self._on_underline_clicked)
        row1.addWidget(self.underline_btn)
        
        row1.addWidget(self._create_separator())
        
        self.font_color_btn = QPushButton("A")
        self.font_color_btn.setToolTip("Font Color")
        self.font_color_btn.clicked.connect(self._on_font_color_clicked)
        self.font_color = QColor(Qt.white)
        self._update_font_color_button()
        row1.addWidget(self.font_color_btn)
        
        self.text_bg_color_btn = QPushButton("")
        self.text_bg_color_btn.setToolTip("Text Background Color (Right-click for No Color)")
        self.text_bg_color_btn.clicked.connect(self._on_text_bg_color_clicked)
        self.text_bg_color_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_bg_color_btn.customContextMenuRequested.connect(self._on_text_bg_color_context_menu)
        self.text_bg_color = None
        self._update_text_bg_color_button()
        row1.addWidget(self.text_bg_color_btn)
        
        row1.addWidget(self._create_separator())
        
        self.outline_btn = QPushButton("🔲")
        self.outline_btn.setCheckable(True)
        self.outline_btn.setToolTip("Text Outline")
        self.outline_btn.clicked.connect(self._on_outline_clicked)
        row1.addWidget(self.outline_btn)
        
        row1.addStretch()
        main_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.setSpacing(4)
        row2.setContentsMargins(4, 4, 4, 4)
        
        self.align_left_btn = QToolButton()
        self.align_left_btn.setText("↤")
        self.align_left_btn.setToolTip("Align Left")
        self.align_left_btn.setCheckable(True)
        self.align_left_btn.setChecked(True)
        self.align_left_btn.clicked.connect(lambda: self._on_horizontal_align_changed(Qt.AlignLeft))
        row2.addWidget(self.align_left_btn)
        
        self.align_center_btn = QToolButton()
        self.align_center_btn.setText("↔")
        self.align_center_btn.setToolTip("Align Center")
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.clicked.connect(lambda: self._on_horizontal_align_changed(Qt.AlignHCenter))
        row2.addWidget(self.align_center_btn)
        
        self.align_right_btn = QToolButton()
        self.align_right_btn.setText("↦")
        self.align_right_btn.setToolTip("Align Right")
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.clicked.connect(lambda: self._on_horizontal_align_changed(Qt.AlignRight))
        row2.addWidget(self.align_right_btn)
        
        row2.addWidget(self._create_separator())
        
        self.align_top_btn = QToolButton()
        self.align_top_btn.setText("↥")
        self.align_top_btn.setToolTip("Align Top")
        self.align_top_btn.setCheckable(True)
        self.align_top_btn.setChecked(True)
        self.align_top_btn.clicked.connect(lambda: self._on_vertical_align_changed(Qt.AlignTop))
        row2.addWidget(self.align_top_btn)
        
        self.align_middle_btn = QToolButton()
        self.align_middle_btn.setText("↕")
        self.align_middle_btn.setToolTip("Align Middle")
        self.align_middle_btn.setCheckable(True)
        self.align_middle_btn.clicked.connect(lambda: self._on_vertical_align_changed(Qt.AlignVCenter))
        row2.addWidget(self.align_middle_btn)
        
        self.align_bottom_btn = QToolButton()
        self.align_bottom_btn.setText("↧")
        self.align_bottom_btn.setToolTip("Align Bottom")
        self.align_bottom_btn.setCheckable(True)
        self.align_bottom_btn.clicked.connect(lambda: self._on_vertical_align_changed(Qt.AlignBottom))
        row2.addWidget(self.align_bottom_btn)
        
        row2.addStretch()
        main_layout.addLayout(row2)
        
        self._horizontal_align_buttons = [self.align_left_btn, self.align_center_btn, self.align_right_btn]
        self._vertical_align_buttons = [self.align_top_btn, self.align_middle_btn, self.align_bottom_btn]
    
    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #CCCCCC;")
        return separator
    
    def set_line_edit(self, line_edit):
        self.line_edit = line_edit
        self._connect_line_edit()
        self._update_format_buttons()
    
    def _connect_line_edit(self):
        if self.line_edit:
            self._update_format_buttons()
    
    def _update_format_buttons(self):
        if not self.line_edit:
            return
        
        font = self.line_edit.font()
        self.font_family_combo.blockSignals(True)
        self.font_size_spin.blockSignals(True)
        self.font_family_combo.setCurrentText(font.family())
        self.font_size_spin.setValue(font.pointSize())
        self.font_family_combo.blockSignals(False)
        self.font_size_spin.blockSignals(False)
        
        self.bold_btn.blockSignals(True)
        self.italic_btn.blockSignals(True)
        self.underline_btn.blockSignals(True)
        self.bold_btn.setChecked(font.bold())
        self.italic_btn.setChecked(font.italic())
        self.underline_btn.setChecked(font.underline())
        self.bold_btn.blockSignals(False)
        self.italic_btn.blockSignals(False)
        self.underline_btn.blockSignals(False)
        
        alignment = self.line_edit.alignment()
        horizontal_align = alignment & (Qt.AlignLeft | Qt.AlignHCenter | Qt.AlignRight)
        if horizontal_align == 0:
            horizontal_align = Qt.AlignLeft
        self._horizontal_alignment = horizontal_align
        
        stylesheet = self.line_edit.styleSheet()
        if stylesheet:
            if "border: 1px solid black" in stylesheet:
                self.outline_btn.blockSignals(True)
                self.outline_btn.setChecked(True)
                self.outline_btn.blockSignals(False)
        
        self.align_left_btn.blockSignals(True)
        self.align_center_btn.blockSignals(True)
        self.align_right_btn.blockSignals(True)
        self.align_left_btn.setChecked(self._horizontal_alignment == Qt.AlignLeft)
        self.align_center_btn.setChecked(self._horizontal_alignment == Qt.AlignHCenter)
        self.align_right_btn.setChecked(self._horizontal_alignment == Qt.AlignRight)
        self.align_left_btn.blockSignals(False)
        self.align_center_btn.blockSignals(False)
        self.align_right_btn.blockSignals(False)
        
        self.align_top_btn.blockSignals(True)
        self.align_middle_btn.blockSignals(True)
        self.align_bottom_btn.blockSignals(True)
        self.align_top_btn.setChecked(self._vertical_alignment == Qt.AlignTop)
        self.align_middle_btn.setChecked(self._vertical_alignment == Qt.AlignVCenter)
        self.align_bottom_btn.setChecked(self._vertical_alignment == Qt.AlignBottom)
        self.align_top_btn.blockSignals(False)
        self.align_middle_btn.blockSignals(False)
        self.align_bottom_btn.blockSignals(False)
    
    def _apply_format_to_line_edit(self):
        if not self.line_edit:
            return
        
        font = self.line_edit.font()
        font.setFamily(self.font_family_combo.currentText())
        font.setPointSize(self.font_size_spin.value())
        font.setBold(self.bold_btn.isChecked())
        font.setItalic(self.italic_btn.isChecked())
        font.setUnderline(self.underline_btn.isChecked())
        self.line_edit.setFont(font)
        
        self.line_edit.setAlignment(self._horizontal_alignment)
        
        style_parts = []
        style_parts.append(f"color: {self.font_color.name()};")
        
        if self.text_bg_color:
            style_parts.append(f"background-color: {self.text_bg_color.name()};")
        
        if self.outline_btn.isChecked():
            style_parts.append("border: 1px solid black;")
        
        if self._vertical_alignment == Qt.AlignTop:
            style_parts.append("padding-top: 0px; padding-bottom: auto;")
        elif self._vertical_alignment == Qt.AlignVCenter:
            style_parts.append("padding-top: auto; padding-bottom: auto;")
        elif self._vertical_alignment == Qt.AlignBottom:
            style_parts.append("padding-top: auto; padding-bottom: 0px;")
        
        self.line_edit.setStyleSheet("".join(style_parts))
    
    def _on_font_family_changed(self, family):
        if not self.line_edit:
            return
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _on_font_size_changed(self, size):
        if not self.line_edit:
            return
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _on_bold_clicked(self, checked):
        if not self.line_edit:
            return
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _on_italic_clicked(self, checked):
        if not self.line_edit:
            return
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _on_underline_clicked(self, checked):
        if not self.line_edit:
            return
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _on_font_color_clicked(self):
        color = QColorDialog.getColor(self.font_color, self, "Select Font Color")
        if color.isValid():
            self.font_color = color
            self._update_font_color_button()
            self._apply_format_to_line_edit()
            self._emit_format_changed()
    
    def _on_text_bg_color_clicked(self):
        color = QColorDialog.getColor(
            self.text_bg_color if self.text_bg_color else Qt.white,
            self, "Select Text Background Color"
        )
        if color.isValid():
            self.text_bg_color = color
            self._update_text_bg_color_button()
            self._apply_format_to_line_edit()
            self._emit_format_changed()
    
    def _on_text_bg_color_context_menu(self, position: QPoint):
        menu = QMenu(self)
        choose_color_action = menu.addAction("Choose Color...")
        no_color_action = menu.addAction("No Color")
        menu.addSeparator()
        
        action = menu.exec_(self.text_bg_color_btn.mapToGlobal(position))
        
        if action == choose_color_action:
            self._on_text_bg_color_clicked()
        elif action == no_color_action:
            self.text_bg_color = None
            self._update_text_bg_color_button()
            self._apply_format_to_line_edit()
            self._emit_format_changed()
    
    def _on_outline_clicked(self, checked):
        if not self.line_edit:
            return
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _on_horizontal_align_changed(self, alignment):
        for btn in self._horizontal_align_buttons:
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)
        
        if alignment == Qt.AlignLeft:
            self.align_left_btn.setChecked(True)
        elif alignment == Qt.AlignHCenter:
            self.align_center_btn.setChecked(True)
        elif alignment == Qt.AlignRight:
            self.align_right_btn.setChecked(True)
        
        self._horizontal_alignment = alignment
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _on_vertical_align_changed(self, alignment):
        for btn in self._vertical_align_buttons:
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)
        
        if alignment == Qt.AlignTop:
            self.align_top_btn.setChecked(True)
        elif alignment == Qt.AlignVCenter:
            self.align_middle_btn.setChecked(True)
        elif alignment == Qt.AlignBottom:
            self.align_bottom_btn.setChecked(True)
        
        self._vertical_alignment = alignment
        self._apply_format_to_line_edit()
        self._emit_format_changed()
    
    def _update_font_color_button(self):
        if self.font_color:
            self.font_color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.font_color.name()};
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 12px;
                    color: {'white' if self.font_color.lightness() < 128 else 'black'};
                }}
                QPushButton:hover {{
                    border: 2px solid #4A90E2;
                }}
                QPushButton:pressed {{
                    background-color: {self.font_color.darker(120).name()};
                }}
            """)
        else:
            self.font_color_btn.setStyleSheet("")
    
    def _update_text_bg_color_button(self):
        if self.text_bg_color:
            self.text_bg_color_btn.setText("")
            self.text_bg_color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.text_bg_color.name()};
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 12px;
                    color: {'white' if self.text_bg_color.lightness() < 128 else 'black'};
                }}
                QPushButton:hover {{
                    border: 2px solid #4A90E2;
                }}
                QPushButton:pressed {{
                    background-color: {self.text_bg_color.darker(120).name()};
                }}
            """)
        else:
            self.text_bg_color_btn.setText("Text BG")
            self.text_bg_color_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #E8F4F8;
                    border: 1px solid #4A90E2;
                }
                QPushButton:pressed {
                    background-color: #D0E8F2;
                }
            """)
    
    def _emit_format_changed(self):
        alignment_str = "left"
        if self._horizontal_alignment == Qt.AlignHCenter:
            alignment_str = "center"
        elif self._horizontal_alignment == Qt.AlignRight:
            alignment_str = "right"
        
        vertical_alignment_str = "top"
        if self._vertical_alignment == Qt.AlignVCenter:
            vertical_alignment_str = "middle"
        elif self._vertical_alignment == Qt.AlignBottom:
            vertical_alignment_str = "bottom"
        
        format_data = {
            "font_family": self.font_family_combo.currentText(),
            "font_size": self.font_size_spin.value(),
            "bold": self.bold_btn.isChecked(),
            "italic": self.italic_btn.isChecked(),
            "underline": self.underline_btn.isChecked(),
            "font_color": self.font_color.name() if self.font_color else None,
            "text_bg_color": self.text_bg_color.name() if self.text_bg_color else None,
            "outline": self.outline_btn.isChecked(),
            "alignment": alignment_str,
            "vertical_alignment": vertical_alignment_str,
        }
        self.format_changed.emit(format_data)

