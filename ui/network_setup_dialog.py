"""
Network Setup Dialog - First launch network configuration
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkSetupDialog(QDialog):
    """Network setup dialog shown on first launch"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Setup - First Launch")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Welcome to SLPlayer")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(150)
        instructions.setText("""
<b>Network Setup Instructions:</b><br><br>
1. Make sure your PC is connected to the same network as your LED display controller.<br>
2. Connect your PC to the network via Ethernet or Wi-Fi.<br>
3. Ensure the controller is powered on and connected to the network.<br>
4. Click "Continue" to proceed to the main application.<br><br>
<i>You can discover and connect to controllers from the Control menu after starting the application.</i>
        """)
        instructions.setStyleSheet("background-color: #F5F5F5; border: 1px solid #CCCCCC; padding: 10px;")
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        continue_btn = QPushButton("Continue")
        continue_btn.setMinimumWidth(100)
        continue_btn.clicked.connect(self.accept)
        button_layout.addWidget(continue_btn)
        
        layout.addLayout(button_layout)
    
    def exec_(self):
        """Override exec_ to return result"""
        return super().exec_()

