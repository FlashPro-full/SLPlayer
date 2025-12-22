import xml.etree.ElementTree as ET
import json
from typing import Any, Dict, List, Union
from utils.logger import get_logger

logger = get_logger(__name__)


class XMLToJSONConverter:
    
    @staticmethod
    def convert(xml_string: str) -> Union[Dict, List, None]:
        try:
            root = ET.fromstring(xml_string)
            result = XMLToJSONConverter._element_to_dict(root)
            if isinstance(result, str):
                return {"#text": result}
            return result
        except ET.ParseError as e:
            logger.error(f"Error parsing XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Error converting XML to JSON: {e}")
            return None
    
    @staticmethod
    def _element_to_dict(element: ET.Element) -> Union[Dict, str]:
        result: Dict[str, Any] = {}
        
        if element.attrib:
            result["@attributes"] = element.attrib
        
        if element.text and element.text.strip():
            text = element.text.strip()
            if not list(element):
                return text
            result["#text"] = text
        
        children: Dict[str, Any] = {}
        for child in element:
            child_dict = XMLToJSONConverter._element_to_dict(child)
            child_tag = child.tag
            
            if child_tag in children:
                if not isinstance(children[child_tag], list):
                    children[child_tag] = [children[child_tag]]
                if isinstance(children[child_tag], list):
                    children[child_tag].append(child_dict)
            else:
                children[child_tag] = child_dict
        
        if children:
            result.update(children)
        
        if not result:
            return ""
        
        if "@attributes" in result and len(result) == 1:
            return result["@attributes"]
        
        return result
    
    @staticmethod
    def to_json_string(xml_string: str, indent: int = 2) -> str:
        result = XMLToJSONConverter.convert(xml_string)
        if result is None:
            return "{}"
        return json.dumps(result, indent=indent, ensure_ascii=False)


def xml_to_json(xml_string: str) -> Union[Dict, List, None]:
    return XMLToJSONConverter.convert(xml_string)


def xml_to_json_string(xml_string: str, indent: int = 2) -> str:
    return XMLToJSONConverter.to_json_string(xml_string, indent)

