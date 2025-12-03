from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import os


@dataclass
class FileInfo:
    localFile: str
    url: Optional[str] = None
    size: int = 0
    md5: Optional[str] = None

    def __post_init__(self):
        # Normalized path separator
        self.localFile = os.path.normpath(self.localFile)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileInfo):
            return False

        if self is other:
            return True

        try:
            return (
                    Path(self.localFile).resolve() ==
                    Path(other.localFile).resolve()
            )
        except (OSError, RuntimeError):
            # If path resolution fails (e.g. file does not exist), compare the string directly
            return self.localFile == other.localFile

    def __hash__(self) -> int:
        try:
            # The hash is calculated using the parsed absolute path
            return hash(Path(self.localFile).resolve())
        except (OSError, RuntimeError):
            # If path parsing fails, use the original string
            return hash(self.localFile)

    @property
    def exists(self) -> bool:
        return Path(self.localFile).exists()

    @property
    def is_remote(self) -> bool:
        return bool(self.url and self.url.startswith(('http://', 'https://')))

    def to_dict(self) -> dict:
        return {
            'localFile': self.localFile,
            'url': self.url,
            'size': self.size,
            'md5': self.md5
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FileInfo':
        return cls(
            localFile=data.get('localFile', ''),
            url=data.get('url'),
            size=data.get('size', 0),
            md5=data.get('md5')
        )