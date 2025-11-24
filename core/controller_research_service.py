"""
Controller Research Service
Comprehensive database of NovaStar and Huidu controller series
"""
from typing import List, Dict, Any
from core.controller_database import get_controller_database
from utils.logger import get_logger

logger = get_logger(__name__)


class ControllerResearchService:

    NOVASTAR_MODELS = [
        {
            "brand": "NovaStar",
            "model": "T3",
            "range": "320 × 256",
            "max_w": 1024,
            "max_h": 512,
            "storage": "4 GB",
            "gray": "65536",
            "iface": "Ethernet / Wi‑Fi / U‑disk",
            "other": "Taurus series - Entry level controller"
        },
        {
            "brand": "NovaStar",
            "model": "T6",
            "range": "512 × 384",
            "max_w": 2048,
            "max_h": 1024,
            "storage": "8 GB",
            "gray": "65536",
            "iface": "Ethernet / Wi‑Fi / 4G / U‑disk",
            "other": "Taurus series - Mid-range controller"
        },
        {
            "brand": "NovaStar",
            "model": "T8",
            "range": "640 × 512",
            "max_w": 4096,
            "max_h": 2048,
            "storage": "16 GB",
            "gray": "65536",
            "iface": "Ethernet / Wi‑Fi / 4G / U‑disk",
            "other": "Taurus series - High-end controller"
        },
        {
            "brand": "NovaStar",
            "model": "TB3",
            "range": "384 × 320",
            "max_w": 2048,
            "max_h": 1024,
            "storage": "8 GB",
            "gray": "65536",
            "iface": "Ethernet / Wi‑Fi / U‑disk",
            "other": "Taurus TB series - Enhanced version"
        },
        {
            "brand": "NovaStar",
            "model": "MCTRL300",
            "range": "2048 × 668",
            "max_w": 2048,
            "max_h": 1200,
            "storage": "Internal",
            "gray": "65536",
            "iface": "DVI / Audio / Ethernet",
            "other": "Entry-level video controller - 1.3M pixels @60Hz, 2× Gigabit Ethernet"
        },
        {
            "brand": "NovaStar",
            "model": "MCTRL600",
            "range": "1920 × 1200",
            "max_w": 1920,
            "max_h": 1200,
            "storage": "Internal",
            "gray": "65536",
            "iface": "DVI / HDMI 1.3 / Ethernet",
            "other": "Mid-range video controller - 4× Gigabit Ethernet, pixel-level calibration"
        },
        {
            "brand": "NovaStar",
            "model": "MCTRL660 PRO",
            "range": "1920 × 1200",
            "max_w": 1920,
            "max_h": 1200,
            "storage": "Internal",
            "gray": "10-bit/12-bit",
            "iface": "3G-SDI / HDMI 1.4a / DVI / Ethernet / 10G Optical",
            "other": "Professional video controller - 6× Gigabit Ethernet, 2× 10G optical, <1ms latency"
        },
        {
            "brand": "NovaStar",
            "model": "MCTRL4K",
            "range": "4096 × 2160",
            "max_w": 4096,
            "max_h": 2160,
            "storage": "Internal",
            "gray": "HDR10 / HLG",
            "iface": "DP 1.2 / DVI / Dual-link DVI / Ethernet / 10G Optical",
            "other": "4K video controller - 16× Gigabit Ethernet, 4× 10G optical, supports 3D"
        },
        {
            "brand": "NovaStar",
            "model": "MCTRL R5",
            "range": "3840 × 1080",
            "max_w": 3840,
            "max_h": 1080,
            "storage": "Internal",
            "gray": "65536",
            "iface": "6G-SDI / Dual-link DVI / HDMI 1.4 / Ethernet / Fiber",
            "other": "Ultra-wide video controller - 8× Gigabit Ethernet, 2× fiber optic, rotation support"
        },
    ]
    
    HUIDU_MODELS = [
        {
            "brand": "Huidu",
            "model": "A3",
            "range": "1280 × 512",
            "max_w": 4096,
            "max_h": 2048,
            "storage": "8 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A3L",
            "range": "1280 × 512",
            "max_w": 8192,
            "max_h": 3840,
            "storage": "16 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A4",
            "range": "1280 × 512",
            "max_w": 16384,
            "max_h": 2048,
            "storage": "8 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A4L",
            "range": "1280 × 512",
            "max_w": 16384,
            "max_h": 4096,
            "storage": "16 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired netwokr / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A5",
            "range": "1280 × 1024",
            "max_w": 16384,
            "max_h": 2048,
            "storage": "8 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A5L",
            "range": "1280 × 1024",
            "max_w": 16384,
            "max_h": 4096,
            "storage": "16 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 4G / 5G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A6",
            "range": "1920 × 1200",
            "max_w": 16384,
            "max_h": 4096,
            "storage": "8 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A6L",
            "range": "1920 × 1356",
            "max_w": 65536,
            "max_h": 4096,
            "storage": "16 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 4G / 5G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A7",
            "range": "3840 × 1344",
            "max_w": 65536,
            "max_h": 2160,
            "storage": "32 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 4G / 5G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "A8",
            "range": "3840 × 2160",
            "max_w": 65536,
            "max_h": 2160,
            "storage": "32 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 4G / 5G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "B6",
            "range": "1920 × 1200",
            "max_w": 3840,
            "max_h": 4096,
            "storage": "8 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "B6L",
            "range": "1920 × 1356",
            "max_w": 16384,
            "max_h": 4096,
            "storage": "16 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 4G / 5G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "C08L",
            "range": "1024 × 192",
            "max_w": 2048,
            "max_h": 1024,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "C15",
            "range": "384 × 320",
            "max_w": 1024,
            "max_h": 512,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "C16",
            "range": "640 × 320",
            "max_w": 8192,
            "max_h": 1024,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "C16L",
            "range": "1280 × 510",
            "max_w": 8192,
            "max_h": 1920,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "C35",
            "range": "1024 × 512",
            "max_w": 1024,
            "max_h": 1024,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "C36",
            "range": "1024 × 512",
            "max_w": 8192,
            "max_h": 1024,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": "Two-channel stereo"
        },
        {
            "brand": "Huidu",
            "model": "D15",
            "range": "640 × 64",
            "max_w": 640,
            "max_h": 128,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": ""
        },
        {
            "brand": "Huidu",
            "model": "D16",
            "range": "1024 × 64",
            "max_w": 1024,
            "max_h": 256,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": ""
        },
        {
            "brand": "Huidu",
            "model": "D18",
            "range": "640 × 128",
            "max_w": 1024,
            "max_h": 256,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "U disk / Wi‑Fi / 3G / 4G",
            "other": ""
        },
        {
            "brand": "Huidu",
            "model": "D35",
            "range": "1024 × 64",
            "max_w": 1024,
            "max_h": 128,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": ""
        },
        {
            "brand": "Huidu",
            "model": "D36",
            "range": "1024 × 64",
            "max_w": 1024,
            "max_h": 256,
            "storage": "4 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 3G / 4G / Wi‑Fi",
            "other": ""
        },
        {
            "brand": "Huidu",
            "model": "H4K",
            "range": "3840 × 2160",
            "max_w": 32768,
            "max_h": 4096,
            "storage": "16 GB",
            "gray": "256 ~ 65536",
            "iface": "Wired network / U disk / 4G / 5G / Wi‑Fi",
            "other": "Two-channel stereo"
        }
    ]
    
    @classmethod
    def populate_database(cls, force_update: bool = False) -> bool:
        """
        Populate the controller database with comprehensive research data.
        
        Args:
            force_update: If True, update existing models. If False, only add new ones.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            db = get_controller_database()
            all_models = cls.NOVASTAR_MODELS + cls.HUIDU_MODELS
            
            added_count = 0
            updated_count = 0
            
            for model_data in all_models:
                brand = model_data["brand"]
                model = model_data["model"]
                
                # Check if model already exists
                existing = db.get_model_spec(brand, model)
                
                if existing and not force_update:
                    logger.debug(f"Model {brand} {model} already exists, skipping")
                    continue
                
                # Prepare specs dict
                specs = {
                    "range": model_data.get("range"),
                    "max_w": model_data.get("max_w"),
                    "max_h": model_data.get("max_h"),
                    "storage": model_data.get("storage"),
                    "gray": model_data.get("gray"),
                    "iface": model_data.get("iface"),
                    "other": model_data.get("other"),
                }
                
                if db.upsert_controller_model(brand, model, specs):
                    if existing:
                        updated_count += 1
                        logger.info(f"Updated {brand} {model} in database")
                    else:
                        added_count += 1
                        logger.info(f"Added {brand} {model} to database")
                else:
                    logger.warning(f"Failed to add/update {brand} {model}")
            
            logger.info(f"Database population complete: {added_count} added, {updated_count} updated")
            return True
            
        except Exception as e:
            logger.exception(f"Error populating controller database: {e}")
            return False
    
    @classmethod
    def get_all_models_by_brand(cls, brand: str) -> List[Dict[str, Any]]:
        """
        Get all models for a brand from the database.
        
        Args:
            brand: Brand name (e.g., "NovaStar", "Huidu")
        
        Returns:
            List of model dictionaries
        """
        try:
            db = get_controller_database()
            return db.get_models_by_brand(brand)
        except Exception as e:
            logger.exception(f"Error getting models by brand: {e}")
            return []
    
    @classmethod
    def get_model_info(cls, brand: str, model: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific model.
        
        Args:
            brand: Brand name
            model: Model name
        
        Returns:
            Dictionary with model information
        """
        try:
            db = get_controller_database()
            spec = db.get_model_spec(brand, model)
            
            if spec:
                return {
                    "brand": spec.get("brand"),
                    "model": spec.get("model"),
                    "suggested_range": spec.get("suggested_range"),
                    "max_width": spec.get("max_width"),
                    "max_height": spec.get("max_height"),
                    "storage_capacity": spec.get("storage_capacity"),
                    "gray_scale": spec.get("gray_scale"),
                    "communication_interface": spec.get("communication_interface"),
                    "other": spec.get("other"),
                }
            
            return {}
        except Exception as e:
            logger.exception(f"Error getting model info: {e}")
            return {}
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """
        Get statistics about the controller database.
        
        Returns:
            Dictionary with statistics
        """
        try:
            db = get_controller_database()
            
            novastar_models = db.get_models_by_brand("NovaStar")
            huidu_models = db.get_models_by_brand("Huidu")
            
            return {
                "novastar_count": len(novastar_models),
                "huidu_count": len(huidu_models),
                "total_count": len(novastar_models) + len(huidu_models),
                "novastar_models": [m.get("model") for m in novastar_models],
                "huidu_models": [m.get("model") for m in huidu_models],
            }
        except Exception as e:
            logger.exception(f"Error getting statistics: {e}")
            return {
                "novastar_count": 0,
                "huidu_count": 0,
                "total_count": 0,
                "novastar_models": [],
                "huidu_models": [],
            }

