"""
Timer/Countdown widget implementation
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class TimerWidget:
    """Timer/Countdown widget for timing displays"""
    
    def __init__(self, properties: Dict[str, Any]):
        self.properties = properties
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.is_running = False
        self.is_countdown = properties.get("mode", "countdown") == "countdown"
        self.duration_seconds = properties.get("duration", 60)  # Default 60 seconds
    
    def start(self):
        """Start the timer"""
        self.is_running = True
        if self.is_countdown:
            self.end_time = datetime.now() + timedelta(seconds=self.duration_seconds)
        else:
            self.start_time = datetime.now()
    
    def stop(self):
        """Stop the timer"""
        self.is_running = False
    
    def reset(self):
        """Reset the timer"""
        self.start_time = None
        self.end_time = None
        self.is_running = False
    
    def get_display_text(self) -> str:
        """Get the current display text"""
        if not self.is_running:
            if self.is_countdown:
                return self.format_time(self.duration_seconds)
            else:
                return "00:00:00"
        
        now = datetime.now()
        
        if self.is_countdown:
            if self.end_time:
                remaining = (self.end_time - now).total_seconds()
                if remaining <= 0:
                    self.is_running = False
                    return "00:00:00"
                return self.format_time(int(remaining))
            return "00:00:00"
        else:
            if self.start_time:
                elapsed = (now - self.start_time).total_seconds()
                return self.format_time(int(elapsed))
            return "00:00:00"
    
    def format_time(self, seconds: int) -> str:
        """Format seconds as HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


