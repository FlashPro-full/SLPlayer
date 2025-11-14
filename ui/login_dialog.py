"""
Login dialog for user authentication and license validation
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QCheckBox,
                             QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
import json
from typing import Optional


class ActivationThread(QThread):
    """Thread for license activation to avoid blocking UI"""
    activation_complete = pyqtSignal(dict)
    
    def __init__(self, license_manager, controller_id: str, email: str, device_id: str):
        super().__init__()
        self.license_manager = license_manager
        self.controller_id = controller_id
        self.email = email
        self.device_id = device_id
    
    def run(self):
        """Run activation in background"""
        try:
            result = self.license_manager.activate_license(
                self.controller_id, self.email, self.device_id
            )
            self.activation_complete.emit(result)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error in activation thread: {e}")
            self.activation_complete.emit({
                'success': False,
                'code': 'THREAD_ERROR',
                'message': f'Activation error: {e}'
            })


class LoginDialog(QDialog):
    """Login dialog with user authentication and license activation"""
    
    def __init__(self, parent=None, controller_id: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("SLPlayer - Login")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.license_valid = False
        self.controller_id = controller_id
        self.activation_thread = None
        self.init_ui()
        self.load_saved_credentials()
        
        # Check if license activation is needed
        if controller_id:
            self.check_license_status()
    
    def init_ui(self):
        """Initialize login UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("SLPlayer")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("LED Display Controller Program Manager")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Username
        username_label = QLabel("Username:")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password:")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Email (for license activation)
        email_label = QLabel("Email:")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        layout.addWidget(self.email_input)
        
        # License activation section (shown if controller_id is provided)
        if self.controller_id:
            self.activation_section = QVBoxLayout()
            self.activation_label = QLabel(f"Controller ID: {self.controller_id}")
            self.activation_label.setStyleSheet("font-weight: bold; color: #2196F3;")
            self.activation_section.addWidget(self.activation_label)
            
            self.activate_btn = QPushButton("Activate License")
            self.activate_btn.clicked.connect(self.on_activate_license)
            self.activation_section.addWidget(self.activate_btn)
            
            self.activation_status = QLabel("")
            self.activation_status.setWordWrap(True)
            self.activation_status.setStyleSheet("color: #666; font-size: 10pt;")
            self.activation_section.addWidget(self.activation_status)
            
            self.activation_progress = QProgressBar()
            self.activation_progress.setVisible(False)
            self.activation_section.addWidget(self.activation_progress)
            
            layout.addLayout(self.activation_section)
        
        # Remember credentials
        self.remember_check = QCheckBox("Remember credentials")
        self.remember_check.setChecked(True)
        layout.addWidget(self.remember_check)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        login_btn = QPushButton("Login")
        login_btn.setDefault(True)
        login_btn.setMinimumWidth(100)
        login_btn.clicked.connect(self.on_login)
        button_layout.addWidget(login_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #333;
                font-size: 11pt;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #CCC;
                border-radius: 4px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QCheckBox {
                font-size: 10pt;
                color: #666;
            }
        """)
    
    def load_saved_credentials(self):
        """Load saved credentials if available"""
        config_file = Path.home() / ".slplayer" / "credentials.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("remember", False):
                        self.username_input.setText(data.get("username", ""))
                        self.password_input.setText(data.get("password", ""))
                        self.email_input.setText(data.get("email", ""))
                        self.remember_check.setChecked(True)
            except:
                pass
    
    def check_license_status(self):
        """Check if license already exists for this controller"""
        if not self.controller_id:
            return
        
        try:
            from core.license_manager import LicenseManager
            license_manager = LicenseManager()
            
            if license_manager.has_valid_license(self.controller_id):
                self.activation_status.setText("✓ License already activated")
                self.activation_status.setStyleSheet("color: green; font-size: 10pt;")
                self.activate_btn.setEnabled(False)
                self.license_valid = True
            else:
                self.activation_status.setText("License not activated. Please activate to continue.")
                self.activation_status.setStyleSheet("color: orange; font-size: 10pt;")
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Error checking license status: {e}")
    
    def on_activate_license(self):
        """Handle license activation"""
        if not self.controller_id:
            QMessageBox.warning(self, "No Controller", "No controller ID available")
            return
        
        email = self.email_input.text().strip()
        if not email or '@' not in email:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address")
            return
        
        # Disable button and show progress
        self.activate_btn.setEnabled(False)
        self.activation_progress.setVisible(True)
        self.activation_progress.setRange(0, 0)  # Indeterminate
        self.activation_status.setText("Activating license...")
        
        try:
            from core.license_manager import LicenseManager
            from utils.device_id import get_device_id
            
            license_manager = LicenseManager()
            device_id = get_device_id()
            
            # Start activation in background thread
            self.activation_thread = ActivationThread(
                license_manager, self.controller_id, email, device_id
            )
            self.activation_thread.activation_complete.connect(self.on_activation_complete)
            self.activation_thread.start()
        except Exception as e:
            self.activation_progress.setVisible(False)
            self.activate_btn.setEnabled(True)
            QMessageBox.warning(self, "Activation Error", f"Could not start activation: {e}")
    
    def on_activation_complete(self, result: dict):
        """Handle activation result"""
        self.activation_progress.setVisible(False)
        self.activate_btn.setEnabled(True)
        
        if result.get('success'):
            self.activation_status.setText("✓ License activated successfully!")
            self.activation_status.setStyleSheet("color: green; font-size: 10pt;")
            self.activate_btn.setEnabled(False)
            self.license_valid = True
            QMessageBox.information(self, "Success", "License activated successfully!")
        else:
            error_code = result.get('code', 'UNKNOWN')
            error_message = result.get('message', 'Unknown error')
            actions = result.get('actions', [])
            
            # Handle specific error codes
            if error_code == 'TRANSFER_REQUIRED':
                msg = f"{error_message}\n\nWould you like to request a transfer?"
                reply = QMessageBox.question(
                    self, "Transfer Required", msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.request_transfer()
            
            elif error_code == 'DISPLAY_ALREADY_ASSIGNED':
                msg = f"{error_message}\n\n"
                if actions:
                    action_text = "\n".join([f"- {a.get('label', '')}" for a in actions])
                    msg += f"Available actions:\n{action_text}"
                
                reply = QMessageBox.question(
                    self, "Display Already Assigned", msg,
                    QMessageBox.StandardButton.Ok
                )
                
                # Show actions if available
                if actions:
                    for action in actions:
                        if action.get('type') == 'buy':
                            # Could open URL in browser
                            pass
            
            elif error_code == 'LICENSE_REVOKED':
                QMessageBox.warning(self, "License Revoked", error_message)
            
            else:
                QMessageBox.warning(self, "Activation Failed", f"{error_code}: {error_message}")
            
            self.activation_status.setText(f"✗ Activation failed: {error_message}")
            self.activation_status.setStyleSheet("color: red; font-size: 10pt;")
    
    def request_transfer(self):
        """Request license transfer"""
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Email Required", "Please enter your email address")
            return
        
        try:
            from core.license_manager import LicenseManager
            license_manager = LicenseManager()
            
            if license_manager.request_transfer(self.controller_id, email):
                QMessageBox.information(
                    self, "Transfer Requested",
                    "Transfer request has been sent. Please contact Starled Italia for approval."
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not request transfer: {e}")
    
    def save_credentials(self):
        """Save credentials if remember is checked"""
        if not self.remember_check.isChecked():
            return
        
        config_file = Path.home() / ".slplayer" / "credentials.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "username": self.username_input.text(),
                    "password": self.password_input.text(),
                    "email": self.email_input.text(),
                    "remember": True
                }, f, indent=2)
        except:
            pass
    
    def on_login(self):
        """Handle login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Simple validation (can be enhanced with actual authentication)
        if not username:
            QMessageBox.warning(self, "Login Failed", "Please enter a username")
            return
        
        # Check license if controller_id is provided
        if self.controller_id:
            if not self.license_valid:
                # Check again in case it was just activated
                try:
                    from core.license_manager import LicenseManager
                    license_manager = LicenseManager()
                    if license_manager.has_valid_license(self.controller_id):
                        self.license_valid = True
                    else:
                        reply = QMessageBox.question(
                            self, "License Required",
                            "License not activated for this controller. Do you want to activate now?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            # Don't block here - let user activate in dialog
                            # They can try again after activation
                            pass
                        else:
                            QMessageBox.warning(
                                self, "License Required",
                                "You must activate a license to use SLPlayer with this controller."
                            )
                            return
                except Exception as e:
                    from utils.logger import get_logger
                    logger = get_logger(__name__)
                    logger.warning(f"License check error: {e}")
                    # Continue anyway (graceful degradation)
        
        # Save credentials if requested
        if self.remember_check.isChecked():
            self.save_credentials()
        
        self.accept()
    
    def get_username(self) -> str:
        """Get entered username"""
        return self.username_input.text()
    
    def get_email(self) -> str:
        """Get entered email"""
        return self.email_input.text()
    
    def is_license_valid(self) -> bool:
        """Check if license is valid"""
        return self.license_valid

