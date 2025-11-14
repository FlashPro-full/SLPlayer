"""
Media library panel for browsing and managing media files
"""
from typing import Optional, List, Dict
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QGridLayout, QLineEdit, QComboBox,
                             QFileDialog, QMessageBox, QMenu, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QContextMenuEvent

from core.media_library import get_media_library
from utils.logger import get_logger

logger = get_logger(__name__)


class MediaThumbnailWidget(QWidget):
    """Widget for displaying a media file thumbnail"""
    
    clicked = pyqtSignal(str)  # Emits file path when clicked
    double_clicked = pyqtSignal(str)  # Emits file path when double-clicked
    
    def __init__(self, media_info: Dict, parent=None):
        super().__init__(parent)
        self.media_info = media_info
        self.file_path = media_info.get("file_path", "")
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Thumbnail image
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(150, 150)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #BDBDBD;
                background-color: #F5F5F5;
            }
        """)
        
        # Load thumbnail
        thumbnail_path = self.media_info.get("thumbnail_path")
        if thumbnail_path and Path(thumbnail_path).exists():
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    150, 150,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled)
            else:
                self.thumbnail_label.setText("No\nPreview")
        else:
            # Show file type icon
            file_type = self.media_info.get("file_type", "")
            if file_type == "image":
                self.thumbnail_label.setText("📷")
            elif file_type == "video":
                self.thumbnail_label.setText("🎬")
            else:
                self.thumbnail_label.setText("📄")
        
        layout.addWidget(self.thumbnail_label)
        
        # File name
        file_name = Path(self.file_path).name
        name_label = QLabel(file_name)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #424242;
            }
        """)
        layout.addWidget(name_label)
        
        # Set fixed size
        self.setFixedSize(160, 200)
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QWidget:hover {
                border: 2px solid #2196F3;
                background-color: #F5F5F5;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.file_path)
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.file_path)
        super().mouseDoubleClickEvent(event)


class MediaLibraryPanel(QWidget):
    """Media library panel for browsing media files"""
    
    media_selected = pyqtSignal(str)  # Emits file path when media is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_library = get_media_library()
        self.current_media_files: List[Dict] = []
        self.init_ui()
        self.refresh_media_list()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Media Library")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add media button
        add_btn = QPushButton("+ Add")
        add_btn.setToolTip("Add media files to library")
        add_btn.clicked.connect(self.on_add_media)
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 12px;
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        header_layout.addWidget(add_btn)
        
        # Scan directory button
        scan_btn = QPushButton("📁 Scan")
        scan_btn.setToolTip("Scan directory for media files")
        scan_btn.clicked.connect(self.on_scan_directory)
        scan_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 12px;
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """)
        header_layout.addWidget(scan_btn)
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Images", "Videos"])
        self.type_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.type_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.search_input)
        
        layout.addLayout(filter_layout)
        
        # Scroll area for thumbnails
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0;
                background-color: white;
            }
        """)
        
        self.thumbnails_widget = QWidget()
        self.thumbnails_layout = QGridLayout(self.thumbnails_widget)
        self.thumbnails_layout.setSpacing(10)
        self.thumbnails_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll.setWidget(self.thumbnails_widget)
        layout.addWidget(scroll)
        
        # Status label
        self.status_label = QLabel("0 media files")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #757575;
            }
        """)
        layout.addWidget(self.status_label)
    
    def refresh_media_list(self, file_type: Optional[str] = None, search_text: str = ""):
        """Refresh media list display"""
        # Clear existing thumbnails
        while self.thumbnails_layout.count():
            child = self.thumbnails_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get media files
        if file_type == "Images":
            media_type = "image"
        elif file_type == "Videos":
            media_type = "video"
        else:
            media_type = None
        
        self.current_media_files = self.media_library.get_media_files(
            file_type=media_type
        )
        
        # Filter by search text
        if search_text:
            search_lower = search_text.lower()
            self.current_media_files = [
                m for m in self.current_media_files
                if search_lower in Path(m["file_path"]).name.lower()
            ]
        
        # Create thumbnail widgets
        row = 0
        col = 0
        max_cols = 4
        
        for media_info in self.current_media_files:
            thumbnail_widget = MediaThumbnailWidget(media_info, self)
            thumbnail_widget.clicked.connect(self.on_thumbnail_clicked)
            thumbnail_widget.double_clicked.connect(self.on_thumbnail_double_clicked)
            self.thumbnails_layout.addWidget(thumbnail_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Update status
        count = len(self.current_media_files)
        self.status_label.setText(f"{count} media file{'s' if count != 1 else ''}")
    
    def on_add_media(self):
        """Add media files to library"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Add Media Files", "",
            "Media Files (*.png *.jpg *.jpeg *.gif *.bmp *.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        
        added_count = 0
        for file_path in file_paths:
            if self.media_library.add_media_file(file_path):
                added_count += 1
        
        if added_count > 0:
            self.refresh_media_list()
            QMessageBox.information(self, "Success", f"Added {added_count} media file(s) to library.")
        else:
            QMessageBox.warning(self, "Warning", "No files were added to the library.")
    
    def on_scan_directory(self):
        """Scan directory for media files"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if directory:
            count = self.media_library.scan_directory(directory, recursive=True)
            self.refresh_media_list()
            QMessageBox.information(self, "Scan Complete", f"Found and added {count} media file(s).")
    
    def on_filter_changed(self, text: str):
        """Handle filter change"""
        search_text = self.search_input.text()
        self.refresh_media_list(file_type=text, search_text=search_text)
    
    def on_search_changed(self, text: str):
        """Handle search text change"""
        filter_type = self.type_filter.currentText()
        self.refresh_media_list(file_type=filter_type, search_text=text)
    
    def on_thumbnail_clicked(self, file_path: str):
        """Handle thumbnail click"""
        self.media_library.update_usage(file_path)
        self.media_selected.emit(file_path)
    
    def on_thumbnail_double_clicked(self, file_path: str):
        """Handle thumbnail double click"""
        self.media_library.update_usage(file_path)
        self.media_selected.emit(file_path)

