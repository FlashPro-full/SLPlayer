"""
Network setup dialog for first launch
Guides user to connect PC to the same network as the display
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkSetupDialog(QDialog):
    """Dialog shown on first launch to guide network setup"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Setup - First Launch")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Welcome to SLPlayer!")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "To use SLPlayer, your PC must be connected to the same network\n"
            "as your LED display controller."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Steps
        steps_label = QLabel("Please follow these steps:")
        steps_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(steps_label)
        
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setMaximumHeight(150)
        steps_text.setHtml("""
        <ol>
            <li><b>Connect your PC to the same network</b> as your LED display controller</li>
            <li>This can be done via:
                <ul>
                    <li>Ethernet cable (recommended)</li>
                    <li>Wi-Fi connection</li>
                </ul>
            </li>
            <li>Ensure your PC and controller are on the same subnet</li>
            <li>Click "Discover Controllers" from the Control menu to find your display</li>
        </ol>
        """)
        layout.addWidget(steps_text)
        
        # Network info
        network_info = QLabel(
            "Tip: If you're not sure about the network setup, contact your\n"
            "system administrator or refer to the controller documentation."
        )
        network_info.setWordWrap(True)
        network_info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(network_info)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        skip_btn = QPushButton("Skip for Now")
        skip_btn.clicked.connect(self.on_skip)
        button_layout.addWidget(skip_btn)
        
        ok_btn = QPushButton("I Understand")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_skip(self):
        """Handle skip button"""
        reply = QMessageBox.question(
            self,
            "Skip Network Setup",
            "You can set up the network connection later.\n\n"
            "Do you want to continue without network setup?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.accept()

