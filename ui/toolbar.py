"""
Horizontal toolbar with content type buttons
"""
from PyQt6.QtWidgets import QToolButton, QMenu, QWidget, QHBoxLayout, QLabel, QWidgetAction
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QFont, QAction

from config.constants import ContentType


class Toolbar(QWidget):
    """Main toolbar with content type buttons - using QWidget for full control"""
    
    content_type_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Toolbar")
        
        # Create horizontal layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 1, 4, 1)
        self.layout.setSpacing(2)
        self.setMaximumHeight(32)
        
        # Set toolbar color to distinguish it from menubar and titlebar
        self.setStyleSheet("""
            QWidget {
                background-color: #D6D6D6;
            }
            QToolButton {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                padding: 2px 4px;
                margin: 0px;
            }
            QToolButton:hover {
                background-color: #F5F5F5;
                border: 1px solid #BDBDBD;
            }
            QToolButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        
        self.init_toolbar()
    
    def add_separator(self):
        """Add a visual separator"""
        separator = QLabel("|")
        separator.setStyleSheet("""
            QLabel {
                color: #000000;
                padding: 0px 2px;
                background-color: transparent;
            }
        """)
        self.layout.addWidget(separator)
    
    def init_toolbar(self):
        """Initialize toolbar buttons"""
        # Program Management
        program_btn = self.create_button("▶️ Program", ContentType.PROGRAM.value, "Program")
        self.layout.addWidget(program_btn)
        
        custom_area_btn = self.create_button("🏁 Custom Area", ContentType.CUSTOM_AREA.value, "Custom Area")
        self.layout.addWidget(custom_area_btn)
        
        self.add_separator()
        
        # Content Type Buttons - Show from Video to Digital Watch directly on toolbar
        visible_content_types = [
            ("🎞 Video", ContentType.VIDEO.value),
            ("🌄 Photo", ContentType.PHOTO.value),
            ("🔠 Text", ContentType.TEXT.value),
            ("🆕 SingleLineText", ContentType.SINGLE_LINE_TEXT.value),
            ("🎇 Animation", ContentType.ANIMATION.value),
            ("🧊 3D Text", ContentType.TEXT_3D.value),
            ("🕓 Clock", ContentType.CLOCK.value),
            ("🗓 Calendar", ContentType.CALENDAR.value),
            ("⌛️ Timing", ContentType.TIMING.value),
            ("🌦 Weather", ContentType.WEATHER.value),
            ("🩺 Sensor", ContentType.SENSOR.value),
            ("💡 Neon", ContentType.NEON.value),
            ("📚 WPS", ContentType.WPS.value),
            ("📅 Table", ContentType.TABLE.value),
            ("🗃 Office", ContentType.OFFICE.value),
            ("📟 Digital Watch", ContentType.DIGITAL_WATCH.value),
        ]
        
        for label, content_type in visible_content_types:
            btn = self.create_button(label, content_type, label)
            self.layout.addWidget(btn)
        
        self.add_separator()
        
        # "See More" button with overflow items
        self.more_btn = QToolButton()
        self.more_btn.setText("▼")
        self.more_btn.setToolTip("Show more toolbar items")
        more_font = QFont()
        more_font.setPixelSize(12)  # Slightly reduced from 18px
        # Removed bold to prevent shadow/duplication effect
        self.more_btn.setFont(more_font)
        # Set arrow type to NoArrow to prevent menu indicator
        self.more_btn.setArrowType(Qt.ArrowType.NoArrow)
        self.more_btn.setStyleSheet("""
            QToolButton {
                background-color: #CFD8DC;
                border: 1px solid #90A4AE;
                border-radius: 3px;
                padding: 2px;
                color: #37474F;
                min-width: 24px;
            }
            QToolButton:hover {
                background-color: #B0BEC5;
            }
            QToolButton:pressed {
                background-color: #90A4AE;
            }
            QToolButton::menu-indicator {
                image: none;
                border: none;
            }
        """)
        # Create and set the menu with remaining items
        overflow_menu = self.create_overflow_menu()
        if overflow_menu:
            self.more_btn.setMenu(overflow_menu)
            # Use InstantPopup so clicking shows menu immediately
            self.more_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.layout.addWidget(self.more_btn)
        
        # Add stretch at the end to push all items to the left
        self.layout.addStretch()
    
    def create_button(self, text: str, action: str, tooltip: str) -> QToolButton:
        """Create a toolbar button with larger emojis"""
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        
        # Set button font - increased to fill screen width
        button_font = QFont()
        button_font.setPixelSize(14)  # Slightly reduced from 16px
        btn.setFont(button_font)
        
        btn.clicked.connect(lambda: self.on_button_clicked(action))
        return btn
    
    def create_label(self, text: str):
        """Create a label widget"""
        from PyQt6.QtWidgets import QLabel
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumWidth(50)
        return label
    
    def create_menu_item_widget(self, label: str) -> QWidget:
        """Create a custom widget for menu item with larger emoji and smaller text"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QWidget:hover {
                background-color: #FFF3E0;
            }
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(4)
        
        # Split emoji and text
        parts = label.split(' ', 1)
        if len(parts) == 2:
            emoji = parts[0]
            text = parts[1]
            
            # Emoji label with 18px font
            emoji_label = QLabel(emoji)
            emoji_font = QFont()
            emoji_font.setPixelSize(18)
            emoji_label.setFont(emoji_font)
            emoji_label.setStyleSheet("background-color: transparent;")
            layout.addWidget(emoji_label)
            
            # Text label with 12px font
            text_label = QLabel(text)
            text_font = QFont()
            text_font.setPixelSize(12)
            text_label.setFont(text_font)
            text_label.setStyleSheet("background-color: transparent;")
            layout.addWidget(text_label)
        else:
            # No text, just emoji - make it larger
            emoji_label = QLabel(label)
            emoji_font = QFont()
            emoji_font.setPixelSize(18)
            emoji_label.setFont(emoji_font)
            emoji_label.setStyleSheet("background-color: transparent;")
            layout.addWidget(emoji_label)
        
        layout.addStretch()
        return widget
    
    def create_overflow_menu(self) -> QMenu:
        """Create overflow menu with remaining toolbar items"""
        menu = QMenu(self)
        menu.setTitle("More Tools")
        # Set font for menu to ensure emojis render properly
        menu_font = QFont()
        menu_font.setPixelSize(14)
        menu.setFont(menu_font)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #BDBDBD;
                font-size: 14px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E0E0E0;
                margin: 2px 0px;
            }
        """)
        
        # Add remaining content types (HTML, LiveStream, QR code, HDMI)
        remaining_content_types = [
            ("🌐 HTML", ContentType.HTML.value),
            ("🎥 LiveStream", ContentType.LIVESTREAM.value),
            ("🧿 QR code", ContentType.QR_CODE.value),
            ("🔌 HDMI", ContentType.HDMI.value),
        ]
        
        for label, content_type in remaining_content_types:
            widget = self.create_menu_item_widget(label)
            action = QWidgetAction(self)
            action.setDefaultWidget(widget)
            action.setData(content_type)
            action.triggered.connect(lambda checked, ct=content_type: self.on_menu_action(ct))
            menu.addAction(action)
        
        menu.addSeparator()
        
        # Add control actions
        control_actions = [
            ("⬇️ Send", "send"),
            ("🔗 To U-disk", "usb"),
            ("📲 Insert", "insert"),
            ("🧹 Clear program", "clear"),
        ]
        
        for label, action_name in control_actions:
            widget = self.create_menu_item_widget(label)
            action = QWidgetAction(self)
            action.setDefaultWidget(widget)
            action.setData(action_name)
            action.triggered.connect(lambda checked, an=action_name: self.on_menu_action(an))
            menu.addAction(action)
        
        menu.addSeparator()
        
        # Add navigation actions
        nav_actions = [
            ("⏮ First", "first"),
            ("◀️ Previous", "prev"),
            ("▶️ Next", "next"),
            ("⏭ Last", "last"),
        ]
        
        for label, action_name in nav_actions:
            widget = self.create_menu_item_widget(label)
            action = QWidgetAction(self)
            action.setDefaultWidget(widget)
            action.setData(action_name)
            action.triggered.connect(lambda checked, an=action_name: self.on_menu_action(an))
            menu.addAction(action)
        
        menu.addSeparator()
        
        # Add playback actions
        playback_actions = [
            ("▶️ Play", "play"),
            ("⏹ Stop", "stop"),
        ]
        
        for label, action_name in playback_actions:
            widget = self.create_menu_item_widget(label)
            action = QWidgetAction(self)
            action.setDefaultWidget(widget)
            action.setData(action_name)
            action.triggered.connect(lambda checked, an=action_name: self.on_menu_action(an))
            menu.addAction(action)
        
        menu.addSeparator()
        
        # Add system actions
        system_actions = [
            ("⚙️ Settings", "settings"),
            ("❓ Help", "help"),
            ("ℹ️ About", "about"),
        ]
        
        for label, action_name in system_actions:
            widget = self.create_menu_item_widget(label)
            action = QWidgetAction(self)
            action.setDefaultWidget(widget)
            action.setData(action_name)
            action.triggered.connect(lambda checked, an=action_name: self.on_menu_action(an))
            menu.addAction(action)
        
        return menu
    
    def on_menu_action(self, action_data):
        """Handle menu action click"""
        # Check if it's a content type
        content_types = [ct.value for ct in ContentType]
        if action_data in content_types:
            self.content_type_selected.emit(action_data)
        else:
            # Handle other actions
            print(f"Menu action: {action_data}")
    
    def on_button_clicked(self, action: str):
        """Handle button click"""
        # Check if it's a content type
        content_types = [ct.value for ct in ContentType]
        if action in content_types:
            self.content_type_selected.emit(action)
        else:
            # Handle other actions (send, play, stop, etc.)
            print(f"Action: {action}")

