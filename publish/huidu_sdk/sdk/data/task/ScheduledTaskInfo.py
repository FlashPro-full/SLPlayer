from typing import Optional
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class ScheduledTaskInfo:
    time_range: Optional[str] = None
    date_range: Optional[str] = None
    week_filter: Optional[str] = None
    month_filter: Optional[str] = None
    data: Optional[str] = None

    def __init__(self,
                 data: Optional[str] = None,
                 time_range: Optional[str] = None,
                 date_range: Optional[str] = None,
                 week_filter: Optional[str] = None,
                 month_filter: Optional[str] = None):
        self.data = data
        self.time_range = time_range
        self.date_range = date_range
        self.week_filter = week_filter
        self.month_filter = month_filter

    def copy(self) -> 'ScheduledTaskInfo':
        return deepcopy(self)

    @property
    def time_range(self) -> Optional[str]:
        return self._time_range

    @time_range.setter
    def time_range(self, value: Optional[str]):
        self._time_range = value

    @property
    def date_range(self) -> Optional[str]:
        return self._date_range

    @date_range.setter
    def date_range(self, value: Optional[str]):
        self._date_range = value

    @property
    def week_filter(self) -> Optional[str]:
        return self._week_filter

    @week_filter.setter
    def week_filter(self, value: Optional[str]):
        self._week_filter = value

    @property
    def month_filter(self) -> Optional[str]:
        return self._month_filter

    @month_filter.setter
    def month_filter(self, value: Optional[str]):
        self._month_filter = value

    @property
    def data(self) -> Optional[str]:
        return self._data

    @data.setter
    def data(self, value: Optional[str]):
        self._data = value

    def to_dict(self) -> dict:
        return {
            "timeRange": self.time_range,
            "dateRange": self.date_range,
            "weekFilter": self.week_filter,
            "monthFilter": self.month_filter,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduledTaskInfo':
        return cls(
            data.get("data"),
            data.get("timeRange"),
            data.get("dateRange"),
            data.get("weekFilter"),
            data.get("monthFilter")
        )

    def __repr__(self) -> str:
        return (f"ScheduledTaskInfo(time_range={self.time_range!r}, "
                f"date_range={self.date_range!r}, "
                f"week_filter={self.week_filter!r}, "
                f"month_filter={self.month_filter!r}, "
                f"data={self.data!r})")