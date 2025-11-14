"""
Undo/Redo system for program editing
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from copy import deepcopy


class Command:
    """Base command class for undo/redo"""
    
    def execute(self):
        """Execute the command"""
        raise NotImplementedError
    
    def undo(self):
        """Undo the command"""
        raise NotImplementedError


class ElementCommand(Command):
    """Command for element operations"""
    
    def __init__(self, program, element_id: str, operation: str, old_data: Dict, new_data: Dict):
        self.program = program
        self.element_id = element_id
        self.operation = operation  # 'add', 'delete', 'modify', 'move'
        self.old_data = deepcopy(old_data) if old_data else None
        self.new_data = deepcopy(new_data) if new_data else None
    
    def execute(self):
        """Execute the command"""
        if self.operation == 'add' and self.new_data:
            self.program.elements.append(self.new_data)
        elif self.operation == 'delete':
            self.program.elements = [e for e in self.program.elements if e.get("id") != self.element_id]
        elif self.operation == 'modify':
            for i, elem in enumerate(self.program.elements):
                if elem.get("id") == self.element_id:
                    self.program.elements[i] = self.new_data
                    break
        elif self.operation == 'move':
            for elem in self.program.elements:
                if elem.get("id") == self.element_id:
                    elem.update(self.new_data)
                    break
    
    def undo(self):
        """Undo the command"""
        if self.operation == 'add':
            self.program.elements = [e for e in self.program.elements if e.get("id") != self.element_id]
        elif self.operation == 'delete' and self.old_data:
            self.program.elements.append(self.old_data)
        elif self.operation == 'modify' and self.old_data:
            for i, elem in enumerate(self.program.elements):
                if elem.get("id") == self.element_id:
                    self.program.elements[i] = self.old_data
                    break
        elif self.operation == 'move' and self.old_data:
            for elem in self.program.elements:
                if elem.get("id") == self.element_id:
                    elem.update(self.old_data)
                    break


class UndoRedoManager:
    """Manages undo/redo history"""
    
    def __init__(self, max_history: int = 50):
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_history = max_history
    
    def execute_command(self, command: Command):
        """Execute a command and add to undo stack"""
        command.execute()
        self.undo_stack.append(command)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        # Clear redo stack when new command is executed
        self.redo_stack.clear()
    
    def undo(self) -> bool:
        """Undo last command"""
        if not self.undo_stack:
            return False
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """Redo last undone command"""
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        return True
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return len(self.redo_stack) > 0
    
    def clear(self):
        """Clear all history"""
        self.undo_stack.clear()
        self.redo_stack.clear()

