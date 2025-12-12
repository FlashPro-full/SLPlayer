import sys
import atexit
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from config.settings import settings
from core.startup_service import StartupService
from utils.logger import get_logger
from utils.icon_manager import IconManager

logger = get_logger(__name__)

def cleanup_api_server():
    try:
        from controllers.huidu_sdk import _stop_api_server
        _stop_api_server()
    except Exception as e:
        logger.error(f"Error stopping API server during cleanup: {e}")

atexit.register(cleanup_api_server)


def main():
    try:
        if "--reset-first-launch" in sys.argv or "--reset-first" in sys.argv:
            settings.set("first_launch_complete", False)
            print("✓ First launch flag has been reset!")
            print("The Network Setup Dialog will appear on next application start.")
            return
        
        skip_license = "--skip-license" in sys.argv or "--skip-lic" in sys.argv
        
        soo_file_path = None
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                continue
            potential_path = Path(arg)
            if potential_path.suffix.lower() == '.soo':
                if not potential_path.exists():
                    potential_path = potential_path.resolve()
                if potential_path.exists():
                    soo_file_path = str(potential_path.absolute())
                    break
        
        logger.info("Starting SLPlayer application")
        app = QApplication(sys.argv)
        app.setApplicationName("SLPlayer")
        app.setOrganizationName("SLPlayer")
        
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent
        else:
            base_path = Path(__file__).parent
        IconManager.setup_application_icon(app, base_path)
        
        window_width = settings.get("window.width", 1400)
        window_height = settings.get("window.height", 900)
        window_x = settings.get("window.x", 100)
        window_y = settings.get("window.y", 100)
        
        first_launch_complete = settings.get("first_launch_complete", False)
        if not first_launch_complete:
            from ui.network_setup_dialog import NetworkSetupDialog
            network_dialog = NetworkSetupDialog()
            network_dialog.exec()
            settings.set("first_launch_complete", True)
            logger.info("First launch network setup completed")
        
        from ui.device_selection_dialog import DeviceSelectionDialog
        device_dialog = DeviceSelectionDialog()
        device_dialog.show()
        
        window = MainWindow()
        window.resize(window_width, window_height)
        window.move(window_x, window_y)
        window.hide()
        
        device_dialog.set_main_window(window)
        
        def on_device_selected(ip, port, controller_type, device_id):
            try:
                success = window.controller_service.connect_to_controller(
                    ip,
                    port,
                    controller_type
                )
                if success:
                    logger.info(f"Connected to device {device_id} at {ip}:{port}")
                    
                    from core.controller_database import get_controller_database
                    db = get_controller_database()
                    device_info = db.get_controller(device_id)
                    
                    if device_info:
                        width = device_info.get('width')
                        height = device_info.get('height')
                        
                        if not width or not height:
                            display_resolution = device_info.get('display_resolution', '')
                            if display_resolution and 'x' in display_resolution.lower():
                                try:
                                    parts = display_resolution.lower().replace(' ', '').split('x')
                                    if len(parts) == 2:
                                        width = int(parts[0])
                                        height = int(parts[1])
                                except (ValueError, IndexError):
                                    pass
                        
                        if width and height:
                            from core.screen_config import set_screen_config
                            brand = device_info.get('model', '') or controller_type
                            model = device_info.get('model', '') or ''
                            set_screen_config(brand, model, width, height, 0, None)
                            logger.info(f"Set screen resolution from device: {width}x{height}")
                        else:
                            logger.warning(f"Could not extract resolution from device info")
                else:
                    logger.warning(f"Failed to connect to device {device_id} at {ip}:{port}")
            except Exception as e:
                logger.error(f"Error connecting to device: {e}")
            
            window.show()
            window.raise_()
            window.activateWindow()
        
        device_dialog.device_selected.connect(on_device_selected)
        
        window._device_dialog = device_dialog
        
        if soo_file_path:
            logger.info(f"Loading specific .soo file from command-line: {soo_file_path}")
            window.load_soo_file(soo_file_path, clear_existing=True, async_load=True)
        else:
            logger.info("No specific .soo file provided, loading all autosaved files")
            window._load_autosaved_files()
        
        IconManager.setup_taskbar_icon(window, base_path)
        
        sys.exit(app.exec())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error starting application: {e}", exc_info=True)
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"Application failed to start:\n{str(e)}\n\nCheck logs for details."
            )
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

