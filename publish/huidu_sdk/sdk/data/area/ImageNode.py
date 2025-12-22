from enum import Enum
from typing import List, Optional
from sdk.data.area.ContentNode import ContentNode  # Import base class
from sdk.data.other.Effect import Effect
from sdk.data.other.FileInfo import FileInfo


class ImageNode(ContentNode):
    class Fit(Enum):
        FILL = "fill"  # Fill the area by cropping
        CENTER = "center"  # Center with black bars
        STRETCH = "stretch"  # Stretch to fit (may distort)
        TILE = "tile"  # Tile the image

        def get_value(self) -> str:
            return self.value

    def __init__(self, *args):
        super().__init__()
        self.set_type("image")  # Set node type to "image"

        # Initialize fields with default values
        self.localPath: Optional[str] = None
        self.file: Optional[str] = None  # URL for remote file
        self.fileSize: int = 0
        self.fileMd5: Optional[str] = None
        self.effect: Optional[Effect] = None
        self.fit: ImageNode.Fit = self.Fit.STRETCH  # Default fit

        # Handle different argument patterns
        if len(args) == 1:
            if isinstance(args[0], ImageNode):
                # Copy constructor
                self._copy_from(args[0])
            else:
                # Local path constructor
                self.localPath = args[0]
        elif len(args) == 2:
            # Local path + fit
            self.localPath = args[0]
            self.fit = args[1]
        elif len(args) == 3:
            # Remote file info (url, size, md5)
            self.localPath = args[0]  # url is stored in localPath
            self.file = args[0]  # also store in file field
            self.fileSize = args[1]
            self.fileMd5 = args[2]
        elif len(args) == 4:
            # Remote file info + fit
            self.localPath = args[0]
            self.file = args[0]
            self.fileSize = args[1]
            self.fileMd5 = args[2]
            self.fit = args[3]

    def _copy_from(self, other: 'ImageNode'):
        super()._copy_from(other)  # Copy base class properties
        self.localPath = other.localPath
        self.file = other.file
        self.fileSize = other.fileSize
        self.fileMd5 = other.fileMd5
        self.effect = other.effect
        self.fit = other.fit

    def get_files_info(self) -> List[FileInfo]:
        if not self.localPath:
            return []

        file_info = FileInfo(self.localPath)
        file_info.md5 = self.fileMd5
        file_info.size = self.fileSize
        file_info.url = self.file
        return [file_info]

    def update_files_info(self, files_info: List[FileInfo]):
        if not self.localPath:
            return

        current_file = FileInfo(self.localPath)
        for file_info in files_info:
            if file_info == current_file:
                self.fileMd5 = file_info.md5
                self.fileSize = file_info.size
                self.file = file_info.url
                break

    # Property accessors
    def get_file(self) -> Optional[str]:
        return self.file

    def set_file(self, file_url: str):
        self.file = file_url

    def get_file_size(self) -> int:
        return self.fileSize

    def set_file_size(self, size: int):
        self.fileSize = size

    def get_file_md5(self) -> Optional[str]:
        return self.fileMd5

    def set_file_md5(self, md5: str):
        self.fileMd5 = md5

    def get_effect(self) -> Optional[Effect]:
        return self.effect

    def set_effect(self, effect: Effect):
        self.effect = effect

    def get_fit(self) -> Fit:
        return self.fit

    def set_fit(self, fit: Fit):
        self.fit = fit

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "localPath": self.localPath,
            "file": self.file,
            "fileSize": self.fileSize,
            "fileMd5": self.fileMd5,
            "effect": self.effect.to_dict() if self.effect else None,
            "fit": self.fit.get_value() if self.fit else None
        })
        return data

    def __repr__(self) -> str:
        return (f"ImageNode(uuid={self.id}, name='{self.name}', "
                f"localPath='{self.localPath}', fit={self.fit.name})")