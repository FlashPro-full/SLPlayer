class PeriodicTaskInfo:
    def __init__(self, *args):
        self.url: str = ""
        self.rege: str = ""
        self.interval: int = 0

        if len(args) == 3:
            # Parameterized constructor
            self.url = args[0]
            self.rege = args[1]
            self.interval = args[2]
        elif len(args) == 1 and isinstance(args[0], PeriodicTaskInfo):
            # Copy constructor
            self._copy_from(args[0])

    def _copy_from(self, other: 'PeriodicTaskInfo'):
        self.url = other.url
        self.rege = other.rege
        self.interval = other.interval

    # Property accessors
    def get_url(self) -> str:
        return self.url

    def set_url(self, url: str):
        self.url = url

    def get_rege(self) -> str:
        return self.rege

    def set_rege(self, rege: str):
        self.rege = rege

    def get_interval(self) -> int:
        return self.interval

    def set_interval(self, interval: int):
        self.interval = interval

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "rege": self.rege,
            "interval": self.interval
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get("url", ""),
            data.get("rege", ""),
            data.get("interval", 0)
        )

    def __repr__(self) -> str:
        return (f"PeriodicTaskInfo(url='{self.url}', "
                f"rege='{self.rege}', interval={self.interval})")