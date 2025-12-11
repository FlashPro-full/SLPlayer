from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QPushButton, QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor, QFont, QImage
from pathlib import Path
from typing import List, Dict, Optional


class VideoIconItem(QFrame):
    
    delete_requested = pyqtSignal(int)
    
    def __init__(self, video_path: str, index: int, parent=None, is_active: bool = False):
        super().__init__(parent)
        self.video_path = video_path
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
        video_name = Path(video_path).stem if video_path else "Video"
        self.name_label.setText(video_name[:15] + "..." if len(video_name) > 15 else video_name)
        
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
        self._load_video_thumbnail()
    
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
        
        thumbnail = self._get_video_thumbnail()
        if thumbnail and not thumbnail.isNull():
            scaled_thumbnail = thumbnail.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_thumbnail)
            self.icon_label.setText("")
        else:
            self.icon_label.clear()
            self.icon_label.setText("No\nPreview")
    
    def _load_video_thumbnail(self):
        """Load video thumbnail and display it, saving to temp file if needed"""
        thumbnail = self._get_video_thumbnail()
        if thumbnail and not thumbnail.isNull():
            scaled_thumbnail = thumbnail.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_thumbnail)
            self.icon_label.setText("")
        else:
            self.icon_label.clear()
            self.icon_label.setText("No\nPreview")
    
    def _get_video_thumbnail(self) -> Optional[QPixmap]:
        if not self.video_path:
            return None
        
        video_file = Path(self.video_path)
        if not video_file.exists():
            return None
        
        # Check if thumbnail already exists in temp file
        import tempfile
        import hashlib
        import os
        
        # Create a hash-based filename for the thumbnail
        video_hash = hashlib.md5(str(video_file).encode()).hexdigest()
        temp_dir = tempfile.gettempdir()
        thumbnail_path = os.path.join(temp_dir, f"slplayer_video_thumb_{video_hash}.jpg")
        
        # If thumbnail file exists, load it
        if os.path.exists(thumbnail_path):
            try:
                pixmap = QPixmap(thumbnail_path)
                if not pixmap.isNull():
                    return pixmap
            except Exception:
                pass
        
        # Generate thumbnail from video
        from media.video_player import VideoPlayer
        thumbnail = VideoPlayer.get_video_thumbnail(str(video_file), frame_time=1.0)
        
        # Save thumbnail to temp file
        if thumbnail and not thumbnail.isNull():
            try:
                thumbnail.save(thumbnail_path, "JPG")
            except Exception:
                pass
        
        return thumbnail
    
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


class VideoIconView(QWidget):
    
    item_selected = pyqtSignal(int)
    item_deleted = pyqtSignal(int)
    active_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_items: List[VideoIconItem] = []
        self.video_data: List[Dict] = []
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
    
    def set_videos(self, video_list: List[Dict]):
        self.video_data = video_list
        if len(video_list) > 0:
            self.active_index = 0
        else:
            self.active_index = -1
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
        for item in self.video_items:
            item.deleteLater()
        self.video_items.clear()

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

        for i, video in enumerate(self.video_data):
            video_path = video.get("path", "")
            if video_path:
                if items_in_current_row >= self.items_per_row:
                    self._create_new_row()
                    items_in_current_row = 0
                
                is_active = (i == self.active_index)
                item = VideoIconItem(video_path, i, self.grid_widget, is_active=is_active)
                item.delete_requested.connect(self._on_item_delete)
                # Ensure thumbnail is loaded and displayed
                item._load_video_thumbnail()

                def make_click_handler(idx):
                    def handler(event):
                        if hasattr(item, 'active_btn') and item.active_btn.isVisible():
                            active_rect = item.active_btn.geometry()
                            if active_rect.contains(event.pos()):
                                return
                        self._on_item_clicked(idx)
                    return handler
                item.mousePressEvent = make_click_handler(i)
                self.video_items.append(item)

                self.current_row_layout.insertWidget(self.current_row_layout.count() - 1, item)
                items_in_current_row += 1
    
    def _on_item_clicked(self, index: int):
        self.set_active_index(index)
        self.item_selected.emit(index)
    
    def _on_item_delete(self, index: int):
        self.item_deleted.emit(index)
    
    def clear(self):
        self.set_videos([])
    
    def add_item(self, video_path: str):
        self.video_data.append({"path": video_path})
        self._update_display()
    
    def remove_item(self, index: int):
        if 0 <= index < len(self.video_data):
            self.video_data.pop(index)
            if len(self.video_data) > 0:
                if self.active_index >= len(self.video_data):
                    self.active_index = len(self.video_data) - 1
                elif self.active_index > index:
                    self.active_index -= 1
            else:
                self.active_index = -1
            self._update_display()
    
    def move_item_up(self, index: int):
        if index > 0:
            self.video_data[index], self.video_data[index - 1] = self.video_data[index - 1], self.video_data[index]
            if self.active_index == index:
                self.active_index = index - 1
            elif self.active_index == index - 1:
                self.active_index = index
            self._update_display()
            self.active_changed.emit(self.active_index)
            return index - 1
        return index
    
    def move_item_down(self, index: int):
        if 0 <= index < len(self.video_data) - 1:
            self.video_data[index], self.video_data[index + 1] = self.video_data[index + 1], self.video_data[index]
            if self.active_index == index:
                self.active_index = index + 1
            elif self.active_index == index + 1:
                self.active_index = index
            self._update_display()
            self.active_changed.emit(self.active_index)
            return index + 1
        return index
    
    def set_active_index(self, index: int):
        if 0 <= index < len(self.video_data):
            old_active = self.active_index
            self.active_index = index
            if old_active < len(self.video_items):
                self.video_items[old_active].set_active(False)
                self.video_items[old_active].active_btn.hide()
            if index < len(self.video_items):
                self.video_items[index].set_active(True)
                self.video_items[index].active_btn.show()
                self.video_items[index].active_btn.raise_()
                self.video_items[index].active_btn.move(self.video_items[index].width() - 35, 5)
            self.active_changed.emit(self.active_index)
    
    def get_active_index(self) -> int:
        return self.active_index
    
    def get_current_index(self) -> int:
        return -1
