from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class PasswordDialog(QDialog):
    
    ADMIN_PASSWORD = "Starled-Italian@888"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Authentication")
        self.setModal(True)
        self.setMinimumWidth(350)
        self.password_correct = False
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("Enter Admin Password")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title_label)
        
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #FFFFFF; font-size: 11pt;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.on_ok)
        layout.addWidget(self.password_input)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.on_ok)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 11pt;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #555555;
                border-radius: 4px;
                font-size: 11pt;
                background-color: #3B3B3B;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
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
    
    def on_ok(self):
        password = self.password_input.text()
        if password == self.ADMIN_PASSWORD:
            self.password_correct = True
            self.accept()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Password", "Incorrect password. Please try again.")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def is_password_correct(self):
        return self.password_correct

