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
from utils.app_data import get_licenses_dir, ensure_app_data_dir
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
            except (ImportError, AttributeError, KeyError):
                api_base_url = "https://www.starled-italia.com/license/api"
        
        self.api_base_url = api_base_url.rstrip('/')
        ensure_app_data_dir()  # Ensure base directory exists
        self.license_dir = get_licenses_dir()
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
        
        # Prepare request data - PHP backend uses $_REQUEST which reads form data
        # Backend expects: $_REQUEST['controllerId'], $_REQUEST['deviceId'], $_REQUEST['email']
        request_data = {
            'controllerId': controller_id,
            'deviceId': device_id,
            'email': email
        }
        
        try:
            # Call activation API
            api_url = f"{self.api_base_url}/slplayer_activate.php"
            logger.info(f"Activating license: controller={controller_id}, email={email}")
            
            # Display request on console
            print("\n" + "=" * 60)
            print("LICENSE ACTIVATION REQUEST")
            print("=" * 60)
            print(f"URL: {api_url}")
            print(f"Method: POST")
            print(f"Content-Type: application/x-www-form-urlencoded")
            print(f"\nForm Data (what PHP $_REQUEST will receive):")
            print(f"  controllerId: {controller_id}")
            print(f"  deviceId: {device_id}")
            print(f"  email: {email}")
            # Show URL-encoded format
            import urllib.parse
            url_encoded = urllib.parse.urlencode(request_data)
            print(f"\nURL-encoded format: {url_encoded}")
            print("=" * 60)
            
            # Send POST request with form data (PHP backend uses $_REQUEST for form data)
            # Backend logic: $_REQUEST['controllerId'] ?? $_REQUEST['controller_id'] ?? ''
            response = requests.post(
                api_url, 
                data=request_data,  # Form data - PHP $_REQUEST can read this
                timeout=10,
                headers={
                    'User-Agent': 'SLPlayer/1.0'
                }
            )
            
            # Parse response JSON once
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = None
            
            # Display response on console
            print("\n" + "=" * 60)
            print("LICENSE ACTIVATION RESPONSE")
            print("=" * 60)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            if result:
                print(f"Response Body (JSON):")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"Response Body (raw, first 500 chars):")
                print(response.text[:500])
            print("=" * 60 + "\n")
            
            # Backend returns 200 for all responses (even errors)
            # Errors are indicated by 'success': false in JSON body
            # Only 400/500 are actual HTTP errors
            if response.status_code == 400:
                # Missing parameters
                if result:
                    return {
                        'success': False,
                        'code': result.get('code', 'MISSING_PARAMS'),
                        'message': result.get('message', 'Missing required parameters')
                    }
                else:
                    return {
                        'success': False,
                        'code': 'MISSING_PARAMS',
                        'message': 'Missing required parameters'
                    }
            elif response.status_code == 500:
                # Server error (e.g., missing private key)
                if result:
                    return {
                        'success': False,
                        'code': result.get('code', 'SERVER_ERROR'),
                        'message': result.get('message', 'Server error')
                    }
                else:
                    return {
                        'success': False,
                        'code': 'SERVER_ERROR',
                        'message': 'Server error'
                    }
            
            # For 200 responses, check JSON success field
            if not result:
                return {
                    'success': False,
                    'code': 'INVALID_RESPONSE',
                    'message': 'Server returned invalid response format'
                }
            
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
            
            # Handle error cases (backend returns 200 with success: false for these)
            error_code = result.get('code', 'UNKNOWN_ERROR')
            error_message = result.get('message', 'Unknown error')
            actions = result.get('actions', [])
            
            return {
                'success': False,
                'code': error_code,
                'message': error_message,
                'actions': actions
            }
            
        except requests.exceptions.ConnectionError as e:
            logger.exception(f"Connection error during license activation: {e}")
            print("\n" + "=" * 60)
            print("CONNECTION ERROR")
            print("=" * 60)
            print(f"Error: Could not connect to license server")
            print(f"Details: {str(e)}")
            print(f"\nPossible causes:")
            print(f"  1. XAMPP server is not running")
            print(f"  2. PHP backend is not accessible at: {api_url}")
            print(f"  3. Database connection failed in PHP backend")
            print(f"  4. PHP script crashed (check XAMPP error logs)")
            print(f"  5. Missing private key file")
            print(f"\nTroubleshooting:")
            print(f"  - Check XAMPP Apache is running")
            print(f"  - Check XAMPP MySQL is running")
            print(f"  - Check XAMPP error logs: C:\\xampp\\apache\\logs\\error.log")
            print(f"  - Verify database credentials in: Admin SLPlayer/license/config/db.php")
            print(f"  - Test URL in browser: {api_url}")
            print("=" * 60 + "\n")
            return {
                'success': False,
                'code': 'NETWORK_ERROR',
                'message': f'Could not connect to license server. Make sure XAMPP is running and the backend is accessible at {api_url}'
            }
        except requests.exceptions.RequestException as e:
            logger.exception(f"Network error during license activation: {e}")
            print("\n" + "=" * 60)
            print("NETWORK ERROR")
            print("=" * 60)
            print(f"Error: {str(e)}")
            print(f"URL: {api_url}")
            print("=" * 60 + "\n")
            return {
                'success': False,
                'code': 'NETWORK_ERROR',
                'message': f'Network error: {e}'
            }
        except json.JSONDecodeError as e:
            logger.exception(f"Invalid JSON response from server: {e}")
            return {
                'success': False,
                'code': 'INVALID_RESPONSE',
                'message': 'Server returned invalid response format'
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
        
        NOTE: The backend does not provide a transfer_request endpoint.
        This method only sends an email to Starled Italia with transfer request details.
        
        Args:
            controller_id: Controller ID
            email: User email
            new_device_id: New device ID (auto-generated if not provided)
            note: Optional note/message for the transfer request
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        if new_device_id is None:
            new_device_id = get_device_id()
        
        try:
            logger.info(f"Transfer request: controller={controller_id}, email={email}, new_device={new_device_id}")
            
            # Backend does not provide transfer_request.php endpoint
            # Send email to Starled Italia for manual processing
            email_success = self._send_transfer_email(controller_id, email, new_device_id, note)
            
            return email_success
                
        except Exception as e:
            logger.exception(f"Error requesting transfer: {e}")
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
            except (ImportError, AttributeError, KeyError):
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

