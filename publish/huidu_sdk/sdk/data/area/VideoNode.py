from typing import List, Optional
from sdk.data.area.ContentNode import ContentNode  # Import base class
from sdk.data.other.FileInfo import FileInfo  # Import dependency class


class VideoNode(ContentNode):
    def __init__(self, *args):
        super().__init__()
        self.set_type("video")  # Set node type to "video"

        self.localPath: Optional[str] = None
        self.file: Optional[str] = None  # URL for remote file
        self.fileSize: int = 0
        self.fileMd5: Optional[str] = None
        self.aspectRatio: bool = False  # Default aspect ratio

        if len(args) == 1:
            if isinstance(args[0], VideoNode):
                self._copy_from(args[0])
            else:
                self.localPath = args[0]
        elif len(args) == 2:
            if isinstance(args[1], bool):
                self.localPath = args[0]
                self.aspectRatio = args[1]
            else:
                self.localPath = args[0]
                self.file = args[0]
                self.fileSize = args[1]
        elif len(args) == 3:
            self.localPath = args[0]  # url is stored in localPath
            self.file = args[0]  # also store in file field
            self.fileSize = args[1]
            self.fileMd5 = args[2]
        elif len(args) == 4:
            self.localPath = args[0]
            self.file = args[0]
            self.fileSize = args[1]
            self.fileMd5 = args[2]
            self.aspectRatio = args[3]

    def _copy_from(self, other: 'VideoNode'):
        super()._copy_from(other)  # Copy base class properties
        self.localPath = other.localPath
        self.file = other.file
        self.fileSize = other.fileSize
        self.fileMd5 = other.fileMd5
        self.aspectRatio = other.aspectRatio

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

    def get_aspect_ratio(self) -> bool:
        return self.aspectRatio

    def set_aspect_ratio(self, aspect_ratio: bool):
        self.aspectRatio = aspect_ratio

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "localPath": self.localPath,
            "file": self.file,
            "fileSize": self.fileSize,
            "fileMd5": self.fileMd5,
            "aspectRatio": self.aspectRatio
        })
        return data

    def __repr__(self) -> str:
        return (f"VideoNode(uuid={self.id}, name='{self.name}', "
                f"localPath='{self.localPath}', aspectRatio={self.aspectRatio})")