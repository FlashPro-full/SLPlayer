"""
Export handler for converting programs to controller-compatible formats
"""
import json
from typing import Dict, Optional
from pathlib import Path
from core.program_manager import Program
from controllers.base_controller import ControllerType


class ExportHandler:
    """Handles export of programs to controller formats"""
    
    @staticmethod
    def export_to_novastar(program: Program, output_path: str) -> bool:
        """Export program to NovaStar format"""
        try:
            # Convert program to NovaStar-compatible format
            export_data = ExportHandler._convert_to_novastar_format(program)
            
            # Save to file
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to NovaStar: {e}")
            return False
    
    @staticmethod
    def export_to_huidu(program: Program, output_path: str) -> bool:
        """Export program to Huidu format"""
        try:
            # Convert program to Huidu-compatible format
            export_data = ExportHandler._convert_to_huidu_format(program)
            
            # Save to file
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to Huidu: {e}")
            return False
    
    @staticmethod
    def _convert_to_novastar_format(program: Program) -> Dict:
        """Convert program to NovaStar format"""
        return {
            "version": "1.0",
            "controller": "novastar",
            "program": {
                "name": program.name,
                "width": program.width,
                "height": program.height,
                "elements": program.elements,
                "properties": program.properties,
                "play_mode": program.play_mode,
                "play_control": program.play_control
            }
        }
    
    @staticmethod
    def _convert_to_huidu_format(program: Program) -> Dict:
        """Convert program to Huidu format"""
        return {
            "version": "1.0",
            "controller": "huidu",
            "program": {
                "name": program.name,
                "width": program.width,
                "height": program.height,
                "elements": program.elements,
                "properties": program.properties,
                "play_mode": program.play_mode,
                "play_control": program.play_control
            }
        }
    
    @staticmethod
    def export_to_file(program: Program, output_path: str, format_type: str = "json") -> bool:
        """Export program to file in specified format"""
        if format_type.lower() == "novastar":
            return ExportHandler.export_to_novastar(program, output_path)
        elif format_type.lower() == "huidu":
            return ExportHandler.export_to_huidu(program, output_path)
        else:
            # Default JSON format
            try:
                output_file = Path(output_path)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(program.to_dict(), f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"Error exporting program: {e}")
                return False

