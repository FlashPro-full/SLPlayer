"""
Startup service - Handles application startup logic including license verification
"""
import sys
import base64
import json
from pathlib import Path
from typing import Optional, Tuple
from PyQt5.QtWidgets import QApplication, QMessageBox

from core.license_manager import LicenseManager
from core.license_verifier import LicenseVerifier
from utils.device_id import get_device_id
from utils.logger import get_logger

logger = get_logger(__name__)


class StartupService:
    """Handles application startup operations"""
    
    def __init__(self):
        self.license_manager = LicenseManager()
        self.verifier = LicenseVerifier()
        self.device_id = get_device_id()
    
    def verify_license_at_startup(self) -> Tuple[Optional[str], bool]:
        """
        Verify license at startup.
        
        Returns:
            Tuple of (controller_id, valid_license_found)
        """
        controller_id = None
        valid_license_found = False
        invalid_licenses = []
        
        try:
            license_dir = self.license_manager.license_dir
            if license_dir.exists():
                for license_file_path in license_dir.glob("*.slp"):
                    try:
                        license_data = self.verifier.parse_license_file(license_file_path)
                        if not license_data:
                            logger.warning(f"Could not parse license file: {license_file_path.name}")
                            continue
                        
                        if not self.verifier.verify_signature(license_data['payload'], license_data['signature']):
                            logger.warning(f"Invalid signature in license file: {license_file_path.name}")
                            invalid_licenses.append(license_file_path.stem)
                            continue
                        
                        payload_bytes = base64.b64decode(license_data['payload'])
                        payload_json = json.loads(payload_bytes.decode('utf-8'))
                        
                        license_controller_id = payload_json.get('controllerId')
                        license_device_id = payload_json.get('deviceId')
                        
                        if not license_controller_id:
                            logger.warning(f"No controllerId in license file: {license_file_path.name}")
                            invalid_licenses.append(license_file_path.stem)
                            continue
                        
                        if license_device_id != self.device_id:
                            logger.warning(
                                f"Device ID mismatch in license {license_file_path.name}: "
                                f"expected {self.device_id}, got {license_device_id}"
                            )
                            invalid_licenses.append(license_controller_id)
                            continue
                        
                        logger.info(f"Valid offline license found for controller: {license_controller_id}")
                        controller_id = license_controller_id
                        valid_license_found = True
                        break
                        
                    except Exception as e:
                        logger.warning(f"Error checking license file {license_file_path.name}: {e}")
                        invalid_licenses.append(license_file_path.stem)
            
            if invalid_licenses and not valid_license_found:
                invalid_list = ', '.join(invalid_licenses[:3])
                if len(invalid_licenses) > 3:
                    invalid_list += f" and {len(invalid_licenses) - 3} more"
                
                QMessageBox.warning(
                    None, "Invalid License",
                    "Invalid license detected. Please contact Starled Italia.\n\n"
                    f"Controllers: {invalid_list}\n\n"
                    "The license signature or device ID does not match.\n"
                    "Please activate a new license or contact support."
                )
                logger.info("Invalid licenses found - user must activate online")
        
        except Exception as e:
            logger.exception(f"Error during startup license verification: {e}")
        
        return controller_id, valid_license_found
    
    def check_license_after_activation(self, controller_id: Optional[str]) -> bool:
        """
        Check if license is valid after activation dialog.
        
        Args:
            controller_id: Controller ID to verify
            
        Returns:
            True if license is valid, False otherwise
        """
        if not controller_id:
            logger.error("No controller ID available - cannot verify license")
            return False
        
        try:
            if not self.license_manager.has_valid_license(controller_id):
                logger.error(f"License not valid for controller: {controller_id}")
                QMessageBox.critical(
                    None, "License Required",
                    "A valid license is required to use this application.\n\n"
                    f"Controller ID: {controller_id}\n\n"
                    "Please activate your license or contact support.\n\n"
                    "The application will now exit."
                )
                return False
            return True
        except Exception as e:
            logger.exception(f"License verification error: {e}")
            QMessageBox.critical(
                None, "License Verification Error",
                f"Error verifying license: {e}\n\n"
                "The application will now exit."
            )
            return False

