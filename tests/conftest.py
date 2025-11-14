"""
Pytest configuration and fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for tests"""
    config_dir = tmp_path / ".slplayer"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def sample_program_data():
    """Sample program data for testing"""
    return {
        "version": "1.0",
        "metadata": {
            "name": "Test Program",
            "created": "2024-01-01T00:00:00",
            "modified": "2024-01-01T00:00:00",
            "resolution": {
                "width": 1920,
                "height": 1080
            }
        },
        "elements": [],
        "schedule": {
            "enabled": False,
            "rules": []
        }
    }


@pytest.fixture
def mock_controller_info():
    """Mock controller device info"""
    return {
        "controller_id": "HD-M30-00123456",
        "device_name": "Test Display",
        "model": "HD-M30",
        "firmware": "1.0.0",
        "ip_address": "192.168.1.100",
        "resolution": {
            "width": 1920,
            "height": 1080
        }
    }

