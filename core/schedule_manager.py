"""
Schedule manager for program scheduling
"""
from typing import List, Dict, Optional
from datetime import datetime, time, date
from enum import Enum


class ScheduleRuleType(Enum):
    """Schedule rule types"""
    TIME_BASED = "time_based"
    DAY_OF_WEEK = "day_of_week"
    DATE_SPECIFIC = "date_specific"
    PLAYLIST = "playlist"


class ScheduleRule:
    """Represents a scheduling rule"""
    
    def __init__(self, rule_type: ScheduleRuleType, program_id: str):
        self.rule_type = rule_type
        self.program_id = program_id
        self.enabled = True
        self.priority = 0
        self.start_time: Optional[time] = None
        self.end_time: Optional[time] = None
        self.days_of_week: List[int] = []  # 0=Monday, 6=Sunday
        self.specific_dates: List[date] = []
        self.playlist: List[str] = []  # List of program IDs
    
    def to_dict(self) -> Dict:
        """Convert rule to dictionary"""
        return {
            "type": self.rule_type.value,
            "program_id": self.program_id,
            "enabled": self.enabled,
            "priority": self.priority,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "days_of_week": self.days_of_week,
            "specific_dates": [d.isoformat() for d in self.specific_dates],
            "playlist": self.playlist
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScheduleRule':
        """Create rule from dictionary"""
        rule_type = ScheduleRuleType(data.get("type", "time_based"))
        rule = cls(rule_type, data.get("program_id", ""))
        rule.enabled = data.get("enabled", True)
        rule.priority = data.get("priority", 0)
        
        if data.get("start_time"):
            rule.start_time = time.fromisoformat(data["start_time"])
        if data.get("end_time"):
            rule.end_time = time.fromisoformat(data["end_time"])
        
        rule.days_of_week = data.get("days_of_week", [])
        rule.specific_dates = [date.fromisoformat(d) for d in data.get("specific_dates", [])]
        rule.playlist = data.get("playlist", [])
        
        return rule
    
    def matches(self, check_time: datetime) -> bool:
        """Check if rule matches given time"""
        if not self.enabled:
            return False
        
        current_time = check_time.time()
        current_date = check_time.date()
        current_weekday = check_time.weekday()  # 0=Monday, 6=Sunday
        
        if self.rule_type == ScheduleRuleType.TIME_BASED:
            if self.start_time and self.end_time:
                return self.start_time <= current_time <= self.end_time
            return True
        
        elif self.rule_type == ScheduleRuleType.DAY_OF_WEEK:
            if self.days_of_week:
                return current_weekday in self.days_of_week
            return True
        
        elif self.rule_type == ScheduleRuleType.DATE_SPECIFIC:
            if self.specific_dates:
                return current_date in self.specific_dates
            return True
        
        elif self.rule_type == ScheduleRuleType.PLAYLIST:
            return True  # Playlist rules are handled separately
        
        return False


class ScheduleManager:
    """Manages program scheduling"""
    
    def __init__(self):
        self.rules: List[ScheduleRule] = []
        self.enabled = False
    
    def add_rule(self, rule: ScheduleRule):
        """Add a scheduling rule"""
        self.rules.append(rule)
        # Sort by priority (higher priority first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, rule: ScheduleRule):
        """Remove a scheduling rule"""
        if rule in self.rules:
            self.rules.remove(rule)
    
    def get_active_program(self, check_time: datetime = None) -> Optional[str]:
        """Get the program that should be active at given time"""
        if not self.enabled:
            return None
        
        if check_time is None:
            check_time = datetime.now()
        
        # Find matching rules, sorted by priority
        matching_rules = [r for r in self.rules if r.matches(check_time)]
        
        if matching_rules:
            # Return program from highest priority rule
            return matching_rules[0].program_id
        
        return None
    
    def get_rules_for_program(self, program_id: str) -> List[ScheduleRule]:
        """Get all rules for a specific program"""
        return [r for r in self.rules if r.program_id == program_id]
    
    def validate_rules(self) -> List[str]:
        """Validate all rules and return list of errors"""
        errors = []
        
        for i, rule in enumerate(self.rules):
            if rule.rule_type == ScheduleRuleType.TIME_BASED:
                if rule.start_time and rule.end_time:
                    if rule.start_time >= rule.end_time:
                        errors.append(f"Rule {i+1}: Start time must be before end time")
            
            if not rule.program_id:
                errors.append(f"Rule {i+1}: Program ID is required")
        
        return errors
    
    def to_dict(self) -> Dict:
        """Convert schedule to dictionary"""
        return {
            "enabled": self.enabled,
            "rules": [r.to_dict() for r in self.rules]
        }
    
    def from_dict(self, data: Dict):
        """Load schedule from dictionary"""
        self.enabled = data.get("enabled", False)
        self.rules = [ScheduleRule.from_dict(r) for r in data.get("rules", [])]
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def export_to_controller(self, controller) -> bool:
        """
        Export schedule to controller.
        Returns True if successful, False otherwise.
        """
        try:
            if not controller or not controller.is_connected():
                return False
            
            # Convert schedule to controller-compatible format
            schedule_data = self.to_dict()
            
            # Controller-specific export logic
            if hasattr(controller, 'upload_schedule'):
                return controller.upload_schedule(schedule_data)
            else:
                # Fallback: try generic upload method
                if hasattr(controller, 'upload_data'):
                    return controller.upload_data("schedule", schedule_data)
            
            return False
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error exporting schedule to controller: {e}")
            return False
    
    def export_to_file(self, file_path: str) -> bool:
        """Export schedule to JSON file"""
        try:
            import json
            from pathlib import Path
            
            schedule_data = self.to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error exporting schedule to file: {e}")
            return False

