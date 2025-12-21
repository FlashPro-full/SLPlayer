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
        logger.info(f"Initializing database: {self.db_path}")
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            for table_name in ["huidu_controllers", "novastar_controllers"]:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        controller_type TEXT NOT NULL,
                        controller_id TEXT UNIQUE NOT NULL,
                        name TEXT,
                        screen_width TEXT,
                        screen_height TEXT,
                        screen_rotation TEXT,
                        version_hardware TEXT,
                        version_fpga TEXT,
                        version_kernel TEXT,
                        version_app TEXT,
                        time TEXT,
                        time_timeZone TEXT,
                        time_sync TEXT,
                        volume TEXT,
                        volume_mode TEXT,
                        luminance TEXT,
                        luminance_mode TEXT,
                        eth_dhcp TEXT,
                        eth_ip TEXT,
                        wifi_enabled TEXT,
                        wifi_mode TEXT,
                        wifi_ap_ssid TEXT,
                        wifi_ap_passwd TEXT,
                        wifi_ap_channel TEXT,
                        sync TEXT,
                        gsm_apn TEXT,
                        has_license INTEGER DEFAULT 0,
                        license_file_name TEXT
                    )
                """)
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return { "message": "error", "data": str(e) }

    def find_huidu_controller_by_id(self, controller_id: str) -> Optional[Dict]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM huidu_controllers WHERE controller_id = ?", (controller_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Error finding huidu controller by id: {e}")
            return { "message": "error", "data": str(e) }

    def find_novastar_controller_by_id(self, controller_id: str) -> Optional[Dict]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM novastar_controllers WHERE controller_id = ?", (controller_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Error finding novastar controller by id: {e}")
            return { "message": "error", "data": str(e) }
    
    def get_all_huidu_controllers(self) -> List[Dict]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM huidu_controllers")
            rows = cursor.fetchall()
            if rows:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
        except Exception as e:
            logger.error(f"Error getting controller by id: {e}")
            return []

    def get_all_novastar_controllers(self) -> List[Dict]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM novastar_controllers")
            rows = cursor.fetchall()
            if rows:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
        except Exception as e:
            logger.error(f"Error getting all novastar controllers: {e}")
            return []

    def add_huidu_controller(self, controller_properties: Dict) -> Dict:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("INSERT INTO huidu_controllers\
                (controller_type, controller_id, name, screen_width, screen_height, screen_rotation,\
                    version_hardware, version_fpga, version_kernel, version_app,\
                    time, time_timeZone, time_sync, volume, volume_mode, luminance, luminance_mode,\
                    eth_dhcp, eth_ip, wifi_enabled, wifi_mode, wifi_ap_ssid, wifi_ap_passwd, wifi_ap_channel,\
                    sync, gsm_apn)\
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",\
                ("huidu", controller_properties.get("controller_id"), controller_properties.get("name"),
                controller_properties.get("screen.width"), controller_properties.get("screen.height"),
                controller_properties.get("screen.rotation"), controller_properties.get("version.hardware"),
                controller_properties.get("version.fpga"), controller_properties.get("version.kernel"),
                controller_properties.get("version.app"), controller_properties.get("time"),
                controller_properties.get("time.timeZone"), controller_properties.get("time.sync"),
                controller_properties.get("volume"), controller_properties.get("volume.mode"),
                controller_properties.get("luminance"), controller_properties.get("luminance.mode"),
                controller_properties.get("eth.dhcp"), controller_properties.get("eth.ip"),
                controller_properties.get("wifi.enabled"), controller_properties.get("wifi.mode"),
                controller_properties.get("wifi.ap.ssid"), controller_properties.get("wifi.ap.passwd"),
                controller_properties.get("wifi.ap.channel"), controller_properties.get("sync"),
                controller_properties.get("gsm.apn")))
            
            conn.commit()
            return {"message": "ok"}
        except Exception as e:
            logger.error(f"Error adding huidu controller: {e}")
            return {"message": "error", "data": str(e)}

    def update_huidu_controller_by_id(self, controller_id: str, controller_properties: Dict) -> Dict:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""UPDATE huidu_controllers SET
                name = ?, screen_width = ?, screen_height = ?, screen_rotation = ?,
                version_hardware = ?, version_fpga = ?, version_kernel = ?, version_app = ?,
                time = ?, time_timeZone = ?, time_sync = ?, volume = ?, volume_mode = ?,
                luminance = ?, luminance_mode = ?, eth_dhcp = ?, eth_ip = ?,
                wifi_enabled = ?, wifi_mode = ?, wifi_ap_ssid = ?, wifi_ap_passwd = ?,
                wifi_ap_channel = ?, sync = ?, gsm_apn = ?
                WHERE controller_id = ?""",
                (controller_properties.get("name"),
                controller_properties.get("screen.width"), controller_properties.get("screen.height"),
                controller_properties.get("screen.rotation"), controller_properties.get("version.hardware"),
                controller_properties.get("version.fpga"), controller_properties.get("version.kernel"),
                controller_properties.get("version.app"), controller_properties.get("time"),
                controller_properties.get("time.timeZone"), controller_properties.get("time.sync"),
                controller_properties.get("volume"), controller_properties.get("volume.mode"),
                controller_properties.get("luminance"), controller_properties.get("luminance.mode"),
                controller_properties.get("eth.dhcp"), controller_properties.get("eth.ip"),
                controller_properties.get("wifi.enabled"), controller_properties.get("wifi.mode"),
                controller_properties.get("wifi.ap.ssid"), controller_properties.get("wifi.ap.passwd"),
                controller_properties.get("wifi.ap.channel"), controller_properties.get("sync"),
                controller_properties.get("gsm.apn"), controller_id))
            
            conn.commit()
            return {"message": "ok"}
        except Exception as e:
            logger.error(f"Error updating huidu controller by id: {e}")
            return {"message": "error", "data": str(e)}

    def add_novastar_controller(self, controller_properties: Dict) -> Dict:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("INSERT INTO novastar_controllers\
                (controller_type, controller_id, name, screen_width, screen_height, screen_rotation,\
                    version_hardware, version_fpga, version_kernel, version_app,\
                    time, time_timeZone, time_sync, volume, volume_mode, luminance, luminance_mode,\
                    eth_dhcp, eth_ip, wifi_enabled, wifi_mode, wifi_ap_ssid, wifi_ap_passwd, wifi_ap_channel,\
                    sync, gsm_apn)\
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",\
                ("novastar", controller_properties.get("controller_id"), controller_properties.get("name"),
                controller_properties.get("screen.width"), controller_properties.get("screen.height"),
                controller_properties.get("screen.rotation"), controller_properties.get("version.hardware"),
                controller_properties.get("version.fpga"), controller_properties.get("version.kernel"),
                controller_properties.get("version.app"), controller_properties.get("time"),
                controller_properties.get("time.timeZone"), controller_properties.get("time.sync"),
                controller_properties.get("volume"), controller_properties.get("volume.mode"),
                controller_properties.get("luminance"), controller_properties.get("luminance.mode"),
                controller_properties.get("eth.dhcp"), controller_properties.get("eth.ip"),
                controller_properties.get("wifi.enabled"), controller_properties.get("wifi.mode"),
                controller_properties.get("wifi.ap.ssid"), controller_properties.get("wifi.ap.passwd"),
                controller_properties.get("wifi.ap.channel"), controller_properties.get("sync"),
                controller_properties.get("gsm.apn")))
            
            conn.commit()
            return {"message": "ok"}
        except Exception as e:
            logger.error(f"Error adding novastar controller: {e}")
            return {"message": "error", "data": str(e)}

    def update_novastar_controller_by_id(self, controller_id: str, controller_properties: Dict) -> Dict:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""UPDATE novastar_controllers SET
                name = ?, screen_width = ?, screen_height = ?, screen_rotation = ?,
                version_hardware = ?, version_fpga = ?, version_kernel = ?, version_app = ?,
                time = ?, time_timeZone = ?, time_sync = ?, volume = ?, volume_mode = ?,
                luminance = ?, luminance_mode = ?, eth_dhcp = ?, eth_ip = ?,
                wifi_enabled = ?, wifi_mode = ?, wifi_ap_ssid = ?, wifi_ap_passwd = ?,
                wifi_ap_channel = ?, sync = ?, gsm_apn = ?
                WHERE controller_id = ?""",
                (controller_properties.get("name"),
                controller_properties.get("screen.width"), controller_properties.get("screen.height"),
                controller_properties.get("screen.rotation"), controller_properties.get("version.hardware"),
                controller_properties.get("version.fpga"), controller_properties.get("version.kernel"),
                controller_properties.get("version.app"), controller_properties.get("time"),
                controller_properties.get("time.timeZone"), controller_properties.get("time.sync"),
                controller_properties.get("volume"), controller_properties.get("volume.mode"),
                controller_properties.get("luminance"), controller_properties.get("luminance.mode"),
                controller_properties.get("eth.dhcp"), controller_properties.get("eth.ip"),
                controller_properties.get("wifi.enabled"), controller_properties.get("wifi.mode"),
                controller_properties.get("wifi.ap.ssid"), controller_properties.get("wifi.ap.passwd"),
                controller_properties.get("wifi.ap.channel"), controller_properties.get("sync"),
                controller_properties.get("gsm.apn"), controller_id))
                        
            conn.commit()
            return {"message": "ok"}
        except Exception as e:
            logger.error(f"Error updating novastar controller by id: {e}")
            return {"message": "error", "data": str(e)}

    def update_license_info(self, controller_id: str, license_file_name: Optional[str] = None) -> Dict:
        try:
            if license_file_name is None:
                license_file_name = f"{controller_id}.slp"
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE huidu_controllers 
                SET has_license = ?, license_file_name = ?
                WHERE controller_id = ?
            """, (1, license_file_name, controller_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                return {"message": "ok"}
            
            cursor.execute("""
                UPDATE novastar_controllers 
                SET has_license = ?, license_file_name = ?
                WHERE controller_id = ?
            """, (1, license_file_name, controller_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                return {"message": "ok"}
            
            logger.warning(f"Controller {controller_id} not found in database")
            return {"message": "error", "data": "Controller not found"}
            
        except Exception as e:
            logger.error(f"Error updating license info: {e}")
            return {"message": "error", "data": str(e)}


_controller_database_instance = None

def get_controller_database() -> ControllerDatabase:
    global _controller_database_instance
    if _controller_database_instance is None:
        _controller_database_instance = ControllerDatabase()
    return _controller_database_instance