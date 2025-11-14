"""
License manager for activation and management
Handles communication with license server and local license files
"""
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, List, Any
from utils.logger import get_logger
from utils.device_id import get_device_id
from core.license_verifier import LicenseVerifier

logger = get_logger(__name__)


class LicenseManager:
    """Manages license activation and verification"""
    
    def __init__(self, api_base_url: Optional[str] = None):
        """
        Initialize license manager.
        
        Args:
            api_base_url: Base URL for license API (defaults to Starled Italia server)
        """
        if api_base_url is None:
            # Default to Starled Italia server, but allow override via settings
            try:
                from config.settings import settings
                api_base_url = settings.get("license.api_url", "https://www.starled-italia.com/license/api")
            except:
                api_base_url = "https://www.starled-italia.com/license/api"
        
        self.api_base_url = api_base_url.rstrip('/')
        self.license_dir = Path.home() / ".slplayer" / "licenses"
        self.license_dir.mkdir(parents=True, exist_ok=True)
        self.verifier = LicenseVerifier()
    
    def get_license_file_path(self, controller_id: str) -> Path:
        """Get path to license file for a controller"""
        # Sanitize controller_id for filename
        safe_id = controller_id.replace('/', '_').replace('\\', '_')
        return self.license_dir / f"{safe_id}.slp"
    
    def activate_license(self, controller_id: str, email: str, 
                        device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Activate license with server.
        
        Args:
            controller_id: Controller ID from LED display
            email: User email
            device_id: Device ID (auto-generated if not provided)
        
        Returns:
            Dictionary with activation result:
            {
                'success': bool,
                'code': str (if error),
                'message': str,
                'license': dict (if success),
                'actions': list (if DISPLAY_ALREADY_ASSIGNED)
            }
        """
        if device_id is None:
            device_id = get_device_id()
        
        # Prepare request data
        data = {
            'controllerId': controller_id,
            'deviceId': device_id,
            'email': email
        }
        
        try:
            # Call activation API
            api_url = f"{self.api_base_url}/slplayer_activate.php"
            logger.info(f"Activating license: controller={controller_id}, email={email}")
            
            response = requests.post(api_url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle success
            if result.get('success'):
                license_data = result.get('license', {})
                if license_data:
                    # Save license file
                    if self.save_license_file(license_data, controller_id):
                        logger.info(f"License activated and saved for controller {controller_id}")
                        return {
                            'success': True,
                            'message': 'License activated successfully',
                            'license': license_data
                        }
                    else:
                        return {
                            'success': False,
                            'code': 'SAVE_FAILED',
                            'message': 'License activated but failed to save locally'
                        }
                else:
                    return {
                        'success': False,
                        'code': 'NO_LICENSE_DATA',
                        'message': 'Server returned success but no license data'
                    }
            
            # Handle error cases
            error_code = result.get('code', 'UNKNOWN_ERROR')
            error_message = result.get('message', 'Unknown error')
            actions = result.get('actions', [])
            
            return {
                'success': False,
                'code': error_code,
                'message': error_message,
                'actions': actions
            }
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"Network error during license activation: {e}")
            return {
                'success': False,
                'code': 'NETWORK_ERROR',
                'message': f'Could not connect to license server: {e}'
            }
        except Exception as e:
            logger.exception(f"Error activating license: {e}")
            return {
                'success': False,
                'code': 'ACTIVATION_ERROR',
                'message': f'License activation failed: {e}'
            }
    
    def save_license_file(self, license_data: Dict[str, str], controller_id: str) -> bool:
        """
        Save license file in .slp format.
        
        Format:
        -----BEGIN SLPLAYER LICENSE-----
        payload: <base64>
        signature: <base64>
        -----END SLPLAYER LICENSE-----
        """
        try:
            license_file = self.get_license_file_path(controller_id)
            
            payload = license_data.get('payload', '')
            signature = license_data.get('signature', '')
            
            if not payload or not signature:
                logger.error("License data missing payload or signature")
                return False
            
            # Write license file
            with open(license_file, 'w', encoding='utf-8') as f:
                f.write("-----BEGIN SLPLAYER LICENSE-----\n")
                f.write(f"payload: {payload}\n")
                f.write(f"signature: {signature}\n")
                f.write("-----END SLPLAYER LICENSE-----\n")
            
            logger.info(f"License file saved: {license_file}")
            return True
        except Exception as e:
            logger.exception(f"Error saving license file: {e}")
            return False
    
    def load_license_file(self, controller_id: str) -> Optional[Dict[str, str]]:
        """Load license file for a controller"""
        license_file = self.get_license_file_path(controller_id)
        return self.verifier.parse_license_file(license_file)
    
    def verify_license_offline(self, controller_id: str, device_id: Optional[str] = None) -> bool:
        """
        Verify license offline (without server connection).
        
        Args:
            controller_id: Controller ID to verify
            device_id: Device ID (auto-generated if not provided)
        
        Returns:
            True if license is valid and matches, False otherwise
        """
        if device_id is None:
            device_id = get_device_id()
        
        # Load license file
        license_data = self.load_license_file(controller_id)
        if not license_data:
            logger.warning(f"No license file found for controller {controller_id}")
            return False
        
        # Validate license
        return self.verifier.validate_license_data(license_data, controller_id, device_id)
    
    def get_controller_licenses(self) -> List[Dict[str, Any]]:
        """
        Get all stored licenses.
        
        Returns:
            List of license info dictionaries
        """
        licenses = []
        
        for license_file in self.license_dir.glob("*.slp"):
            try:
                license_data = self.verifier.parse_license_file(license_file)
                if license_data:
                    license_info = self.verifier.get_license_info(license_data)
                    if license_info:
                        licenses.append(license_info)
            except Exception as e:
                logger.warning(f"Error reading license file {license_file}: {e}")
        
        return licenses
    
    def request_transfer(self, controller_id: str, email: str, 
                        new_device_id: Optional[str] = None,
                        note: Optional[str] = None) -> bool:
        """
        Request license transfer to new device.
        
        Sends an email to Starled Italia with transfer request details.
        Also attempts to call transfer API endpoint if available.
        
        Args:
            controller_id: Controller ID
            email: User email
            new_device_id: New device ID (auto-generated if not provided)
            note: Optional note/message for the transfer request
        
        Returns:
            True if request was sent successfully, False otherwise
        """
        if new_device_id is None:
            new_device_id = get_device_id()
        
        try:
            logger.info(f"Transfer request: controller={controller_id}, email={email}, new_device={new_device_id}")
            
            # Try API endpoint first (if available)
            api_success = self._send_transfer_api_request(controller_id, email, new_device_id, note)
            
            # Always try email as well (more reliable)
            email_success = self._send_transfer_email(controller_id, email, new_device_id, note)
            
            # Return True if at least one method succeeded
            if api_success or email_success:
                logger.info("Transfer request sent successfully")
                return True
            else:
                logger.warning("Failed to send transfer request via both API and email")
                return False
                
        except Exception as e:
            logger.exception(f"Error requesting transfer: {e}")
            return False
    
    def _send_transfer_api_request(self, controller_id: str, email: str, 
                                   new_device_id: str, note: Optional[str]) -> bool:
        """
        Send transfer request via API endpoint (if available).
        
        Returns:
            True if API request succeeded, False otherwise
        """
        try:
            # Try to call transfer API endpoint
            transfer_url = f"{self.api_base_url}/transfer_request.php"
            
            data = {
                'controllerId': controller_id,
                'email': email,
                'deviceId': new_device_id,
                'note': note or ''
            }
            
            response = requests.post(transfer_url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info("Transfer request sent via API")
                    return True
        except requests.exceptions.RequestException:
            # API endpoint may not exist, that's okay
            pass
        except Exception as e:
            logger.debug(f"API transfer request failed (this is optional): {e}")
        
        return False
    
    def _send_transfer_email(self, controller_id: str, email: str, 
                             new_device_id: str, note: Optional[str]) -> bool:
        """
        Send transfer request via email to Starled Italia.
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from datetime import datetime
            
            # Get email configuration from settings
            try:
                from config.settings import settings
                smtp_server = settings.get("license.smtp_server", "smtp.gmail.com")
                smtp_port = settings.get("license.smtp_port", 587)
                smtp_user = settings.get("license.smtp_user", "")
                smtp_password = settings.get("license.smtp_password", "")
                transfer_email = settings.get("license.transfer_email", "license@starled-italia.com")
            except:
                # Use defaults if settings not available
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                smtp_user = ""
                smtp_password = ""
                transfer_email = "license@starled-italia.com"
            
            # If SMTP credentials not configured, try to send without authentication
            # (some SMTP servers allow this for specific domains)
            if not smtp_user or not smtp_password:
                logger.warning("SMTP credentials not configured. Email transfer request will be logged only.")
                # Log the request details for manual processing
                logger.info(f"""
                ===== LICENSE TRANSFER REQUEST =====
                Controller ID: {controller_id}
                User Email: {email}
                New Device ID: {new_device_id}
                Request Date: {datetime.now().isoformat()}
                Note: {note or 'No note provided'}
                ====================================
                """)
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = transfer_email
            msg['Subject'] = f"SLPlayer License Transfer Request - {controller_id}"
            
            # Email body
            body = f"""
License Transfer Request

Controller ID: {controller_id}
User Email: {email}
New Device ID: {new_device_id}
Request Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Note:
{note or 'No note provided'}

Please process this license transfer request.

This is an automated message from SLPlayer.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                server.quit()
                
                logger.info(f"Transfer request email sent successfully to {transfer_email}")
                return True
            except smtplib.SMTPAuthenticationError:
                logger.error("SMTP authentication failed. Please check SMTP credentials in settings.")
                return False
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error: {e}")
                return False
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                return False
                
        except ImportError:
            logger.warning("smtplib not available. Email transfer request cannot be sent.")
            return False
        except Exception as e:
            logger.exception(f"Error in email transfer request: {e}")
            return False
    
    def delete_license(self, controller_id: str) -> bool:
        """Delete license file for a controller"""
        try:
            license_file = self.get_license_file_path(controller_id)
            if license_file.exists():
                license_file.unlink()
                logger.info(f"License file deleted: {license_file}")
                return True
            return False
        except Exception as e:
            logger.exception(f"Error deleting license: {e}")
            return False
    
    def has_valid_license(self, controller_id: str) -> bool:
        """Check if controller has a valid license"""
        return self.verify_license_offline(controller_id)
    
    def get_license_info(self, controller_id: str) -> Optional[Dict[str, Any]]:
        """Get license information for a controller"""
        license_data = self.load_license_file(controller_id)
        if license_data:
            return self.verifier.get_license_info(license_data)
        return None

