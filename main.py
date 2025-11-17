"""
SLPlayer - LED Display Controller Program Manager
Main application entry point
"""
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from config.settings import settings
from core.startup_service import StartupService
from utils.logger import get_logger
from utils.icon_manager import IconManager

logger = get_logger(__name__)


def main():
    """Main application entry point"""
    try:
        # Check for command-line arguments
        if "--reset-first-launch" in sys.argv or "--reset-first" in sys.argv:
            settings.set("first_launch_complete", False)
            print("✓ First launch flag has been reset!")
            print("The Network Setup Dialog will appear on next application start.")
            return
        
        # Check for skip license flag
        skip_license = "--skip-license" in sys.argv or "--skip-lic" in sys.argv
        
        # Check for .soo file path in command-line arguments
        soo_file_path = None
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                continue
            potential_path = Path(arg)
            if potential_path.suffix.lower() == '.soo':
                if potential_path.exists():
                    soo_file_path = str(potential_path.absolute())
                    break
                else:
                    potential_path = Path(arg).resolve()
                    if potential_path.exists():
                        soo_file_path = str(potential_path)
                        break
        
        logger.info("Starting SLPlayer application")
        app = QApplication(sys.argv)
        app.setApplicationName("SLPlayer")
        app.setOrganizationName("SLPlayer")
        
        # Set application icon
        base_path = Path(__file__).parent
        IconManager.setup_application_icon(app, base_path)
        
        # Load settings
        window_width = settings.get("window.width", 1400)
        window_height = settings.get("window.height", 900)
        window_x = settings.get("window.x", 100)
        window_y = settings.get("window.y", 100)
        
        # Check for first launch - show network setup dialog
        first_launch_complete = settings.get("first_launch_complete", False)
        if not first_launch_complete:
            from ui.network_setup_dialog import NetworkSetupDialog
            network_dialog = NetworkSetupDialog()
            network_dialog.exec()
            settings.set("first_launch_complete", True)
            logger.info("First launch network setup completed")
        
        # License verification at startup
        startup_service = StartupService()
        controller_id, valid_license_found = startup_service.verify_license_at_startup()
        license_must_be_activated = not valid_license_found
        
        # Show license activation dialog if needed
        if not skip_license:
            from ui.login_dialog import LoginDialog
            login_dialog = LoginDialog(controller_id=controller_id)
            
            if license_must_be_activated and not controller_id:
                logger.info("No valid license found - showing license activation dialog for online activation")
            
            dialog_result = login_dialog.exec()
            
            if not dialog_result:
                logger.info("User cancelled license activation - application exit required")
                sys.exit(0)
            
            if not login_dialog.is_license_valid():
                controller_id = login_dialog.controller_id or controller_id
                if not startup_service.check_license_after_activation(controller_id):
                    sys.exit(1)
            
            controller_id = login_dialog.controller_id or controller_id
            
            if controller_id and license_must_be_activated:
                if not startup_service.check_license_after_activation(controller_id):
                    sys.exit(1)
        else:
            logger.info("License dialog skipped via command-line argument")
        
        # Final license verification
        if controller_id and not skip_license:
            if not startup_service.check_license_after_activation(controller_id):
                sys.exit(1)
        
        # Create and show main window
        window = MainWindow()
        window.resize(window_width, window_height)
        window.move(window_x, window_y)
        window.show()
        
        if soo_file_path:
            logger.info(f"Loading specific .soo file from command-line: {soo_file_path}")
            window._latest_file_loaded = window.load_soo_file(soo_file_path, clear_existing=True)
            if window._latest_file_loaded:
                logger.info("Specific .soo file loaded successfully")
            else:
                logger.warning("Failed to load specific .soo file, will try to load all autosaved files")
                window._latest_file_loaded = window.file_manager.load_latest_soo_files()
        else:
            logger.info("No specific .soo file provided, loading all autosaved files")
            window._latest_file_loaded = window.file_manager.load_latest_soo_files()
        
        logger.info(f"File loaded status: {window._latest_file_loaded}")
        if not window._latest_file_loaded:
            logger.info("No files loaded, opening screen settings dialog")
            window.open_screen_settings_on_startup()
        else:
            logger.info("Files loaded successfully, skipping screen settings dialog")
        
        # Set taskbar icon using Windows API
        IconManager.setup_taskbar_icon(window, base_path)
        
        sys.exit(app.exec())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error starting application: {e}", exc_info=True)
        # Show error dialog if possible
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"Application failed to start:\n{str(e)}\n\nCheck logs for details."
            )
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

