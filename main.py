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
    """Cleanup function to stop the API server on exit"""
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
        
        try:
            from core.controller_research_service import ControllerResearchService
            ControllerResearchService.populate_database(force_update=False)
            logger.info("Controller database populated with research data")
        except Exception as e:
            logger.warning(f"Could not populate controller database at startup: {e}")
        
        # Show device selection dialog first
        from ui.device_selection_dialog import DeviceSelectionDialog
        device_dialog = DeviceSelectionDialog()
        
        selected_ip = None
        selected_port = None
        selected_type = None
        selected_device_id = None
        
        if device_dialog.exec() == device_dialog.Accepted:
            selected_ip = device_dialog.selected_ip
            selected_port = device_dialog.selected_port
            selected_type = device_dialog.selected_type
            selected_device_id = device_dialog.selected_controller_id
        
        window = MainWindow()
        window.resize(window_width, window_height)
        window.move(window_x, window_y)
        
        # Connect to selected device
        if selected_ip and selected_port and selected_type:
            try:
                success = window.controller_service.connect_to_controller(
                    selected_ip,
                    selected_port,
                    selected_type
                )
                if success:
                    logger.info(f"Connected to device {selected_device_id} at {selected_ip}:{selected_port}")
                else:
                    logger.warning(f"Failed to connect to device {selected_device_id} at {selected_ip}:{selected_port}")
            except Exception as e:
                logger.error(f"Error connecting to device: {e}")
        
        window.show()
        
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
            # Last resort error handling - can't show message box if QApplication failed
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

