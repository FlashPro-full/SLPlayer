"""
Alignment tools for canvas elements
"""
from typing import List, Dict, Optional


class AlignmentTools:
    """Tools for aligning and distributing elements"""
    
    @staticmethod
    def align_left(elements: List[Dict]) -> bool:
        """Align elements to the leftmost position"""
        if not elements:
            return False
        
        leftmost = min(elem.get("x", 0) for elem in elements)
        for elem in elements:
            elem["x"] = leftmost
        return True
    
    @staticmethod
    def align_right(elements: List[Dict]) -> bool:
        """Align elements to the rightmost position"""
        if not elements:
            return False
        
        rightmost = max(elem.get("x", 0) + elem.get("width", 200) for elem in elements)
        for elem in elements:
            elem["x"] = rightmost - elem.get("width", 200)
        return True
    
    @staticmethod
    def align_center_horizontal(elements: List[Dict]) -> bool:
        """Align elements to horizontal center"""
        if not elements:
            return False
        
        # Find center of all elements
        leftmost = min(elem.get("x", 0) for elem in elements)
        rightmost = max(elem.get("x", 0) + elem.get("width", 200) for elem in elements)
        center = (leftmost + rightmost) / 2
        
        for elem in elements:
            elem["x"] = center - elem.get("width", 200) / 2
        return True
    
    @staticmethod
    def align_top(elements: List[Dict]) -> bool:
        """Align elements to the topmost position"""
        if not elements:
            return False
        
        topmost = min(elem.get("y", 0) for elem in elements)
        for elem in elements:
            elem["y"] = topmost
        return True
    
    @staticmethod
    def align_bottom(elements: List[Dict]) -> bool:
        """Align elements to the bottommost position"""
        if not elements:
            return False
        
        bottommost = max(elem.get("y", 0) + elem.get("height", 100) for elem in elements)
        for elem in elements:
            elem["y"] = bottommost - elem.get("height", 100)
        return True
    
    @staticmethod
    def align_center_vertical(elements: List[Dict]) -> bool:
        """Align elements to vertical center"""
        if not elements:
            return False
        
        # Find center of all elements
        topmost = min(elem.get("y", 0) for elem in elements)
        bottommost = max(elem.get("y", 0) + elem.get("height", 100) for elem in elements)
        center = (topmost + bottommost) / 2
        
        for elem in elements:
            elem["y"] = center - elem.get("height", 100) / 2
        return True
    
    @staticmethod
    def distribute_horizontal(elements: List[Dict]) -> bool:
        """Distribute elements horizontally with equal spacing"""
        if len(elements) < 3:
            return False
        
        # Sort by x position
        sorted_elements = sorted(elements, key=lambda e: e.get("x", 0))
        leftmost = sorted_elements[0].get("x", 0)
        rightmost = sorted_elements[-1].get("x", 0) + sorted_elements[-1].get("width", 200)
        
        total_width = sum(elem.get("width", 200) for elem in sorted_elements)
        spacing = (rightmost - leftmost - total_width) / (len(sorted_elements) - 1)
        
        current_x = leftmost
        for elem in sorted_elements:
            elem["x"] = current_x
            current_x += elem.get("width", 200) + spacing
        
        return True
    
    @staticmethod
    def distribute_vertical(elements: List[Dict]) -> bool:
        """Distribute elements vertically with equal spacing"""
        if len(elements) < 3:
            return False
        
        # Sort by y position
        sorted_elements = sorted(elements, key=lambda e: e.get("y", 0))
        topmost = sorted_elements[0].get("y", 0)
        bottommost = sorted_elements[-1].get("y", 0) + sorted_elements[-1].get("height", 100)
        
        total_height = sum(elem.get("height", 100) for elem in sorted_elements)
        spacing = (bottommost - topmost - total_height) / (len(sorted_elements) - 1)
        
        current_y = topmost
        for elem in sorted_elements:
            elem["y"] = current_y
            current_y += elem.get("height", 100) + spacing
        
        return True

