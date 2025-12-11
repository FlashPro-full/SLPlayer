from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QPushButton, QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QPixmap, QImage
from pathlib import Path
from typing import List, Dict, Optional


class PhotoIconItem(QFrame):
    
    delete_requested = pyqtSignal(int)
    
    def __init__(self, photo_path: str, index: int, parent=None, is_active: bool = False):
        super().__init__(parent)
        self.photo_path = photo_path
        self.index = index
        self.hovered = False
        self.is_active = is_active
        self.setFixedSize(120, 140)
        self._update_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #2B2B2B;
                border: 1px solid #DDDDDD;
                border-radius: 2px;
            }
        """)
        
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #333333;
            }
        """)
        photo_name = Path(photo_path).stem if photo_path else "Photo"
        self.name_label.setText(photo_name[:15] + "..." if len(photo_name) > 15 else photo_name)
        
        self.active_btn = QPushButton("✓")
        self.active_btn.setFixedSize(30, 30)
        self.active_btn.setCheckable(True)
        self.active_btn.setChecked(is_active)
        self.active_btn.hide()
        self._update_active_btn_style()
        self.active_btn.clicked.connect(self._on_active_clicked)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        
        self.setLayout(layout)
        self.active_btn.setParent(self)
        self.active_btn.raise_()
        self.active_btn.installEventFilter(self)
        
        # Load thumbnail when item is created
        thumbnail = self._get_photo_thumbnail()
        if thumbnail:
            self.icon_label.setPixmap(thumbnail.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.icon_label.setText("No\nPreview")
    
    def _update_style(self):
        if self.is_active:
            self.setStyleSheet("""
                QFrame {
                    background-color: #E8F4F8;
                    border: 2px solid #4A90E2;
                    border-radius: 4px;
                }
                QFrame:hover {
                    background-color: #D0E8F2;
                    border: 2px solid #4A90E2;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5;
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                }
                QFrame:hover {
                    background-color: #EEEEEE;
                    border: 1px solid #999999;
                }
            """)
    
    def _update_active_btn_style(self):
        if self.is_active:
            self.active_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    border: 2px solid #2E5C8A;
                    border-radius: 15px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5BA0F2;
                }
                QPushButton:pressed {
                    background-color: #3A80D2;
                }
            """)
        else:
            self.active_btn.setStyleSheet("""
                QPushButton {
                    background-color: #CCCCCC;
                    border: 2px solid #999999;
                    border-radius: 15px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DDDDDD;
                }
                QPushButton:pressed {
                    background-color: #BBBBBB;
                }
            """)
    
    def set_active(self, active: bool):
        self.is_active = active
        self.active_btn.setChecked(active)
        self._update_style()
        self._update_active_btn_style()
    
    def _on_active_clicked(self):
        self.set_active(not self.is_active)
        
        thumbnail = self._get_photo_thumbnail()
        if thumbnail:
            self.icon_label.setPixmap(thumbnail.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.icon_label.setText("No\nPreview")
    
    def _get_photo_thumbnail(self) -> Optional[QPixmap]:
        if not self.photo_path:
            return None
        
        try:
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                return pixmap
        except Exception:
            pass
        
        try:
            image = QImage(self.photo_path)
            if not image.isNull():
                return QPixmap.fromImage(image)
        except Exception:
            pass
        
        return None
    
    def enterEvent(self, event):
        self.hovered = True
        self.active_btn.show()
        self.active_btn.raise_()
        self.active_btn.move(self.width() - 35, 5)
        self.active_btn.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.hovered = False
        if not self.is_active:
            self.active_btn.hide()
        else:
            self.active_btn.show()
            self.active_btn.raise_()
        super().leaveEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.hovered or self.is_active:
            self.active_btn.move(self.width() - 35, 5)
            self.active_btn.raise_()
    
    def eventFilter(self, obj, event):
        if obj == self.active_btn:
            if event.type() == QEvent.MouseButtonPress:
                self._on_active_clicked()
                event.accept()
                return True
        return False


class PhotoIconView(QWidget):
    
    item_selected = pyqtSignal(int)
    item_deleted = pyqtSignal(int)
    active_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photo_items: List[PhotoIconItem] = []
        self.photo_data: List[Dict] = []
        self.items_per_row = 4
        self.current_row = 0
        self.active_index = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #CCCCCC;
                background-color: #2B2B2B;
            }
        """)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(10)
        
        scroll_area.setWidget(self.grid_widget)
        layout.addWidget(scroll_area)
        self.setLayout(layout)
    
    def set_photos(self, photo_list: List[Dict]):
        self.photo_data = photo_list
        self._update_display()
    
    def _create_new_row(self):
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row_layout.addStretch()
        self.grid_layout.addLayout(row_layout, self.current_row, 0)
        self.current_row_layout = row_layout
        self.current_row += 1
        return row_layout
    
    def _update_display(self):
        for item in self.photo_items:
            item.deleteLater()
        self.photo_items.clear()
        
        while self.grid_layout.count() > 0:
            child = self.grid_layout.takeAt(0)
            if child.layout():
                while child.layout().count() > 0:
                    subchild = child.layout().takeAt(0)
                    if subchild.widget():
                        subchild.widget().deleteLater()
            elif child.widget():
                child.widget().deleteLater()
        
        self.current_row = 0
        self._create_new_row()
        items_in_current_row = 0
        
        for i, photo in enumerate(self.photo_data):
            photo_path = photo.get("path", "")
            if photo_path:
                if items_in_current_row >= self.items_per_row:
                    self._create_new_row()
                    items_in_current_row = 0
                
                is_active = (i == self.active_index)
                item = PhotoIconItem(photo_path, i, self.grid_widget, is_active=is_active)
                item.delete_requested.connect(self._on_item_delete)
                
                if is_active:
                    item.active_btn.show()
                    item.active_btn.raise_()
                    item.active_btn.move(item.width() - 35, 5)
                
                def make_click_handler(idx):
                    def handler(event):
                        if hasattr(item, 'active_btn') and item.active_btn.isVisible():
                            active_rect = item.active_btn.geometry()
                            if active_rect.contains(event.pos()):
                                return
                        self._on_item_clicked(idx)
                    return handler
                item.mousePressEvent = make_click_handler(i)
                self.photo_items.append(item)
                
                self.current_row_layout.insertWidget(self.current_row_layout.count() - 1, item)
                items_in_current_row += 1
    
    def _on_item_clicked(self, index: int):
        self.set_active_index(index)
        self.item_selected.emit(index)
    
    def _on_item_delete(self, index: int):
        self.item_deleted.emit(index)
    
    def clear(self):
        self.set_photos([])
    
    def add_item(self, photo_path: str):
        self.photo_data.append({"path": photo_path})
        self._update_display()
    
    def remove_item(self, index: int):
        if 0 <= index < len(self.photo_data):
            self.photo_data.pop(index)
            if len(self.photo_data) > 0:
                if self.active_index >= len(self.photo_data):
                    self.active_index = len(self.photo_data) - 1
                elif self.active_index > index:
                    self.active_index -= 1
            else:
                self.active_index = -1
            self._update_display()
    
    def move_item_up(self, index: int):
        if index > 0:
            self.photo_data[index], self.photo_data[index - 1] = self.photo_data[index - 1], self.photo_data[index]
            if self.active_index == index:
                self.active_index = index - 1
            elif self.active_index == index - 1:
                self.active_index = index
            self._update_display()
            self.active_changed.emit(self.active_index)
            return index - 1
        return index
    
    def move_item_down(self, index: int):
        if 0 <= index < len(self.photo_data) - 1:
            self.photo_data[index], self.photo_data[index + 1] = self.photo_data[index + 1], self.photo_data[index]
            if self.active_index == index:
                self.active_index = index + 1
            elif self.active_index == index + 1:
                self.active_index = index
            self._update_display()
            self.active_changed.emit(self.active_index)
            return index + 1
        return index
    
    def set_active_index(self, index: int):
        if 0 <= index < len(self.photo_data):
            old_active = self.active_index
            self.active_index = index
            if old_active < len(self.photo_items):
                self.photo_items[old_active].set_active(False)
                self.photo_items[old_active].active_btn.hide()
            if index < len(self.photo_items):
                self.photo_items[index].set_active(True)
                self.photo_items[index].active_btn.show()
                self.photo_items[index].active_btn.raise_()
                self.photo_items[index].active_btn.move(self.photo_items[index].width() - 35, 5)
            self.active_changed.emit(self.active_index)
    
    def get_active_index(self) -> int:
        return self.active_index
    
    def get_current_index(self) -> int:
        return -1

