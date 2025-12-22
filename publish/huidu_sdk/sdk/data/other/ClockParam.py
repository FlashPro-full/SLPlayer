class ClockParam:
    class FormatColor:
        def __init__(self, display: str = None, format: str = None,
                     color: str = None, size: int = None):
            self.display = display  # Text to display
            self.format = format    # Format pattern (e.g., "HH:mm:ss")
            self.color = color      # Text color value
            self.size = size        # Font size

    class StringColor:
        def __init__(self, display: str = None, string: str = None,
                     size: int = None, color: str = None):
            self.display = display  # Display label
            self.string = string    # Actual string content
            self.size = size         # Font size
            self.color = color       # Text color value

    class Style:
        def __init__(self, hourHandColor: str = None, minuteHandColor: str = None,
                     secondHandColor: str = None, hourScaleColor: str = None,
                     minuteScaleColor: str = None, fontName: str = None,
                     fontSize: int = None):
            self.hourHandColor = hourHandColor    # Hour hand color
            self.minuteHandColor = minuteHandColor  # Minute hand color
            self.secondHandColor = secondHandColor  # Second hand color
            self.hourScaleColor = hourScaleColor    # Hour scale/mark color
            self.minuteScaleColor = minuteScaleColor  # Minute scale/mark color
            self.fontName = fontName              # Font family name
            self.fontSize = fontSize              # Base font size

    class FmtStyle:
        def __init__(self, swap: str = None, space: str = None):
            self.swap = swap    # AM/PM swap indicator
            self.space = space  # Space formatting character