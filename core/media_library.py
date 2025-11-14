"""
Media library with SQLite database and thumbnail generation
"""
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from PyQt6.QtGui import QPixmap, QImage, QColor
from PyQt6.QtCore import QSize, Qt

from utils.logger import get_logger
from config.constants import SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS

logger = get_logger(__name__)


class MediaLibrary:
    """Media library with database and thumbnail support"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize media library"""
        if db_path is None:
            db_path = Path.home() / ".slplayer" / "media_library.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir = db_path.parent / "thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create media_files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    width INTEGER,
                    height INTEGER,
                    duration REAL,
                    thumbnail_path TEXT,
                    added_date TEXT NOT NULL,
                    last_used_date TEXT,
                    usage_count INTEGER DEFAULT 0,
                    tags TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_type ON media_files(file_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_added_date ON media_files(added_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON media_files(tags)")
            
            conn.commit()
            conn.close()
            logger.info("Media library database initialized")
        except Exception as e:
            logger.exception(f"Error initializing media library database: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def _generate_thumbnail(self, file_path: Path, file_type: str) -> Optional[Path]:
        """Generate thumbnail for media file"""
        try:
            file_hash = self._calculate_file_hash(file_path)
            thumbnail_path = self.thumbnail_dir / f"{file_hash}.png"
            
            # If thumbnail already exists, return it
            if thumbnail_path.exists():
                return thumbnail_path
            
            if file_type == "image":
                # Generate thumbnail for image
                pixmap = QPixmap(str(file_path))
                if not pixmap.isNull():
                    # Scale to thumbnail size (200x200 max, maintain aspect ratio)
                    scaled = pixmap.scaled(
                        200, 200,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    scaled.save(str(thumbnail_path), "PNG")
                    return thumbnail_path
            
            elif file_type == "video":
                # Generate thumbnail for video (first frame)
                try:
                    from PyQt6.QtMultimedia import QMediaPlayer
                    from PyQt6.QtCore import QUrl
                    
                    player = QMediaPlayer()
                    player.setSource(QUrl.fromLocalFile(str(file_path)))
                    
                    # Wait for media to load (simplified - in production use signals)
                    # For now, we'll create a placeholder
                    placeholder = QPixmap(200, 150)
                    placeholder.fill(QColor(50, 50, 50))
                    placeholder.save(str(thumbnail_path), "PNG")
                    return thumbnail_path
                except Exception as e:
                    logger.warning(f"Could not generate video thumbnail: {e}")
                    # Create placeholder
                    from PyQt6.QtGui import QColor
                    placeholder = QPixmap(200, 150)
                    placeholder.fill(QColor(50, 50, 50))
                    placeholder.save(str(thumbnail_path), "PNG")
                    return thumbnail_path
            
            return None
        except Exception as e:
            logger.exception(f"Error generating thumbnail for {file_path}: {e}")
            return None
    
    def add_media_file(self, file_path: str, tags: List[str] = None, 
                      metadata: Dict = None) -> bool:
        """Add media file to library"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Media file not found: {file_path}")
                return False
            
            # Determine file type
            ext = path.suffix.lower().lstrip('.')
            if ext in SUPPORTED_IMAGE_FORMATS:
                file_type = "image"
            elif ext in SUPPORTED_VIDEO_FORMATS:
                file_type = "video"
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return False
            
            # Get file info
            file_size = path.stat().st_size
            file_hash = self._calculate_file_hash(path)
            
            # Generate thumbnail
            thumbnail_path = self._generate_thumbnail(path, file_type)
            
            # Get image/video dimensions
            width = None
            height = None
            duration = None
            
            if file_type == "image":
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    width = pixmap.width()
                    height = pixmap.height()
            
            # Insert into database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            tags_str = ",".join(tags) if tags else ""
            metadata_str = str(metadata) if metadata else ""
            
            cursor.execute("""
                INSERT OR REPLACE INTO media_files 
                (file_path, file_hash, file_type, file_size, width, height, duration,
                 thumbnail_path, added_date, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(path.absolute()),
                file_hash,
                file_type,
                file_size,
                width,
                height,
                duration,
                str(thumbnail_path) if thumbnail_path else None,
                datetime.now().isoformat(),
                tags_str,
                metadata_str
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added media file to library: {file_path}")
            return True
        except Exception as e:
            logger.exception(f"Error adding media file to library: {e}")
            return False
    
    def get_media_files(self, file_type: Optional[str] = None, 
                       tags: List[str] = None, limit: int = 100) -> List[Dict]:
        """Get media files from library"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM media_files WHERE 1=1"
            params = []
            
            if file_type:
                query += " AND file_type = ?"
                params.append(file_type)
            
            if tags:
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            query += " ORDER BY last_used_date DESC, added_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append({
                    "id": row["id"],
                    "file_path": row["file_path"],
                    "file_hash": row["file_hash"],
                    "file_type": row["file_type"],
                    "file_size": row["file_size"],
                    "width": row["width"],
                    "height": row["height"],
                    "duration": row["duration"],
                    "thumbnail_path": row["thumbnail_path"],
                    "added_date": row["added_date"],
                    "last_used_date": row["last_used_date"],
                    "usage_count": row["usage_count"],
                    "tags": row["tags"].split(",") if row["tags"] else [],
                    "metadata": row["metadata"]
                })
            
            conn.close()
            return result
        except Exception as e:
            logger.exception(f"Error getting media files: {e}")
            return []
    
    def update_usage(self, file_path: str):
        """Update usage statistics for media file"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE media_files 
                SET last_used_date = ?, usage_count = usage_count + 1
                WHERE file_path = ?
            """, (datetime.now().isoformat(), str(Path(file_path).absolute())))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.exception(f"Error updating usage: {e}")
    
    def remove_media_file(self, file_path: str) -> bool:
        """Remove media file from library"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get thumbnail path before deleting
            cursor.execute("SELECT thumbnail_path FROM media_files WHERE file_path = ?",
                         (str(Path(file_path).absolute()),))
            row = cursor.fetchone()
            
            # Delete from database
            cursor.execute("DELETE FROM media_files WHERE file_path = ?",
                         (str(Path(file_path).absolute()),))
            
            conn.commit()
            conn.close()
            
            # Delete thumbnail if exists
            if row and row[0]:
                thumbnail_path = Path(row[0])
                if thumbnail_path.exists():
                    thumbnail_path.unlink()
            
            logger.info(f"Removed media file from library: {file_path}")
            return True
        except Exception as e:
            logger.exception(f"Error removing media file: {e}")
            return False
    
    def get_thumbnail(self, file_path: str) -> Optional[QPixmap]:
        """Get thumbnail for media file"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT thumbnail_path FROM media_files WHERE file_path = ?",
                         (str(Path(file_path).absolute()),))
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                thumbnail_path = Path(row[0])
                if thumbnail_path.exists():
                    pixmap = QPixmap(str(thumbnail_path))
                    if not pixmap.isNull():
                        return pixmap
            
            return None
        except Exception as e:
            logger.exception(f"Error getting thumbnail: {e}")
            return None
    
    def scan_directory(self, directory: str, recursive: bool = True) -> int:
        """Scan directory for media files and add to library"""
        count = 0
        try:
            dir_path = Path(directory)
            if not dir_path.exists() or not dir_path.is_dir():
                logger.warning(f"Directory not found: {directory}")
                return 0
            
            pattern = "**/*" if recursive else "*"
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    ext = file_path.suffix.lower().lstrip('.')
                    if ext in SUPPORTED_IMAGE_FORMATS or ext in SUPPORTED_VIDEO_FORMATS:
                        if self.add_media_file(str(file_path)):
                            count += 1
            
            logger.info(f"Scanned {count} media files from {directory}")
            return count
        except Exception as e:
            logger.exception(f"Error scanning directory: {e}")
            return count


# Global media library instance
_media_library_instance: Optional[MediaLibrary] = None

def get_media_library() -> MediaLibrary:
    """Get global media library instance"""
    global _media_library_instance
    if _media_library_instance is None:
        _media_library_instance = MediaLibrary()
    return _media_library_instance

