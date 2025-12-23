from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from utils.logger import get_logger

logger = get_logger(__name__)


class DownloadDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Programs")
        self.setMinimumWidth(400)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 11pt;
            }
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                background-color: #4A90E2;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
        """)
        
        self.result = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        message_label = QLabel("Do you want to download programs from the device?")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        yes_btn = QPushButton("Yes")
        yes_btn.clicked.connect(lambda: self.accept_with_result(True))
        button_layout.addWidget(yes_btn)
        
        no_btn = QPushButton("No")
        no_btn.clicked.connect(lambda: self.accept_with_result(False))
        button_layout.addWidget(no_btn)
        
        layout.addLayout(button_layout)
    
    def accept_with_result(self, result: bool):
        self.result = result
        self.accept()
    
    @staticmethod
    def ask_download(parent=None) -> bool:
        dialog = DownloadDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog.result if dialog.result is not None else False
        return False

