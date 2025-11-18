"""
Video icon view widget - displays videos as large icons with hover trash button
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor, QFont
from pathlib import Path
from typing import List, Dict, Optional


class VideoIconItem(QFrame):
    """Single video icon item with hover trash button"""
    
    delete_requested = pyqtSignal(int)  # Emits index when delete is clicked
    
    def __init__(self, video_path: str, index: int, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.index = index
        self.hovered = False
        self.setFixedSize(120, 140)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
            QFrame:hover {
                background-color: #F0F0F0;
                border: 1px solid #4A90E2;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the icon item UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Icon area
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 1px solid #DDDDDD;
                border-radius: 2px;
            }
        """)
        
        # Try to load video icon or use default
        icon_path = self._get_video_icon()
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_label.setPixmap(scaled)
            else:
                self.icon_label.setText("🎬")
        else:
            self.icon_label.setText("🎬")
        
        layout.addWidget(self.icon_label)
        
        # File name label
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumHeight(30)
        file_name = Path(self.video_path).name if self.video_path else "Unknown"
        self.name_label.setText(file_name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #333333;
            }
        """)
        layout.addWidget(self.name_label)
        
        # Trash button (always visible)
        self.trash_btn = QPushButton("🗑")
        self.trash_btn.setFixedSize(30, 30)
        self.trash_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
            QPushButton:pressed {
                background-color: #CC0000;
            }
        """)
        # Use a closure to properly capture the index
        def make_delete_handler(idx):
            def handler():
                self.delete_requested.emit(idx)
            return handler
        self.trash_btn.clicked.connect(make_delete_handler(self.index))
        self.trash_btn.setParent(self)
        # Ensure trash button is always on top and visible
        self.trash_btn.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.trash_btn.show()  # Always show the button
        self.trash_btn.raise_()
        # Position the button in top-right corner
        self.trash_btn.move(self.width() - 35, 5)
        # Make sure trash button doesn't propagate clicks
        # Prevent trash button clicks from propagating to parent
        self.trash_btn.installEventFilter(self)
    
    def _get_video_icon(self) -> Optional[str]:
        """Get icon for video file - could be thumbnail or default icon"""
        # For now, return None to use default emoji
        # Could be extended to extract video thumbnail
        return None
    
    def enterEvent(self, event):
        """Handle hover - ensure trash button is visible"""
        self.hovered = True
        self.trash_btn.show()
        self.trash_btn.raise_()  # Ensure it's on top
        self.trash_btn.move(self.width() - 35, 5)
        self.trash_btn.update()  # Force update to ensure visibility
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle leave - keep trash button visible"""
        self.hovered = False
        # Keep trash button visible (don't hide it)
        self.trash_btn.show()
        super().leaveEvent(event)
    
    def resizeEvent(self, event):
        """Update trash button position on resize"""
        super().resizeEvent(event)
        self.trash_btn.move(self.width() - 35, 5)
        self.trash_btn.raise_()  # Ensure it stays on top
        self.trash_btn.show()  # Ensure it's visible
    
    def eventFilter(self, obj, event):
        """Filter events to prevent trash button clicks from propagating"""
        if obj == self.trash_btn:
            if event.type() == QEvent.MouseButtonPress:
                # Let the button handle it, but don't propagate to parent
                event.accept()
                return False  # Let button process it
        return False


class VideoIconView(QWidget):
    """Video list displayed as large icons in a grid"""
    
    item_selected = pyqtSignal(int)
    item_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_items: List[VideoIconItem] = []
        self.video_data: List[Dict] = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the icon view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for the icon grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #CCCCCC;
                background-color: #F9F9F9;
            }
        """)
        
        # Container widget for the grid
        self.grid_widget = QWidget()
        self.grid_layout = QVBoxLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(10)
        
        # Create rows for wrapping items
        self.current_row_layout = None
        self.items_per_row = 4  # Number of items per row
        self._create_new_row()
        
        scroll_area.setWidget(self.grid_widget)
        layout.addWidget(scroll_area)
    
    def set_videos(self, video_list: List[Dict]):
        """Set the list of videos to display"""
        self.video_data = video_list
        self._update_display()
    
    def _create_new_row(self):
        """Create a new row layout for items"""
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row_layout.addStretch()
        self.grid_layout.addLayout(row_layout)
        self.current_row_layout = row_layout
        return row_layout
    
    def _update_display(self):
        """Update the icon display"""
        # Clear existing items
        for item in self.video_items:
            item.deleteLater()
        self.video_items.clear()
        
        # Clear all layouts
        while self.grid_layout.count() > 0:
            child = self.grid_layout.takeAt(0)
            if child.layout():
                while child.layout().count() > 0:
                    subchild = child.layout().takeAt(0)
                    if subchild.widget():
                        subchild.widget().deleteLater()
            elif child.widget():
                child.widget().deleteLater()
        
        # Reset row tracking
        self._create_new_row()
        items_in_current_row = 0
        
        # Create icon items
        for i, video in enumerate(self.video_data):
            video_path = video.get("path", "")
            if video_path:
                # Create new row if current row is full
                if items_in_current_row >= self.items_per_row:
                    self._create_new_row()
                    items_in_current_row = 0
                
                item = VideoIconItem(video_path, i, self.grid_widget)
                item.delete_requested.connect(self._on_item_delete)
                # Use a closure to properly capture the index
                def make_click_handler(idx):
                    def handler(event):
                        # Don't trigger if clicking on trash button
                        if hasattr(item, 'trash_btn') and item.trash_btn.isVisible():
                            # Check if click is on trash button area
                            trash_rect = item.trash_btn.geometry()
                            if trash_rect.contains(event.pos()):
                                return  # Let trash button handle it
                        self._on_item_clicked(idx)
                    return handler
                item.mousePressEvent = make_click_handler(i)
                self.video_items.append(item)
                
                # Insert before stretch
                self.current_row_layout.insertWidget(self.current_row_layout.count() - 1, item)
                items_in_current_row += 1
    
    def _on_item_clicked(self, index: int):
        """Handle item click"""
        self.item_selected.emit(index)
    
    def _on_item_delete(self, index: int):
        """Handle item delete request"""
        self.item_deleted.emit(index)
    
    def clear(self):
        """Clear all items"""
        self.set_videos([])
    
    def add_item(self, video_path: str):
        """Add a new video item"""
        self.video_data.append({"path": video_path})
        self._update_display()
    
    def remove_item(self, index: int):
        """Remove an item at index"""
        if 0 <= index < len(self.video_data):
            self.video_data.pop(index)
            self._update_display()
    
    def move_item_up(self, index: int):
        """Move item up in the list"""
        if index > 0:
            self.video_data[index], self.video_data[index - 1] = self.video_data[index - 1], self.video_data[index]
            self._update_display()
            return index - 1
        return index
    
    def move_item_down(self, index: int):
        """Move item down in the list"""
        if 0 <= index < len(self.video_data) - 1:
            self.video_data[index], self.video_data[index + 1] = self.video_data[index + 1], self.video_data[index]
            self._update_display()
            return index + 1
        return index
    
    def get_current_index(self) -> int:
        """Get currently selected index"""
        # For now, return -1 (no selection)
        # Could be extended to track selection
        return -1

