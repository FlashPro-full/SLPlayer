from enum import Enum
from datetime import date, time
from typing import List, Optional
import json


class PlayControl:
    class Weekday(Enum):
        Mon = "Mon"
        Tue = "Tue"
        Wed = "Wed"
        Thur = "Thur"
        Fri = "Fri"
        Sat = "Sat"
        Sun = "Sun"

    class Date:

        def __init__(self, start: Optional[date] = None, end: Optional[date] = None):
            self.start = start  # Start date of the range
            self.end = end  # End date of the range

        def to_dict(self):
            return {
                "start": self.start.isoformat() if self.start else None,
                "end": self.end.isoformat() if self.end else None
            }

        @classmethod
        def from_dict(cls, data: dict):
            start = date.fromisoformat(data["start"]) if data.get("start") else None
            end = date.fromisoformat(data["end"]) if data.get("end") else None
            return cls(start, end)

        def __repr__(self):
            return f"Date(start={self.start}, end={self.end})"

    class Time:

        def __init__(self, start: Optional[time] = None, end: Optional[time] = None):
            self.start = start  # Start time of the range
            self.end = end  # End time of the range

        def to_dict(self):
            return {
                "start": self.start.isoformat() if self.start else None,
                "end": self.end.isoformat() if self.end else None
            }

        @classmethod
        def from_dict(cls, data: dict):
            start = time.fromisoformat(data["start"]) if data.get("start") else None
            end = time.fromisoformat(data["end"]) if data.get("end") else None
            return cls(start, end)

        def __repr__(self):
            return f"Time(start={self.start}, end={self.end})"

    class Week:

        def __init__(self, other: Optional['PlayControl.Week'] = None):
            if other:
                # Copy constructor
                self._enable = other.enable_weekdays.copy() if other.enable_weekdays else []
            else:
                self._enable = []  # List of enabled Weekday enums

        @property
        def enable_weekdays(self) -> List['PlayControl.Weekday']:
            return self._enable

        @enable_weekdays.setter
        def enable_weekdays(self, value: List['PlayControl.Weekday']):
            self._enable = value

        @property
        def enable(self) -> str:
            return ",".join(day.value for day in self._enable)

        @enable.setter
        def enable(self, value: str):
            if not value:
                self._enable = []
                return

            new_enable = []
            for item in value.split(","):
                try:
                    # Map string value to Weekday enum
                    weekday = next(w for w in PlayControl.Weekday if w.value == item.strip())
                    new_enable.append(weekday)
                except StopIteration:
                    # Skip invalid values
                    continue
            self._enable = new_enable

        def to_dict(self):
            return {"enable": self.enable}

        @classmethod
        def from_dict(cls, data: dict):
            week = cls()
            if "enable" in data:
                week.enable = data["enable"]
            return week

        def __repr__(self):
            return f"Week(enable={[d.value for d in self._enable]})"

    def __init__(self, other: Optional['PlayControl'] = None):
        if other:
            # Copy constructor
            self.date = [PlayControl.Date(d.start, d.end) for d in other.date]
            self.time = [PlayControl.Time(t.start, t.end) for t in other.time]
            self.week = PlayControl.Week(other.week)
        else:
            self.date = []  # List of Date ranges
            self.time = []  # List of Time ranges
            self.week = PlayControl.Week()  # Week configuration

    def to_dict(self):
        return {
            "date": [d.to_dict() for d in self.date],
            "time": [t.to_dict() for t in self.time],
            "week": self.week.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        pc = cls()
        pc.date = [PlayControl.Date.from_dict(d) for d in data.get("date", [])]
        pc.time = [PlayControl.Time.from_dict(t) for t in data.get("time", [])]
        pc.week = PlayControl.Week.from_dict(data.get("week", {}))
        return pc

    def __repr__(self):
        return (f"PlayControl(date={self.date}, time={self.time}, week={self.week})")