import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from utils.logger import get_logger
from utils.app_data import get_app_data_dir

logger = get_logger(__name__)

class ControllerDatabase:

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            import sys
            if getattr(sys, 'frozen', False):
                db_path = get_app_data_dir() / "controllers.db"
            else:
                try:
                    app_root = Path(__file__).resolve().parents[1]
                    preferred = app_root / "controllers.db"
                    app_root.mkdir(parents=True, exist_ok=True)
                    preferred.touch(exist_ok=True)
                    db_path = preferred
                except Exception:
                    db_path = get_app_data_dir() / "controllers.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS controllers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    controller_id TEXT UNIQUE NOT NULL,
                    ip_address TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    controller_type TEXT NOT NULL,
                    device_name TEXT,
                    mac_address TEXT,
                    firmware_version TEXT,
                    display_resolution TEXT,
                    model TEXT,
                    serial_number TEXT,
                    first_connected TEXT NOT NULL,
                    last_connected TEXT NOT NULL,
                    connection_count INTEGER DEFAULT 1,
                    total_connection_time INTEGER DEFAULT 0,
                    last_disconnected TEXT,
                    is_active INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'disconnected',
                    has_license INTEGER DEFAULT 0,
                    license_file_name TEXT,
                    notes TEXT
                )
            """)
            
            try:
                cursor.execute("ALTER TABLE controllers ADD COLUMN status TEXT DEFAULT 'disconnected'")
                logger.info("Added status column to controllers table")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE controllers ADD COLUMN has_license INTEGER DEFAULT 0")
                logger.info("Added has_license column to controllers table")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE controllers ADD COLUMN license_file_name TEXT")
                logger.info("Added license_file_name column to controllers table")
            except sqlite3.OperationalError:
                pass
            
            cursor.execute("""
                UPDATE controllers 
                SET status = CASE
                    WHEN is_active = 1 AND ip_address != '0.0.0.0' THEN 'connected'
                    WHEN is_active = 0 AND ip_address != '0.0.0.0' THEN 'disconnected'
                    WHEN ip_address = '0.0.0.0' THEN 'license_only'
                    ELSE 'disconnected'
                END
                WHERE status IS NULL OR status = ''
            """)


            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screen_parameters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    brand TEXT,
                    model TEXT,
                    width INTEGER,
                    height INTEGER,
                    rotate INTEGER,
                    controller_id TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS controller_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    controller_id TEXT NOT NULL,
                    screen_name TEXT,
                    time_sync_method TEXT,
                    time_last_synced TEXT,
                    brightness INTEGER,
                    brightness_settings TEXT,
                    power_schedule TEXT,
                    last_updated TEXT NOT NULL,
                    UNIQUE(controller_id, screen_name)
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_controller_id ON controllers(controller_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_settings_controller_id ON controller_settings(controller_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_settings_screen ON controller_settings(controller_id, screen_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ip_address ON controllers(ip_address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_connected ON controllers(last_connected)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_active ON controllers(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON controllers(status)")
            
            conn.commit()
            conn.close()
            logger.info("Controller database initialized")
        except Exception as e:
            logger.exception(f"Error initializing controller database: {e}")
    
    def add_or_update_controller(self, controller_id: str, ip_address: str, port: int,
                                 controller_type: str, device_info: Optional[Dict] = None) -> bool:
        try:
            from core.license_manager import LicenseManager
            license_manager = LicenseManager()
            license_file = license_manager.get_license_file_path(controller_id)
            has_license = 1 if license_file.exists() else 0
            license_file_name = license_file.name if license_file.exists() else None
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            device_name = device_info.get("name") if device_info else None
            mac_address = device_info.get("mac_address") if device_info else None
            firmware_version = device_info.get("firmware_version") or device_info.get("version") if device_info else None
            display_resolution = device_info.get("display_resolution") or device_info.get("resolution") if device_info else None
            model = device_info.get("model") or device_info.get("model_number") if device_info else None
            serial_number = device_info.get("serial_number") or device_info.get("serial") if device_info else None
            
            now = datetime.now().isoformat()
            
            cursor.execute("SELECT id, connection_count FROM controllers WHERE controller_id = ?", 
                          (controller_id,))
            existing = cursor.fetchone()
            
            if existing:
                controller_db_id, connection_count = existing
                new_count = connection_count + 1
                
                cursor.execute("""
                    UPDATE controllers 
                    SET ip_address = ?,
                        port = ?,
                        controller_type = ?,
                        device_name = ?,
                        mac_address = COALESCE(?, mac_address),
                        firmware_version = COALESCE(?, firmware_version),
                        display_resolution = COALESCE(?, display_resolution),
                        model = COALESCE(?, model),
                        serial_number = COALESCE(?, serial_number),
                        last_connected = ?,
                        connection_count = ?,
                        is_active = 1,
                        has_license = ?,
                        license_file_name = ?
                    WHERE controller_id = ?
                """, (
                    ip_address, port, controller_type, device_name,
                    mac_address, firmware_version, display_resolution,
                    model, serial_number, now, new_count, has_license,
                    license_file_name, controller_id
                ))
                
                logger.info(f"Updated controller {controller_id} in database (connection #{new_count})")
            else:
                cursor.execute("""
                    INSERT INTO controllers (
                        controller_id, ip_address, port, controller_type,
                        device_name, mac_address, firmware_version,
                        display_resolution, model, serial_number,
                        first_connected, last_connected, connection_count, is_active,
                        has_license, license_file_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
                """, (
                    controller_id, ip_address, port, controller_type,
                    device_name, mac_address, firmware_version,
                    display_resolution, model, serial_number,
                    now, now, has_license, license_file_name
                ))
                
                logger.info(f"Added new controller {controller_id} to database")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.exception(f"Error adding/updating controller in database: {e}")
            return False
    
    def mark_controller_disconnected(self, controller_id: str) -> bool:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE controllers 
                SET is_active = 0,
                    last_disconnected = ?
                WHERE controller_id = ?
            """, (now, controller_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Marked controller {controller_id} as disconnected")
            return True
        except Exception as e:
            logger.exception(f"Error marking controller as disconnected: {e}")
            return False
    
    def update_license_info(self, controller_id: str) -> bool:
        try:
            from core.license_manager import LicenseManager
            license_manager = LicenseManager()
            license_file = license_manager.get_license_file_path(controller_id)
            has_license = 1 if license_file.exists() else 0
            license_file_name = license_file.name if license_file.exists() else None
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE controllers 
                SET has_license = ?,
                    license_file_name = ?
                WHERE controller_id = ?
            """, (has_license, license_file_name, controller_id))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logger.exception(f"Error updating license info for controller {controller_id}: {e}")
            return False
    
    def add_controller_from_license(self, controller_id: str, license_data: Optional[Dict] = None) -> bool:
        try:
            existing = self.get_controller(controller_id)
            if existing:
                if existing.get('status') != 'license_only':
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE controllers 
                        SET status = 'license_only',
                            ip_address = '0.0.0.0',
                            port = 0
                        WHERE controller_id = ?
                    """, (controller_id,))
                    conn.commit()
                    conn.close()
                logger.debug(f"Controller {controller_id} already exists in database")
                return True
            
            controller_type = "Unknown"
            model = None
            device_name = None
            
            if license_data:
                controller_type_str = license_data.get('controllerType', '') or ''
                model = license_data.get('model', '') or ''
                device_name = license_data.get('deviceName', '') or model
            else:
                ctrl_id_upper = controller_id.upper()
                if 'HD-' in ctrl_id_upper or 'HUIDU' in ctrl_id_upper:
                    controller_type = 'Huidu'
                elif 'NOVASTAR' in ctrl_id_upper or 'T' in ctrl_id_upper or 'MCTRL' in ctrl_id_upper:
                    controller_type = 'NovaStar'
            
            if not device_name:
                device_name = model or controller_id
            
            now = datetime.now().isoformat()
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            from core.license_manager import LicenseManager
            license_manager = LicenseManager()
            license_file = license_manager.get_license_file_path(controller_id)
            has_license = 1 if license_file.exists() else 0
            license_file_name = license_file.name if license_file.exists() else None
            
            cursor.execute("""
                INSERT INTO controllers (
                    controller_id, ip_address, port, controller_type,
                    device_name, model,
                    first_connected, last_connected, connection_count, 
                    is_active, has_license, license_file_name
                ) VALUES (?, '0.0.0.0', 0, ?, ?, ?, ?, 0, 0, ?, ?)
            """, (
                controller_id, controller_type, device_name, model,
                now, now, has_license, license_file_name
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added controller from license: {controller_id} ({controller_type} {model})")
            return True
        except Exception as e:
            logger.exception(f"Error adding controller from license {controller_id}: {e}")
            return False
    
    def get_controller(self, controller_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM controllers WHERE controller_id = ?", (controller_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.exception(f"Error getting controller from database: {e}")
            return None
    
    def get_all_controllers(self, active_only: bool = False) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute("SELECT * FROM controllers WHERE is_active = 1 ORDER BY last_connected DESC")
            else:
                cursor.execute("SELECT * FROM controllers ORDER BY last_connected DESC")
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting all controllers from database: {e}")
            return []
    
    def get_controllers_by_type(self, controller_type: str) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM controllers WHERE controller_type = ? ORDER BY last_connected DESC", 
                          (controller_type,))
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting controllers by type from database: {e}")
            return []
    
    def search_controllers(self, query: str) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM controllers 
                WHERE controller_id LIKE ? 
                   OR device_name LIKE ? 
                   OR ip_address LIKE ?
                   OR model LIKE ?
                ORDER BY last_connected DESC
            """, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error searching controllers in database: {e}")
            return []
    
    def delete_controller(self, controller_id: str) -> bool:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM controllers WHERE controller_id = ?", (controller_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted controller {controller_id} from database")
            return True
        except Exception as e:
            logger.exception(f"Error deleting controller from database: {e}")
            return False
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM controllers")
            total_controllers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM controllers WHERE is_active = 1")
            active_controllers = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(connection_count) FROM controllers")
            total_connections = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT controller_type, COUNT(*) 
                FROM controllers 
                GROUP BY controller_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                "total_controllers": total_controllers,
                "active_controllers": active_controllers,
                "total_connections": total_connections,
                "by_type": by_type
            }
        except Exception as e:
            logger.exception(f"Error getting connection statistics: {e}")
            return {
                "total_controllers": 0,
                "active_controllers": 0,
                "total_connections": 0,
                "by_type": {}
            }


    def save_screen_parameters(self, params: Dict[str, Any]) -> bool:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            width_val = params.get("width")
            height_val = params.get("height")
            rotate_val = params.get("rotate")
            
            width = int(width_val) if width_val is not None and isinstance(width_val, (int, str)) else None
            height = int(height_val) if height_val is not None and isinstance(height_val, (int, str)) else None
            rotate = int(rotate_val) if rotate_val is not None and isinstance(rotate_val, (int, str)) else None
            
            cursor.execute("""
                INSERT INTO screen_parameters (created_at, brand, model, width, height, rotate, controller_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                now,
                params.get("brand"),
                params.get("model"),
                width,
                height,
                rotate,
                params.get("controller_id"),
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.exception(f"Error saving screen parameters: {e}")
            return False
    
    def save_controller_settings(self, controller_id: str, settings: Dict, screen_name: Optional[str] = None) -> bool:
        try:
            import json
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            brightness = settings.get("brightness")
            brightness_settings = settings.get("brightness_settings")
            power_schedule = settings.get("power_schedule")
            time_sync_method = settings.get("time_sync", {}).get("method")
            time_last_synced = settings.get("time_last_synced")
            
            cursor.execute("""
                INSERT INTO controller_settings 
                (controller_id, screen_name, time_sync_method, time_last_synced, 
                 brightness, brightness_settings, power_schedule, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(controller_id, screen_name) DO UPDATE SET
                    time_sync_method = excluded.time_sync_method,
                    time_last_synced = excluded.time_last_synced,
                    brightness = excluded.brightness,
                    brightness_settings = excluded.brightness_settings,
                    power_schedule = excluded.power_schedule,
                    last_updated = excluded.last_updated
            """, (
                controller_id,
                screen_name,
                time_sync_method,
                time_last_synced,
                brightness,
                json.dumps(brightness_settings) if brightness_settings else None,
                json.dumps(power_schedule) if power_schedule else None,
                now
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved settings for controller {controller_id}" + (f" screen {screen_name}" if screen_name else ""))
            return True
        except Exception as e:
            logger.exception(f"Error saving controller settings: {e}")
            return False
    
    def get_controller_settings(self, controller_id: str, screen_name: Optional[str] = None) -> Optional[Dict]:
        try:
            import json
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if screen_name:
                cursor.execute("""
                    SELECT * FROM controller_settings 
                    WHERE controller_id = ? AND screen_name = ?
                    ORDER BY last_updated DESC LIMIT 1
                """, (controller_id, screen_name))
            else:
                cursor.execute("""
                    SELECT * FROM controller_settings 
                    WHERE controller_id = ? AND screen_name IS NULL
                    ORDER BY last_updated DESC LIMIT 1
                """, (controller_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                result = dict(row)
                if result.get("brightness_settings"):
                    try:
                        result["brightness_settings"] = json.loads(result["brightness_settings"])
                    except:
                        result["brightness_settings"] = {}
                if result.get("power_schedule"):
                    try:
                        result["power_schedule"] = json.loads(result["power_schedule"])
                    except:
                        result["power_schedule"] = []
                
                return {
                    "brightness": result.get("brightness"),
                    "brightness_settings": result.get("brightness_settings", {}),
                    "power_schedule": result.get("power_schedule", []),
                    "time_sync": {
                        "method": result.get("time_sync_method", "pc")
                    },
                    "time_last_synced": result.get("time_last_synced")
                }
            return None
        except Exception as e:
            logger.exception(f"Error getting controller settings: {e}")
            return None


_controller_db_instance: Optional[ControllerDatabase] = None

def get_controller_database() -> ControllerDatabase:
    global _controller_db_instance
    if _controller_db_instance is None:
        _controller_db_instance = ControllerDatabase()
    return _controller_db_instance

