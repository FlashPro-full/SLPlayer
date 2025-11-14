"""
Emoji picker dialog/widget for selecting emojis
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QScrollArea, QWidget, QGridLayout,
                             QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from typing import List, Dict
import emoji


class EmojiButton(QPushButton):
    """Button for displaying an emoji"""
    
    emoji_selected = pyqtSignal(str)
    
    def __init__(self, emoji_char: str, parent=None):
        super().__init__(parent)
        self.emoji_char = emoji_char
        self.setText(emoji_char)
        self.setFixedSize(40, 40)
        self.setFont(QFont("Segoe UI Emoji", 20))
        self.setToolTip(emoji.demojize(emoji_char))
        self.clicked.connect(lambda: self.emoji_selected.emit(emoji_char))
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border: 2px solid #2196F3;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)


class EmojiCategoryWidget(QWidget):
    """Widget for displaying emojis in a category"""
    
    emoji_selected = pyqtSignal(str)
    
    def __init__(self, emojis: List[str], parent=None):
        super().__init__(parent)
        self.emojis = emojis
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QGridLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Create buttons for each emoji
        row = 0
        col = 0
        max_cols = 10
        
        for emoji_char in self.emojis:
            btn = EmojiButton(emoji_char, self)
            btn.emoji_selected.connect(self.emoji_selected.emit)
            layout.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1


class EmojiPickerDialog(QDialog):
    """Dialog for picking emojis"""
    
    emoji_selected = pyqtSignal(str)
    
    # Emoji categories
    SMILEYS = ["😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃", 
               "😉", "😊", "😇", "🥰", "😍", "🤩", "😘", "😗", "😚", "😙",
               "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗", "🤭", "🤫", "🤔",
               "🤐", "🤨", "😐", "😑", "😶", "😏", "😒", "🙄", "😬", "🤥",
               "😌", "😔", "😪", "🤤", "😴", "😷", "🤒", "🤕", "🤢", "🤮"]
    
    GESTURES = ["👋", "🤚", "🖐", "✋", "🖖", "👌", "🤏", "✌️", "🤞", "🤟",
                "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "👍", "👎",
                "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝", "🙏"]
    
    PEOPLE = ["👶", "🧒", "👦", "👧", "🧑", "👱", "👨", "🧔", "👩", "🧓",
              "👴", "👵", "🙍", "🙎", "🙅", "🙆", "💁", "🙋", "🧏", "🙇",
              "🤦", "🤷", "👮", "🕵️", "💂", "🥷", "👷", "🤴", "👸", "👳"]
    
    ANIMALS = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
               "🦁", "🐮", "🐷", "🐽", "🐸", "🐵", "🙈", "🙉", "🙊", "🐒",
               "🐔", "🐧", "🐦", "🐤", "🐣", "🐥", "🦆", "🦅", "🦉", "🦇"]
    
    FOOD = ["🍏", "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🍈",
            "🍒", "🍑", "🥭", "🍍", "🥥", "🥝", "🍅", "🍆", "🥑", "🥦",
            "🥬", "🥒", "🌶", "🌽", "🥕", "🥔", "🍠", "🥐", "🥯", "🍞"]
    
    ACTIVITIES = ["⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱",
                  "🏓", "🏸", "🏒", "🏑", "🥍", "🏏", "🥅", "⛳", "🏹", "🎣",
                  "🥊", "🥋", "🎽", "🛹", "🛷", "⛸", "🥌", "🎿", "⛷", "🏂"]
    
    OBJECTS = ["⌚", "📱", "📲", "💻", "⌨️", "🖥", "🖨", "🖱", "🖲", "🕹",
               "🗜", "💾", "💿", "📀", "📼", "📷", "📸", "📹", "🎥", "📽",
               "🎞", "📞", "☎️", "📟", "📠", "📺", "📻", "🎙", "🎚", "🎛"]
    
    SYMBOLS = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
               "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️",
               "✝️", "☪️", "🕉", "☸️", "✡️", "🔯", "🕎", "☯️", "☦️", "🛐"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Emoji Picker")
        self.setMinimumSize(600, 500)
        self.selected_emoji = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search emojis...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tab widget for categories
        tabs = QTabWidget()
        
        # Create category tabs
        categories = [
            ("Smileys", self.SMILEYS),
            ("Gestures", self.GESTURES),
            ("People", self.PEOPLE),
            ("Animals", self.ANIMALS),
            ("Food", self.FOOD),
            ("Activities", self.ACTIVITIES),
            ("Objects", self.OBJECTS),
            ("Symbols", self.SYMBOLS),
        ]
        
        self.category_widgets = {}
        for name, emoji_list in categories:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            widget = EmojiCategoryWidget(emoji_list, self)
            widget.emoji_selected.connect(self.on_emoji_selected)
            scroll.setWidget(widget)
            tabs.addTab(scroll, name)
            self.category_widgets[name] = widget
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def on_search(self, text: str):
        """Filter emojis based on search text"""
        if not text:
            return
        
        # Simple search - filter by emoji name
        filtered = []
        for category_name, emoji_list in [
            ("Smileys", self.SMILEYS),
            ("Gestures", self.GESTURES),
            ("People", self.PEOPLE),
            ("Animals", self.ANIMALS),
            ("Food", self.FOOD),
            ("Activities", self.ACTIVITIES),
            ("Objects", self.OBJECTS),
            ("Symbols", self.SYMBOLS),
        ]:
            for emoji_char in emoji_list:
                emoji_name = emoji.demojize(emoji_char).lower()
                if text.lower() in emoji_name:
                    filtered.append(emoji_char)
        
        # Update first tab with filtered results
        if filtered and "Smileys" in self.category_widgets:
            # Create temporary widget for search results
            pass  # Could implement search results tab
    
    def on_emoji_selected(self, emoji_char: str):
        """Handle emoji selection"""
        self.selected_emoji = emoji_char
        self.emoji_selected.emit(emoji_char)
        self.accept()
    
    def get_selected_emoji(self) -> str:
        """Get the selected emoji"""
        return self.selected_emoji or ""


