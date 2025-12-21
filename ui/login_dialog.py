from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QCheckBox, QWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QEventLoop
from pathlib import Path
import json
from typing import Optional
from utils.logger import get_logger
from utils.app_data import get_credentials_file, ensure_app_data_dir
from ui.widgets.toast import ToastManager
from ui.widgets.loading_spinner import LoadingWidget
from services.controller_service import get_controller_service

logger = get_logger(__name__)


class ActivationThread(QThread):
    activation_complete = pyqtSignal(dict)
    
    def __init__(self, license_manager, controller_id: str, email: str, device_id: str):
        super().__init__()
        self.license_manager = license_manager
        self.controller_id = controller_id
        self.email = email
        self.device_id = device_id
    
    def run(self):
        try:
            result = self.license_manager.activate_license(
                self.controller_id, self.email, self.device_id
            )
            self.activation_complete.emit(result)
        except Exception as e:
            logger.exception(f"Error in activation thread: {e}")
            self.activation_complete.emit({
                'success': False,
                'code': 'THREAD_ERROR',
                'message': f'Activation error: {e}'
            })


class LicenseDialog(QDialog):
    
    def __init__(self, parent=None, controller_id: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("SLPlayer - License Activation")
        self.setMinimumWidth(450)
        self.setModal(True)
        self.license_valid = False
        self.controller_service = get_controller_service()
        self.activation_thread = None
        
        self.controller_id = controller_id
        self.init_ui()
        self.load_saved_email()
        
        if controller_id:
            self.check_license_status()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addSpacing(10)
        

        title_label = QLabel("License Activation")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title_label)
        
        layout.addSpacing(10)
        

        try:
            from utils.device_id import get_device_id
            current_device_id = get_device_id()
            
            device_layout = QVBoxLayout()
            device_layout.setContentsMargins(0, 0, 0, 0)
            device_layout.setSpacing(5)
            
            device_label = QLabel("PC Device ID:")
            device_layout.addWidget(device_label)
            
            device_id_label = QLabel(current_device_id)
            device_id_label.setStyleSheet("font-weight: bold; color: #4CAF50; font-size: 11pt; padding: 8px; background-color: #3B3B3B; border: 1px solid #555555; border-radius: 4px; font-family: monospace;")
            device_layout.addWidget(device_id_label)
            
            layout.addLayout(device_layout)
            layout.addSpacing(10)
        except Exception as e:
            logger.warning(f"Could not get device ID: {e}")
        

        controller_layout = QVBoxLayout()
        controller_layout.setContentsMargins(0, 0, 0, 0)
        controller_layout.setSpacing(5)
        
        controller_label = QLabel("Controller ID:")
        controller_layout.addWidget(controller_label)
        
        if self.controller_id:
            controller_id_label = QLabel(self.controller_id)
            controller_id_label.setStyleSheet("font-weight: bold; color: #4A90E2; font-size: 12pt; padding: 8px; background-color: #3B3B3B; border: 1px solid #555555; border-radius: 4px;")
        else:
            controller_id_label = QLabel("Not connected - No controller found on network")
            controller_id_label.setStyleSheet("font-weight: normal; color: #888888; font-size: 11pt; padding: 8px; background-color: #3B3B3B; border: 1px solid #555555; border-radius: 4px; font-style: italic;")
        
        controller_layout.addWidget(controller_id_label)
        self.controller_id_label = controller_id_label
        layout.addLayout(controller_layout)
        layout.addSpacing(10)
        

        email_label = QLabel("Email:")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        self.email_input.returnPressed.connect(self.on_activate_license)
        layout.addWidget(self.email_input)
        

        min_width = self.email_input.fontMetrics().boundingRect(self.email_input.placeholderText()).width() + 40
        self.email_input.setMinimumWidth(min_width)
        

        if self.controller_id:
            self.activation_section = QVBoxLayout()
            self.activation_section.setContentsMargins(0, 0, 0, 0)
            self.activation_section.setSpacing(10)
            
            self.activate_btn = QPushButton("Activate License")
            self.activate_btn.setDefault(True)
            self.activate_btn.clicked.connect(self.on_activate_license)
            self.activation_section.addWidget(self.activate_btn)
            
            self.activation_status = QLabel("")
            self.activation_status.setWordWrap(True)
            self.activation_status.setStyleSheet("color: #CCCCCC; font-size: 10pt;")
            self.activation_section.addWidget(self.activation_status)
            

            self.activation_loading = LoadingWidget(self, text="Activating license...")
            self.activation_section.addWidget(self.activation_loading, alignment=Qt.AlignCenter)
            
            layout.addLayout(self.activation_section)
        else:

            no_controller_info = QLabel(
                "To activate a license, you need to connect to a controller first.\n\n"
                "Please:\n"
                "1. Connect to your LED display controller\n"
                "2. Or discover controllers from the Control menu\n"
                "3. Then return here to activate your license"
            )
            no_controller_info.setWordWrap(True)
            no_controller_info.setStyleSheet("color: #CCCCCC; font-size: 10pt; padding: 10px; background-color: #3B3B3B; border: 1px solid #555555; border-radius: 4px;")
            layout.addWidget(no_controller_info)
        

        self.remember_check = QCheckBox("Remember email")
        self.remember_check.setChecked(True)
        layout.addWidget(self.remember_check)
        
        layout.addSpacing(10)
        

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if self.controller_id:

            pass
        else:

            close_btn = QPushButton("Close")
            close_btn.setMinimumWidth(100)
            close_btn.clicked.connect(self.reject)
            button_layout.addWidget(close_btn)
        
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
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QCheckBox {
                font-size: 10pt;
                color: #FFFFFF;
            }
        """)
    
    def load_saved_email(self):
        config_file = get_credentials_file()
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("remember", False):
                        if not self.email_input.text():
                            self.email_input.setText(data.get("email", ""))
                        self.remember_check.setChecked(True)
            except (json.JSONDecodeError, KeyError, TypeError, IOError):
                # Silently fail if credentials file is corrupted or missing
                pass
    
    def check_license_status(self):
        if not self.controller_id:



            return
        
        try:
            from core.license_manager import LicenseManager
            license_manager = LicenseManager()
            
            if license_manager.has_valid_license(self.controller_id):
                self.activation_status.setText("✓ License already activated")
                self.activation_status.setStyleSheet("color: #4CAF50; font-size: 10pt; font-weight: bold;")
                self.activate_btn.setEnabled(False)
                self.license_valid = True
                

                QTimer.singleShot(2000, self.accept)
            else:

                self.activation_status.setText("License not activated. Enter your email and click 'Activate License' to activate online.")
                self.activation_status.setStyleSheet("color: #FF9800; font-size: 10pt;")
        except Exception as e:
            logger.warning(f"Error checking license status: {e}")

            self.activation_status.setText("Could not check license status. Please connect to a controller and activate online.")
            self.activation_status.setStyleSheet("color: orange; font-size: 10pt;")
    
    def on_cancel_clicked(self):

        self.reject()
    
    def on_activate_license(self):
        if not self.controller_id:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "No Controller",
                "No controller ID available.\n\n"
                "To activate a license:\n"
                "1. Connect to your LED display controller\n"
                "2. Or discover controllers from the Control menu\n"
                "3. Then return here to activate your license"
            )
            return
        
        email = self.email_input.text().strip()
        if not email or '@' not in email:
            ToastManager.warning(self, "Please enter a valid email address", duration=3000)
            self.email_input.setFocus()
            return
        

        self.activate_btn.setEnabled(False)
        self.activation_loading.start()
        self.activation_status.setText("Activating license...")
        self.activation_status.setStyleSheet("color: #CCCCCC; font-size: 10pt;")
        
        try:
            from core.license_manager import LicenseManager
            from utils.device_id import get_device_id
            
            license_manager = LicenseManager()
            device_id = get_device_id()
            

            self.activation_thread = ActivationThread(
                license_manager, self.controller_id, email, device_id
            )
            self.activation_thread.activation_complete.connect(self.on_activation_complete)
            self.activation_thread.start()
        except Exception as e:
            self.activation_loading.stop()
            self.activate_btn.setEnabled(True)
            ToastManager.error(self, f"Could not start activation: {e}", duration=4000)
    
    def on_activation_complete(self, result: dict):
        self.activation_loading.stop()
        self.activate_btn.setEnabled(True)
        
        if result.get('success'):

            try:
                from core.license_manager import LicenseManager
                from utils.device_id import get_device_id
                
                license_manager = LicenseManager()
                device_id = get_device_id()
                
                if not self.controller_id:
                    logger.error("Cannot verify license: controller_id is None")
                    self.activation_status.setText("✗ License verification failed: No controller ID")
                    self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
                    return

                if license_manager.verify_license_offline(self.controller_id, device_id):
                    self.activation_status.setText("✓ License activated successfully!")
                    self.activation_status.setStyleSheet("color: #4CAF50; font-size: 10pt; font-weight: bold;")
                    self.activate_btn.setEnabled(False)
                    self.license_valid = True
                    

                    if self.remember_check.isChecked():
                        self.save_email()
                    
                    ToastManager.success(self, "License activated successfully!", duration=3000)
                    

                    QTimer.singleShot(1500, self.accept)
                else:

                    self.activation_status.setText("✗ License verification failed")
                    self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
                    ToastManager.error(
                        self,
                        "License was activated but verification failed. Please contact support.",
                        duration=5000
                    )
                    logger.error(f"License verification failed after activation for controller {self.controller_id}")
            except Exception as e:
                logger.exception(f"Error verifying license after activation: {e}")
                self.activation_status.setText("✗ License verification error")
                self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
                ToastManager.error(
                    self,
                    f"Error verifying license: {e}",
                    duration=5000
                )
        else:
            error_code = result.get('code', 'UNKNOWN')
            error_message = result.get('message', 'Unknown error')
            actions = result.get('actions', [])
            

            if error_code == 'TRANSFER_REQUIRED':
                ToastManager.warning(self, error_message, duration=5000)
                msg = f"{error_message}\n\nWould you like to request a transfer?"
                reply = QMessageBox.question(
                    self, "Transfer Required", msg,
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.request_transfer()
            
            elif error_code == 'DISPLAY_ALREADY_ASSIGNED':
                ToastManager.error(self, error_message, duration=5000)
                msg = f"{error_message}\n\n"
                if actions:
                    action_text = "\n".join([f"- {a.get('label', '')}" for a in actions])
                    msg += f"Available actions:\n{action_text}"
                
                QMessageBox.information(
                    self, "Display Already Assigned", msg,
                    QMessageBox.Ok
                )
                

                if actions:
                    for action in actions:
                        if action.get('type') == 'buy':

                            pass
            
            elif error_code == 'LICENSE_REVOKED':
                ToastManager.error(self, "License is revoked. Contact Starled Italia.", duration=5000)
                self.activation_status.setText("✗ License is revoked")
                self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
            elif error_code == 'NETWORK_ERROR':
                ToastManager.error(self, f"Network error: {error_message}", duration=5000)
                self.activation_status.setText(f"✗ Network error: {error_message}")
                self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
            elif error_code == 'SERVER_KEY_MISSING':
                ToastManager.error(self, "Server configuration error. Contact support.", duration=5000)
                self.activation_status.setText("✗ Server error")
                self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
            elif error_code == 'MISSING_PARAMS':
                ToastManager.warning(self, "Missing required information. Please check your input.", duration=4000)
                self.activation_status.setText("✗ Missing information")
                self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
            else:
                ToastManager.error(self, f"Activation failed: {error_message}", duration=5000)
                self.activation_status.setText(f"✗ Activation failed: {error_message}")
                self.activation_status.setStyleSheet("color: #F44336; font-size: 10pt;")
    
    def request_transfer(self):
        email = self.email_input.text().strip()
        if not email:
            ToastManager.warning(self, "Please enter your email address", duration=3000)
            return
        
        try:
            from core.license_manager import LicenseManager
            license_manager = LicenseManager()
            
            if license_manager.request_transfer(self.controller_id, email):
                ToastManager.success(
                    self,
                    "Transfer request has been sent. Please contact Starled Italia for approval.",
                    duration=5000
                )
            else:
                ToastManager.error(
                    self,
                    "Failed to send transfer request. Please try again or contact support.",
                    duration=5000
                )
        except Exception as e:
            ToastManager.error(self, f"Could not request transfer: {e}", duration=5000)
    
    def save_email(self):
        if not self.remember_check.isChecked():
            return
        
        ensure_app_data_dir()
        config_file = get_credentials_file()
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            credentials = {
                "email": self.email_input.text(),
                "remember": True
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save email: {e}")
    
    def get_email(self) -> str:
        return self.email_input.text()
    
    def is_license_valid(self) -> bool:
        return self.license_valid
    
    
    def _update_ui_for_controller(self):
        if self.controller_id:
            self.check_license_status()
            if hasattr(self, 'activation_section'):
                if hasattr(self, 'activate_btn'):
                    self.activate_btn.setEnabled(True)
                if hasattr(self, 'activation_status'):
                    self.activation_status.setText("License not activated. Enter your email and click 'Activate License' to activate online.")
                    self.activation_status.setStyleSheet("color: #FF9800; font-size: 10pt;")


LoginDialog = LicenseDialog
