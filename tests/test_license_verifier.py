"""
Tests for license verification
"""
import pytest
import base64
import json
from pathlib import Path
from core.license_verifier import LicenseVerifier


def test_parse_license_file_format(tmp_path):
    """Test parsing of license file format"""
    license_file = tmp_path / "test_license.slp"
    
    # Create a test license file
    test_payload = base64.b64encode(json.dumps({
        "controllerId": "TEST-123",
        "deviceId": "PC-TEST",
        "email": "test@example.com"
    }).encode()).decode()
    test_signature = base64.b64encode(b"fake_signature").decode()
    
    with open(license_file, 'w') as f:
        f.write("-----BEGIN SLPLAYER LICENSE-----\n")
        f.write(f"payload: {test_payload}\n")
        f.write(f"signature: {test_signature}\n")
        f.write("-----END SLPLAYER LICENSE-----\n")
    
    verifier = LicenseVerifier()
    license_data = verifier.parse_license_file(license_file)
    
    assert license_data is not None
    assert 'payload' in license_data
    assert 'signature' in license_data
    assert license_data['payload'] == test_payload
    assert license_data['signature'] == test_signature


def test_parse_license_file_missing(tmp_path):
    """Test parsing non-existent license file"""
    license_file = tmp_path / "nonexistent.slp"
    verifier = LicenseVerifier()
    license_data = verifier.parse_license_file(license_file)
    assert license_data is None


def test_parse_license_file_invalid_format(tmp_path):
    """Test parsing invalid license file format"""
    license_file = tmp_path / "invalid.slp"
    with open(license_file, 'w') as f:
        f.write("Invalid license file content")
    
    verifier = LicenseVerifier()
    license_data = verifier.parse_license_file(license_file)
    assert license_data is None


def test_get_license_info(tmp_path):
    """Test extracting license info from payload"""
    verifier = LicenseVerifier()
    
    # Create test license data
    test_data = {
        "controllerId": "TEST-123",
        "deviceId": "PC-TEST",
        "email": "test@example.com",
        "keyLicense": "SLP-2025-ABC",
        "issued_at": "2025-01-01T00:00:00Z",
        "product": "SLPlayer",
        "type": "perpetual"
    }
    
    payload = base64.b64encode(json.dumps(test_data).encode()).decode()
    license_data = {
        'payload': payload,
        'signature': base64.b64encode(b"fake").decode()
    }
    
    license_info = verifier.get_license_info(license_data)
    assert license_info is not None
    assert license_info['controllerId'] == "TEST-123"
    assert license_info['deviceId'] == "PC-TEST"
    assert license_info['email'] == "test@example.com"
    assert license_info['product'] == "SLPlayer"

