"""
Tests for device ID generation
"""
import pytest
from utils.device_id import get_device_id, get_machine_id


def test_get_machine_id():
    """Test machine ID generation"""
    machine_id = get_machine_id()
    assert machine_id is not None
    assert isinstance(machine_id, str)
    assert machine_id.startswith("PC-")
    assert len(machine_id) > 3


def test_get_device_id():
    """Test device ID generation and persistence"""
    device_id = get_device_id()
    assert device_id is not None
    assert isinstance(device_id, str)
    assert device_id.startswith("PC-")
    
    # Should return same ID on second call
    device_id2 = get_device_id()
    assert device_id == device_id2


def test_device_id_persistence(tmp_path, monkeypatch):
    """Test that device ID is persisted across calls"""
    import utils.device_id
    from pathlib import Path
    
    # Mock the config directory
    config_dir = tmp_path / ".slplayer"
    config_dir.mkdir()
    
    # Patch the config directory path
    original_home = Path.home
    def mock_home():
        return tmp_path
    
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    # Get device ID (should create file)
    device_id1 = get_device_id()
    assert device_id1 is not None
    
    # Get device ID again (should read from file)
    device_id2 = get_device_id()
    assert device_id1 == device_id2
    
    # Verify file exists
    device_id_file = config_dir / "device_id.txt"
    assert device_id_file.exists()
    
    # Verify file content
    with open(device_id_file, 'r') as f:
        saved_id = f.read().strip()
    assert saved_id == device_id1

