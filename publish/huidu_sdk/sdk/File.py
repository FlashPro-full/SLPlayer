from sdk.common.BaseClient import BaseClient

class File(BaseClient):
    def upload_file(self, file_path: str) -> dict:
        return self.file(file_path)