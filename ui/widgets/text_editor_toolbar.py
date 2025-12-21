from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QToolButton, QComboBox,
                             QSpinBox, QPushButton, QColorDialog, QLabel, QFrame,
                             QCheckBox, QTextEdit, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import (QTextCharFormat, QTextBlockFormat, QTextCursor,
                         QColor, QFont, QTextFrameFormat, QPen, QBrush)
from typing import Optional


class TextEditorToolbar(QWidget):
    
    format_changed = pyqtSignal(dict)
    
    def __init__(self, text_edit: Optional[QTextEdit] = None, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit
        self._horizontal_alignment = Qt.AlignHCenter #type: ignore
        self._vertical_alignment = Qt.AlignVCenter #type: ignore    
        self.font_color = QColor(Qt.white) #type: ignore
        self.text_bg_color = None
        self.init_ui()
        self._connect_text_edit()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                font-size: 12px;
                color: #FFFFFF;
            }
            QToolButton {
                background-color: #3B3B3B;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 8px;
                min-width: 32px;
                min-height: 24px;
                font-size: 12px;
                color: #FFFFFF;
            }
            QToolButton:hover {
                background-color: #4B4B4B;
                border: 1px solid #4A90E2;
            }
            QToolButton:pressed {
                background-color: #5B5B5B;
                border: 1px solid #2E5C8A;
            }
            QToolButton:checked {
                background-color: #4A90E2;
                color: #FFFFFF;
                border: 1px solid #2E5C8A;
            }
            QComboBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #3B3B3B;
                color: #FFFFFF;
                font-size: 12px;
                min-width: 80px;
            }
            QComboBox:hover {
                border: 1px solid #666666;
            }
            QComboBox:focus {
                border: 1px solid #4A90E2;
            }
            QComboBox QAbstractItemView {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: 1px solid #555555;
                selection-background-color: #3B3B3B;
                selection-color: #FFFFFF;
            }
            QSpinBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: #3B3B3B;
                color: #FFFFFF;
                font-size: 12px;
                min-width: 60px;
            }
            QPushButton {
                background-color: #3B3B3B;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
                border: 1px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #5B5B5B;
            }
            QLabel {
                color: #FFFFFF;
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
        self.font_size_spin.editingFinished.connect(self._on_font_size_editing_finished)
        self._font_size_editing = False
        line_edit = self.font_size_spin.lineEdit()
        line_edit.textChanged.connect(self._on_font_size_text_changed)
        row1.addWidget(self.font_size_spin)

        main_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.setSpacing(4)
        row2.setContentsMargins(4, 4, 4, 4)

        self.bold_btn = QToolButton()
        self.bold_btn.setText("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("Bold")
        font = self.bold_btn.font()
        font.setBold(True)
        self.bold_btn.setFont(font)
        self.bold_btn.clicked.connect(self._on_bold_clicked)
        row2.addWidget(self.bold_btn)
        
        self.italic_btn = QToolButton()
        self.italic_btn.setText("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setToolTip("Italic")
        font = self.italic_btn.font()
        font.setItalic(True)
        self.italic_btn.setFont(font)
        self.italic_btn.clicked.connect(self._on_italic_clicked)
        row2.addWidget(self.italic_btn)
        
        self.underline_btn = QToolButton()
        self.underline_btn.setText("U")
        self.underline_btn.setCheckable(True)
        self.underline_btn.setToolTip("Underline")
        font = self.underline_btn.font()
        font.setUnderline(True)
        self.underline_btn.setFont(font)
        self.underline_btn.clicked.connect(self._on_underline_clicked)
        row2.addWidget(self.underline_btn)

        main_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(4)
        row3.setContentsMargins(4, 4, 4, 4)
        
        self.font_color_btn = QToolButton()
        self.font_color_btn.setText("A")
        self.font_color_btn.setToolTip("Font Color")
        self.font_color_btn.clicked.connect(self._on_font_color_clicked)
        self.font_color = QColor(Qt.white)
        self._update_font_color_button()
        row3.addWidget(self.font_color_btn)
        
        self.text_bg_color_btn = QToolButton()
        self.text_bg_color_btn.setText("")
        self.text_bg_color_btn.setToolTip("Text Background Color (Right-click for No Color)")
        self.text_bg_color_btn.clicked.connect(self._on_text_bg_color_clicked)
        self.text_bg_color_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_bg_color_btn.customContextMenuRequested.connect(self._on_text_bg_color_context_menu)
        self.text_bg_color = None
        self._update_text_bg_color_button()
        row3.addWidget(self.text_bg_color_btn)
        
        self.outline_btn = QToolButton()
        self.outline_btn.setText("🔲")
        self.outline_btn.setCheckable(True)
        self.outline_btn.setToolTip("Text Outline")
        self.outline_btn.clicked.connect(self._on_outline_clicked)
        row3.addWidget(self.outline_btn)
        
        main_layout.addLayout(row3)
        
        row4 = QHBoxLayout()
        row4.setSpacing(4)
        row4.setContentsMargins(4, 4, 4, 4)
        
        self.align_left_btn = QToolButton()
        self.align_left_btn.setText("↤")
        self.align_left_btn.setToolTip("Align Left")
        self.align_left_btn.setCheckable(True)
        self.align_left_btn.clicked.connect(lambda: self._on_horizontal_align_changed(Qt.AlignLeft))
        row4.addWidget(self.align_left_btn)
        
        self.align_center_btn = QToolButton()
        self.align_center_btn.setText("↔")
        self.align_center_btn.setToolTip("Align Center")
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.setChecked(True)
        self.align_center_btn.clicked.connect(lambda: self._on_horizontal_align_changed(Qt.AlignHCenter))
        row4.addWidget(self.align_center_btn)
        
        self.align_right_btn = QToolButton()
        self.align_right_btn.setText("↦")
        self.align_right_btn.setToolTip("Align Right")
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.clicked.connect(lambda: self._on_horizontal_align_changed(Qt.AlignRight))
        row4.addWidget(self.align_right_btn)

        main_layout.addLayout(row4)
        
        row5 = QHBoxLayout()
        row5.setSpacing(4)
        row5.setContentsMargins(4, 4, 4, 4)
        
        self.align_top_btn = QToolButton()
        self.align_top_btn.setText("↥")
        self.align_top_btn.setToolTip("Align Top")
        self.align_top_btn.setCheckable(True)
        self.align_top_btn.clicked.connect(lambda: self._on_vertical_align_changed(Qt.AlignTop))
        row5.addWidget(self.align_top_btn)
        
        self.align_middle_btn = QToolButton()
        self.align_middle_btn.setText("↕")
        self.align_middle_btn.setToolTip("Align Middle")
        self.align_middle_btn.setCheckable(True)
        self.align_middle_btn.setChecked(True)
        self.align_middle_btn.clicked.connect(lambda: self._on_vertical_align_changed(Qt.AlignVCenter))
        row5.addWidget(self.align_middle_btn)
        
        self.align_bottom_btn = QToolButton()
        self.align_bottom_btn.setText("↧")
        self.align_bottom_btn.setToolTip("Align Bottom")
        self.align_bottom_btn.setCheckable(True)
        self.align_bottom_btn.clicked.connect(lambda: self._on_vertical_align_changed(Qt.AlignBottom))
        row5.addWidget(self.align_bottom_btn)
        
        main_layout.addLayout(row5)
        
        self._horizontal_align_buttons = [self.align_left_btn, self.align_center_btn, self.align_right_btn]
        self._vertical_align_buttons = [self.align_top_btn, self.align_middle_btn, self.align_bottom_btn]
        self._horizontal_alignment = Qt.AlignHCenter
        self._vertical_alignment = Qt.AlignVCenter
        self._apply_initial_alignment()
    
    def _apply_initial_alignment(self):
        if self.text_edit:
            cursor = self.text_edit.textCursor()
            block_format = cursor.blockFormat()
            block_format.setAlignment(self._horizontal_alignment)
            cursor.setBlockFormat(block_format)
            self.text_edit.setTextCursor(cursor)
    
    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #CCCCCC;")
        return separator
    
    def set_text_edit(self, text_edit):
        self.text_edit = text_edit
        self._connect_text_edit()
    
    def _connect_text_edit(self):
        if self.text_edit:
            self.text_edit.cursorPositionChanged.connect(self._update_format_buttons)
            self.text_edit.textChanged.connect(self._update_format_buttons)
            self._apply_initial_alignment()
    
    def _update_format_buttons(self):
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        block_format = cursor.blockFormat()
        
        font = char_format.font()
        self.font_family_combo.blockSignals(True)
        self.font_size_spin.blockSignals(True)
        self.font_family_combo.setCurrentText(font.family())
        self.font_size_spin.setValue(font.pointSize())
        self.font_family_combo.blockSignals(False)
        self.font_size_spin.blockSignals(False)
        
        self.bold_btn.blockSignals(True)
        self.italic_btn.blockSignals(True)
        self.underline_btn.blockSignals(True)
        self.bold_btn.setChecked(char_format.fontWeight() == QFont.Bold)
        self.italic_btn.setChecked(char_format.fontItalic())
        self.underline_btn.setChecked(char_format.fontUnderline())
        self.bold_btn.blockSignals(False)
        self.italic_btn.blockSignals(False)
        self.underline_btn.blockSignals(False)
        
        foreground = char_format.foreground()
        if foreground.style() != Qt.NoBrush and foreground.color().isValid():
            cursor_color = foreground.color()
            if cursor_color != QColor(Qt.black) or self.font_color == QColor(Qt.black):
                self.font_color = cursor_color
            self._update_font_color_button()
        
        bg_brush = char_format.background()
        bg_style = bg_brush.style()
        if bg_style != 0 and bg_brush.color().isValid() and bg_brush.color().alpha() > 0:
            bg_color = bg_brush.color()
            if bg_color != QColor(Qt.transparent):
                self.text_bg_color = bg_color
            else:
                self.text_bg_color = None
        else:
            self.text_bg_color = None
        self._update_text_bg_color_button()
        
        alignment = block_format.alignment()
        if alignment != 0:
            horizontal_align = alignment & (Qt.AlignLeft | Qt.AlignHCenter | Qt.AlignRight)
            if horizontal_align == 0:
                horizontal_align = Qt.AlignHCenter
            self._horizontal_alignment = horizontal_align
        else:
            self._horizontal_alignment = Qt.AlignHCenter
        
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
        
        pen = char_format.textOutline()
        self.outline_btn.blockSignals(True)
        self.outline_btn.setChecked(pen.style() != Qt.NoPen if pen else False)
        self.outline_btn.blockSignals(False)
    
    def _on_font_family_changed(self, family):
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        font = char_format.font()
        font.setFamily(family)
        char_format.setFont(font)
        cursor.setCharFormat(char_format)
        self._emit_format_changed()
    
    def _on_font_size_text_changed(self, text):
        self._font_size_editing = True
    
    def _on_font_size_editing_finished(self):
        self._font_size_editing = False
        text = self.font_size_spin.lineEdit().text().strip()
        if text:
            try:
                value = int(text)
                if value < 6:
                    value = 6
                elif value > 200:
                    value = 200
                self.font_size_spin.blockSignals(True)
                self.font_size_spin.setValue(value)
                self.font_size_spin.blockSignals(False)
                self._on_font_size_changed(value)
            except ValueError:
                pass
    
    def _on_font_size_changed(self, size):
        if self._font_size_editing:
            return
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        font = char_format.font()
        font.setPointSize(size)
        char_format.setFont(font)
        cursor.setCharFormat(char_format)
        self._emit_format_changed()
    
    def _on_bold_clicked(self, checked):
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        char_format.setFontWeight(QFont.Bold if checked else QFont.Normal)
        cursor.setCharFormat(char_format)
        self._emit_format_changed()
    
    def _on_italic_clicked(self, checked):
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        char_format.setFontItalic(checked)
        cursor.setCharFormat(char_format)
        self._emit_format_changed()
    
    def _on_underline_clicked(self, checked):
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        char_format.setFontUnderline(checked)
        cursor.setCharFormat(char_format)
        self._emit_format_changed()
    
    def _on_font_color_clicked(self):
        color = QColorDialog.getColor(self.font_color, self, "Select Font Color")
        if color.isValid():
            self.font_color = color
            self._update_font_color_button()
            if self.text_edit:
                cursor = self.text_edit.textCursor()
                char_format = cursor.charFormat()
                char_format.setForeground(color)
                cursor.setCharFormat(char_format)
                self._emit_format_changed()
    
    def _on_text_bg_color_clicked(self):
        color = QColorDialog.getColor(
            self.text_bg_color if self.text_bg_color else Qt.white,
            self, "Select Text Background Color"
        )
        if color.isValid():
            self.text_bg_color = color
            self._update_text_bg_color_button()
            if self.text_edit:
                cursor = self.text_edit.textCursor()
                char_format = cursor.charFormat()
                char_format.setBackground(color)
                cursor.setCharFormat(char_format)
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
            if self.text_edit:
                cursor = self.text_edit.textCursor()
                char_format = cursor.charFormat()
                char_format.setBackground(QBrush())
                char_format.clearBackground()
                cursor.setCharFormat(char_format)
                self._emit_format_changed()
    
    def _on_outline_clicked(self, checked):
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        
        if checked:
            pen = QPen(QColor(Qt.black))
            pen.setStyle(Qt.SolidLine)
            pen.setWidth(1)
            char_format.setTextOutline(pen)
        else:
            pen = QPen(Qt.NoPen)
            char_format.setTextOutline(pen)
        
        cursor.setCharFormat(char_format)
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
        self._apply_alignment()
    
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
        self._apply_alignment()
    
    def _apply_alignment(self):
        if not self.text_edit:
            return
        
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        
        block_format = cursor.blockFormat()
        block_format.setAlignment(self._horizontal_alignment)
        cursor.setBlockFormat(block_format)
        self._emit_format_changed()
    
    def _update_font_color_button(self):
        if self.font_color:
            self.font_color_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: #3B3B3B;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 12px;
                    color: {self.font_color.name()};
                }}
                QToolButton:hover {{
                    background-color: #4B4B4B;
                    border: 1px solid #4A90E2;
                }}
                QToolButton:pressed {{
                    background-color: #5B5B5B;
                }}
            """)
        else:
            self.font_color_btn.setStyleSheet("")
    
    def _update_text_bg_color_button(self):
        if self.text_bg_color:
            self.text_bg_color_btn.setText("BG")
            self.text_bg_color_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: #3B3B3B;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 12px;
                    color: {self.text_bg_color.name()};
                }}
                QToolButton:hover {{
                    background-color: #4B4B4B;
                    border: 1px solid #4A90E2;
                }}
                QToolButton:pressed {{
                    background-color: #5B5B5B;
                }}
            """)
        else:
            self.text_bg_color_btn.setText("BG")
            self.text_bg_color_btn.setStyleSheet("""
                QToolButton {
                    background-color: #3B3B3B;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 12px;
                    color: #FFFFFF;
                }
                QToolButton:hover {
                    background-color: #4B4B4B;
                    border: 1px solid #4A90E2;
                }
                QToolButton:pressed {
                    background-color: #5B5B5B;
                }
            """)
    
    def _emit_format_changed(self):
        if self._horizontal_alignment == Qt.AlignLeft:
            alignment_str = "left"
        elif self._horizontal_alignment == Qt.AlignHCenter:
            alignment_str = "center"
        elif self._horizontal_alignment == Qt.AlignRight:
            alignment_str = "right"
        
        if self._vertical_alignment == Qt.AlignTop:
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
