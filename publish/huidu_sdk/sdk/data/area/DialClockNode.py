from typing import Optional
from sdk.data.area.ContentNode import ContentNode
from sdk.data.other.Font import Font
from sdk.data.other.ClockParam import ClockParam


class DialClockNode(ContentNode):
    def __init__(self, other: Optional['DialClockNode'] = None):
        super().__init__()
        self.set_type("dialClock")  # Set node type

        self.timezone: Optional[str] = None
        self.timeOffset: Optional[str] = None
        self.font: Optional[Font] = None
        self.title: ClockParam.StringColor = ClockParam.StringColor()
        self.title.display = "0"  # Set default display value
        self.date: Optional[ClockParam.FormatColor] = None
        self.week: Optional[ClockParam.FormatColor] = None
        self.time: Optional[ClockParam.FormatColor] = None
        self.ampm: Optional[ClockParam.FormatColor] = None
        self.style: Optional[ClockParam.Style] = None
        self.spacing: int = 0
        self.enabled12H: bool = False
        self.swapWeekAndDay: bool = False

        if other:
            self._copy_from(other)

    def _copy_from(self, other: 'DialClockNode'):
        super()._copy_from(other)  # Copy base class properties
        self.timezone = other.timezone
        self.timeOffset = other.timeOffset
        self.font = other.font
        self.title = other.title
        self.date = other.date
        self.week = other.week
        self.time = other.time
        self.ampm = other.ampm
        self.style = other.style
        self.spacing = other.spacing
        self.enabled12H = other.enabled12H
        self.swapWeekAndDay = other.swapWeekAndDay

    def get_timezone(self) -> Optional[str]:
        return self.timezone

    def set_timezone(self, timezone: str):
        self.timezone = timezone

    def get_time_offset(self) -> Optional[str]:
        return self.timeOffset

    def set_time_offset(self, time_offset: str):
        self.timeOffset = time_offset

    def get_font(self) -> Optional[Font]:
        return self.font

    def set_font(self, font: Font):
        self.font = font

    def get_title(self) -> ClockParam.StringColor:
        return self.title

    def set_title(self, title: ClockParam.StringColor):
        self.title = title

    def get_date(self) -> Optional[ClockParam.FormatColor]:
        return self.date

    def set_date(self, date: ClockParam.FormatColor):
        self.date = date

    def get_week(self) -> Optional[ClockParam.FormatColor]:
        return self.week

    def set_week(self, week: ClockParam.FormatColor):
        self.week = week

    def get_time(self) -> Optional[ClockParam.FormatColor]:
        return self.time

    def set_time(self, time: ClockParam.FormatColor):
        self.time = time

    def get_style(self) -> Optional[ClockParam.Style]:
        return self.style

    def set_style(self, style: ClockParam.Style):
        self.style = style

    def get_ampm(self) -> Optional[ClockParam.FormatColor]:
        return self.ampm

    def set_ampm(self, ampm: ClockParam.FormatColor):
        self.ampm = ampm

    def get_enabled12H(self) -> bool:
        return self.enabled12H

    def set_enabled12H(self, enabled: bool):
        self.enabled12H = enabled

    def get_swap_week_and_day(self) -> bool:
        return self.swapWeekAndDay

    def set_swap_week_and_day(self, swap: bool):
        self.swapWeekAndDay = swap

    def get_spacing(self) -> int:
        return self.spacing

    def set_spacing(self, spacing: int):
        self.spacing = spacing

    def get_clock_fmt_style(self) -> ClockParam.FmtStyle:
        fmt_style = ClockParam.FmtStyle()
        if self.swapWeekAndDay:
            fmt_style.swap = "1"
        if self.spacing > 0:
            fmt_style.space = str(self.spacing)
        return fmt_style

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "timezone": self.timezone,
            "timeOffset": self.timeOffset,
            "font": self.font.to_dict() if self.font else None,
            "title": self.title.__dict__ if self.title else None,
            "date": self.date.__dict__ if self.date else None,
            "week": self.week.__dict__ if self.week else None,
            "time": self.time.__dict__ if self.time else None,
            "ampm": self.ampm.__dict__ if self.ampm else None,
            "style": self.style.__dict__ if self.style else None,
            "spacing": self.spacing,
            "enabled12H": self.enabled12H,
            "swapWeekAndDay": self.swapWeekAndDay
        })
        return data

    def __repr__(self) -> str:
        return (f"DialClockNode(uuid={self.id}, name='{self.name}', "
                f"timezone='{self.timezone}', enabled12H={self.enabled12H})")