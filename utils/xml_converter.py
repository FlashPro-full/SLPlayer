import xml.etree.ElementTree as ET
import json
from typing import Any, Dict, List, Union
from utils.logger import get_logger

logger = get_logger(__name__)


class XMLToJSONConverter:
    
    @staticmethod
    def convert(xml_string: str) -> Union[Dict, List, None]:
        """Convert XML string to JSON. Handles both direct XML and JSON-wrapped XML.
        
        Args:
            xml_string: XML string or JSON string containing XML in data[0].data
            
        Returns:
            Converted JSON structure or None on error
        """
        try:
            # Try to parse as JSON first (response might be wrapped in JSON)
            # Example: {"message":"ok", "data":[{"id":"...", "message":"ok", "data":"<xml>...</xml>"}]}
            extracted_xml = None
            try:
                json_response = json.loads(xml_string)
                if isinstance(json_response, dict) and json_response.get("message") == "ok":
                    data_list = json_response.get("data", [])
                    if isinstance(data_list, list) and len(data_list) > 0:
                        first_item = data_list[0]
                        if isinstance(first_item, dict) and "data" in first_item:
                            extracted_xml = first_item.get("data", "")
                            if isinstance(extracted_xml, str):
                                # JSON parser already decodes Unicode escapes (e.g., \u003c -> <)
                                logger.debug(f"Extracted XML from JSON-wrapped response")
            except (json.JSONDecodeError, AttributeError, KeyError, TypeError):
                # Not JSON or doesn't have expected structure, treat as direct XML
                pass
            
            # Use extracted XML if available, otherwise use original string
            xml_to_parse = extracted_xml if extracted_xml else xml_string
            
            # Parse XML
            root = ET.fromstring(xml_to_parse)
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

