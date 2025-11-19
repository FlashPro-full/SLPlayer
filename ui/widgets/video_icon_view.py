from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QPushButton, QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor, QFont, QImage
from pathlib import Path
from typing import List, Dict, Optional


class VideoIconItem(QFrame):
    
    delete_requested = pyqtSignal(int)
    
    def __init__(self, video_path: str, index: int, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.index = index
        self.hovered = False
        self.setFixedSize(120, 140)
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
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
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
        
        self.trash_btn = QPushButton("×")
        self.trash_btn.setFixedSize(30, 30)
        self.trash_btn.hide()
        self.trash_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
            QPushButton:pressed {
                background-color: #CC0000;
            }
        """)
        self.trash_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        
        self.setLayout(layout)
        self.trash_btn.setParent(self)
        self.trash_btn.raise_()
        self.trash_btn.installEventFilter(self)
        
        thumbnail = self._get_video_thumbnail()
        if thumbnail:
            self.icon_label.setPixmap(thumbnail.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.icon_label.setText("No\nPreview")
    
    def _get_video_thumbnail(self) -> Optional[QPixmap]:
        if not self.video_path:
            return None
        
        try:
            from media.video_player import VideoPlayer
            thumbnail = VideoPlayer.get_video_thumbnail(self.video_path)
            if thumbnail and not thumbnail.isNull():
                return thumbnail
        except Exception:
            pass
        
        try:
            import cv2
            import numpy as np
            cap = cv2.VideoCapture(self.video_path)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_rgb = np.ascontiguousarray(frame_rgb)
                    height, width, channel = frame_rgb.shape
                    bytes_per_line = 3 * width
                    q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    q_image = q_image.copy()
                    return QPixmap.fromImage(q_image)
        except Exception:
            pass
        
        return None
    
    def enterEvent(self, event):
        self.hovered = True
        self.trash_btn.show()
        self.trash_btn.raise_()
        self.trash_btn.move(self.width() - 35, 5)
        self.trash_btn.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.hovered = False
        self.trash_btn.hide()
        super().leaveEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.hovered:
            self.trash_btn.move(self.width() - 35, 5)
            self.trash_btn.raise_()
    
    def eventFilter(self, obj, event):
        if obj == self.trash_btn:
            if event.type() == QEvent.MouseButtonPress:
                self.delete_requested.emit(self.index)
                event.accept()
                return True
        return False


class VideoIconView(QWidget):
    
    item_selected = pyqtSignal(int)
    item_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_items: List[VideoIconItem] = []
        self.video_data: List[Dict] = []
        self.items_per_row = 4
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
                background-color: #FFFFFF;
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
        self._update_display()
    
    def _create_new_row(self):
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row_layout.addStretch()
        self.grid_layout.addLayout(row_layout)
        self.current_row_layout = row_layout
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
        
        self._create_new_row()
        items_in_current_row = 0
        
        for i, video in enumerate(self.video_data):
            video_path = video.get("path", "")
            if video_path:
                if items_in_current_row >= self.items_per_row:
                    self._create_new_row()
                    items_in_current_row = 0
                
                item = VideoIconItem(video_path, i, self.grid_widget)
                item.delete_requested.connect(self._on_item_delete)
                
                def make_click_handler(idx):
                    def handler(event):
                        if hasattr(item, 'trash_btn') and item.trash_btn.isVisible():
                            trash_rect = item.trash_btn.geometry()
                            if trash_rect.contains(event.pos()):
                                return
                        self._on_item_clicked(idx)
                    return handler
                item.mousePressEvent = make_click_handler(i)
                self.video_items.append(item)
                
                self.current_row_layout.insertWidget(self.current_row_layout.count() - 1, item)
                items_in_current_row += 1
    
    def _on_item_clicked(self, index: int):
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
            self._update_display()
    
    def move_item_up(self, index: int):
        if index > 0:
            self.video_data[index], self.video_data[index - 1] = self.video_data[index - 1], self.video_data[index]
            self._update_display()
            return index - 1
        return index
    
    def move_item_down(self, index: int):
        if 0 <= index < len(self.video_data) - 1:
            self.video_data[index], self.video_data[index + 1] = self.video_data[index + 1], self.video_data[index]
            self._update_display()
            return index + 1
        return index
    
    def get_current_index(self) -> int:
        return -1
