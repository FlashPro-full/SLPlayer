"""
SLPlayer - LED Display Controller Program Manager
Main application entry point
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Windows-specific icon handling
if sys.platform == "win32":
    try:
        from utils.windows_icon import set_taskbar_icon
    except ImportError:
        set_taskbar_icon = None
else:
    set_taskbar_icon = None


def main():
    """Main application entry point"""
    try:
        logger.info("Starting SLPlayer application")
        app = QApplication(sys.argv)
        app.setApplicationName("SLPlayer")
        app.setOrganizationName("SLPlayer")
        
        # Set application icon (for taskbar and window)
        icon_path = Path(__file__).parent / "resources" / "app.ico"
        if icon_path.exists():
            icon = QIcon(str(icon_path.absolute()))
            app.setWindowIcon(icon)
        else:
            # Try alternative names
            for alt_name in ["icon.ico", "app_icon.ico", "SLPlayer.ico", "icon.png"]:
                alt_path = Path(__file__).parent / "resources" / alt_name
                if alt_path.exists():
                    icon = QIcon(str(alt_path.absolute()))
                    app.setWindowIcon(icon)
                    break
        
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
            # Mark first launch as complete
            settings.set("first_launch_complete", True)
            logger.info("First launch network setup completed")
        
        # Check for license at startup (offline verification)
        controller_id = None
        try:
            # Try to get controller ID from connected controller (if any)
            # For now, we'll check if there's a saved controller ID or detect on first connection
            # This will be enhanced when controller is connected
            pass
        except Exception as e:
            logger.warning(f"Error checking controller ID: {e}")
        
        # Show login dialog
        from ui.login_dialog import LoginDialog
        login_dialog = LoginDialog(controller_id=controller_id)
        if not login_dialog.exec():
            sys.exit(0)  # User cancelled login
        
        # Verify license if controller_id is available
        if controller_id:
            try:
                from core.license_manager import LicenseManager
                license_manager = LicenseManager()
                if not license_manager.has_valid_license(controller_id):
                    QMessageBox.warning(
                        None, "License Required",
                        "Valid license not found. Please activate a license to continue."
                    )
                    sys.exit(0)
            except Exception as e:
                logger.warning(f"License verification error: {e}")
                # Continue anyway (graceful degradation)
        
        # Create and show main window
        window = MainWindow()
        window.resize(window_width, window_height)
        window.move(window_x, window_y)
        window.show()
        
        # Set taskbar icon using Windows API (for better compatibility)
        # This must be done after window.show() and with a small delay
        if sys.platform == "win32" and set_taskbar_icon:
            icon_path = Path(__file__).parent / "resources" / "app.ico"
            if icon_path.exists():
                # Use QTimer to set icon after window is fully shown
                from PyQt6.QtCore import QTimer
                def set_icon():
                    try:
                        window_handle = int(window.winId())
                        set_taskbar_icon(window_handle, icon_path)
                    except Exception as e:
                        logger.warning(f"Could not set taskbar icon: {e}")
                
                # Set icon after a short delay to ensure window is fully initialized
                QTimer.singleShot(100, set_icon)
        
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

