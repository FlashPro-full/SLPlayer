"""
License verification module for RSA signature verification
"""
import base64
import json
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from utils.logger import get_logger

logger = get_logger(__name__)

_license_verifier_instance = None

class LicenseVerifier:
    def __new__(cls, public_key_path: Optional[Path] = None):
        global _license_verifier_instance
        if _license_verifier_instance is None:
            _license_verifier_instance = super(LicenseVerifier, cls).__new__(cls)
        return _license_verifier_instance
    
    def __init__(self, public_key_path: Optional[Path] = None):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        if public_key_path is None:
            import sys
            if getattr(sys, 'frozen', False):
                base_path = Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent.parent
            public_key_path = base_path / "resources" / "public.key"
        
        self.public_key_path = public_key_path
        self.public_key = None
        self._load_public_key()
    
    def _load_public_key(self):
        if not self.public_key_path or not self.public_key_path.exists():
            logger.warning(f"Public key not found at {self.public_key_path}")
            logger.warning("License verification will fail. Please add public.key to resources folder.")
            return
        
        try:
            with open(self.public_key_path, 'rb') as f:
                key_data = f.read()
            
            if b'Replace with actual public key' in key_data:
                logger.warning("Using example public key file. Please replace with actual key from server.")
                return
            
            self.public_key = load_pem_public_key(key_data, backend=default_backend())
            logger.info("Public key loaded successfully")
        except Exception as e:
            logger.exception(f"Error loading public key: {e}")
            self.public_key = None
    
    def verify_signature(self, payload: str, signature: str) -> bool:

        if not self.public_key:
            logger.error("Public key not loaded, cannot verify signature")
            return False
        
        try:
            payload_bytes = base64.b64decode(payload)
            signature_bytes = base64.b64decode(signature)
            
            self.public_key.verify(
                signature_bytes,
                payload_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            logger.info("License signature verified successfully")
            return True
        except Exception as e:
            logger.warning(f"License signature verification failed: {e}")
            return False
    
    def parse_license_file(self, file_path: Path) -> Optional[Dict[str, str]]:
        if not file_path.exists():
            logger.warning(f"License file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "-----BEGIN SLPLAYER LICENSE-----" not in content:
                logger.error("Invalid license file format: missing header")
                return None
            
            if "-----END SLPLAYER LICENSE-----" not in content:
                logger.error("Invalid license file format: missing footer")
                return None
            
            payload = None
            signature = None
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('payload:'):
                    payload = line.replace('payload:', '').strip()
                elif line.startswith('signature:'):
                    signature = line.replace('signature:', '').strip()
            
            if not payload or not signature:
                logger.error("License file missing payload or signature")
                return None
            
            return {
                'payload': payload,
                'signature': signature
            }
        except Exception as e:
            logger.exception(f"Error parsing license file: {e}")
            return None
    
    def validate_license_data(self, license_data: Dict[str, str], 
                             controller_id: str, device_id: str) -> bool:
        if not license_data or 'payload' not in license_data:
            return False
        
        if not self.verify_signature(license_data['payload'], license_data['signature']):
            return False
        
        try:
            payload_bytes = base64.b64decode(license_data['payload'])
            payload_json = json.loads(payload_bytes.decode('utf-8'))
            
            if payload_json.get('controllerId') != controller_id:
                logger.warning(f"Controller ID mismatch: expected {controller_id}, got {payload_json.get('controllerId')}")
                return False
            
            if payload_json.get('deviceId') != device_id:
                logger.warning(f"Device ID mismatch: expected {device_id}, got {payload_json.get('deviceId')}")
                return False
            
            if payload_json.get('product') != 'SLPlayer':
                logger.warning("Invalid product in license")
                return False
            
            logger.info("License data validated successfully")
            return True
        except Exception as e:
            logger.exception(f"Error validating license data: {e}")
            return False
    
    def get_license_info(self, license_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        if not license_data or 'payload' not in license_data:
            return None
        
        try:
            payload_bytes = base64.b64decode(license_data['payload'])
            payload_json = json.loads(payload_bytes.decode('utf-8'))
            return payload_json
        except Exception as e:
            logger.exception(f"Error extracting license info: {e}")
            return None

