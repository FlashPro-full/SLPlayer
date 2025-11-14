"""
Tests for base controller functionality
"""
import pytest
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from controllers.huidu import HuiduController
from controllers.novastar import NovaStarController


def test_controller_id_from_device_info():
    """Test controller ID extraction from device info"""
    # Create a mock controller
    controller = HuiduController("192.168.1.100")
    
    # Mock device_info
    controller.device_info = {
        "controller_id": "HD-M30-00123456",
        "device_name": "Test Display",
        "model": "HD-M30"
    }
    
    # Mock get_device_info to return our mock data
    original_get_info = controller.get_device_info
    controller.get_device_info = lambda: controller.device_info
    
    controller_id = controller.get_controller_id()
    assert controller_id == "HD-M30-00123456"


def test_controller_id_fallback_device_name_model():
    """Test controller ID fallback using device name and model"""
    controller = HuiduController("192.168.1.100")
    
    controller.device_info = {
        "device_name": "Test Display",
        "model": "HD-M30"
    }
    
    original_get_info = controller.get_device_info
    controller.get_device_info = lambda: controller.device_info
    
    controller_id = controller.get_controller_id()
    assert controller_id is not None
    assert "HD-M30" in controller_id
    assert "TEST-DISPLAY" in controller_id or "Test-Display" in controller_id


def test_controller_id_fallback_ip():
    """Test controller ID fallback using IP address"""
    controller = HuiduController("192.168.1.100")
    
    # No device info available
    controller.device_info = None
    original_get_info = controller.get_device_info
    controller.get_device_info = lambda: None
    
    controller_id = controller.get_controller_id()
    assert controller_id is not None
    assert "192-168-1-100" in controller_id or "HUIDU" in controller_id


def test_controller_connection_status():
    """Test controller connection status management"""
    controller = HuiduController("192.168.1.100")
    
    assert controller.status == ConnectionStatus.DISCONNECTED
    assert not controller.is_connected()
    
    controller.set_status(ConnectionStatus.CONNECTED)
    assert controller.status == ConnectionStatus.CONNECTED
    assert controller.is_connected()


def test_controller_type():
    """Test controller type assignment"""
    huidu = HuiduController("192.168.1.100")
    assert huidu.controller_type == ControllerType.HUIDU
    
    novastar = NovaStarController("192.168.1.100")
    assert novastar.controller_type == ControllerType.NOVASTAR

