# Conflict Analysis: Controllers vs Saved File Structure

## Overview
This document identifies conflicts between the controllers' expected data structure and the actual saved file structure in SOO files.

## File Structure Summary

### Saved File Structure (SOO Format)
- **Location**: `core/soo_file_config.py`, `core/program_manager.py`
- **Format**: JSON with nested properties structure
- **Program Structure**:
  ```python
  {
    "id": "program_xxx",
    "name": "Program Name",
    "width": 1920,
    "height": 1080,
    "elements": [
      {
        "id": "element_xxx",
        "type": "text|photo|video|animation|clock|timing|weather|sensor|html|hdmi",
        "x": 0,
        "y": 0,
        "width": 200,
        "height": 100,
        "properties": {
          // Nested structure per element type
        }
      }
    ]
  }
  ```

### Controller Expected Structure

#### HuiduController (`controllers/huidu.py`)
- Expects: `element.get("properties", {})`
- Accesses: `properties.get("text")`, `properties.get("font_family")`, `properties.get("color")`
- **Problem**: Expects flat properties, but saved structure is nested

#### NovaStarController (`controllers/novastar.py`)
- Expects: `element.get("properties", {})`
- Accesses: `properties.get("text")`, `properties.get("color")`, `properties.get("file_path")`
- **Problem**: Same flat structure expectation, but nested in saved files

---

## Detailed Conflicts by Element Type

### 1. TEXT Element

**Saved Structure:**
```python
{
  "type": "text",
  "properties": {
    "text": {
      "content": "Text content",
      "format": {
        "font_family": "Arial",
        "font_size": 24,
        "font_color": "#000000",
        "bold": False,
        "italic": False,
        "alignment": "left|center|right",
        "vertical_alignment": "top|middle|bottom"
      }
    }
  }
}
```

**HuiduController Expects:**
```python
{
  "properties": {
    "text": "Text content",  # Flat string, not nested dict
    "font_family": "Arial",   # At properties root
    "font_size": 24,          # At properties root
    "color": "#000000"        # At properties root (not font_color)
  }
}
```

**NovaStarController Expects:**
```python
{
  "properties": {
    "text": "Text content",  # Flat string
    "font_family": "Arial",   # At properties root
    "font_size": 24,          # At properties root
    "color": "#000000"        # At properties root
  }
}
```

**Conflicts:**
- ❌ Controllers expect `properties.text` as string, but saved as `properties.text.content`
- ❌ Controllers expect `properties.font_family`, but saved as `properties.text.format.font_family`
- ❌ Controllers expect `properties.color`, but saved as `properties.text.format.font_color`
- ❌ Controllers don't access nested format properties

---

### 2. ANIMATION Element

**Saved Structure:**
```python
{
  "type": "animation",
  "properties": {
    "text": {
      "content": "Animation text",
      "format": {
        "font_family": "Arial",
        "font_size": 24,
        "font_color": "#FFFFFF",
        "alignment": "center",
        "vertical_alignment": "top"
      }
    },
    "animation_style": {
      "style_index": 0,
      "hold_time": 6.0,
      "speed": 5,
      "writing_direction": "Horizontal Line Writing",
      "character_movement": True
    }
  }
}
```

**HuiduController:**
- ❌ **NOT SUPPORTED** - No handler for "animation" type
- Falls back to warning message

**NovaStarController:**
- ❌ **NOT SUPPORTED** - No handler for "animation" type
- Not included in widget conversion

**Conflicts:**
- ❌ Animation elements are completely ignored by both controllers
- ❌ No conversion from nested structure to SDK format

---

### 3. TIMING Element

**Saved Structure:**
```python
{
  "type": "timing",
  "properties": {
    "timing": {
      "mode": "suitable_time|count_down|fixed_time",
      "top_text": "To **",
      "top_text_color": "#cdcd00",
      "multiline": True,
      "top_text_space": 5,
      "suitable_time": {
        "datetime": "2024-01-01T00:00:00",
        "color": "#cdcd00"
      },
      "count_down": {
        "datetime": "2024-01-01T00:00:00",
        "color": "#cdcd00"
      },
      "fixed_time": {
        "day_period": 0,
        "time": "12:00:00"
      },
      "display_style": {
        "color": "#ff9900",
        "year": True,
        "day": True,
        "hour": True,
        "minute": True,
        "second": True,
        "millisecond": False,
        "position_align": "center"
      }
    }
  }
}
```

**HuiduController Expects:**
```python
{
  "properties": {
    "count_type": 0,      # Flat integer, not nested
    "count_value": 0,     # Flat integer
    "font_family": "Arial",
    "font_size": 24,
    "color": "#FFFFFF"
  }
}
```

**NovaStarController:**
- ❌ **NOT SUPPORTED** - No handler for "timing" type

**Conflicts:**
- ❌ Huidu expects flat `count_type` and `count_value`, but saved as nested `timing.mode`, `timing.suitable_time.datetime`, etc.
- ❌ Huidu doesn't access `timing.top_text`, `timing.display_style`, etc.
- ❌ NovaStar completely ignores timing elements

---

### 4. WEATHER Element

**Saved Structure:**
```python
{
  "type": "weather",
  "properties": {
    "weather": {
      "city": "Rome",
      "temp_enabled": True,
      "temp_color": "#FFFFFF",
      "temp_unit": "C",
      "date_enabled": True,
      "date_color": "#FFFFFF",
      # ... other attributes
    }
  }
}
```

**HuiduController:**
- ❌ **NOT SUPPORTED** - No handler

**NovaStarController:**
- ❌ **NOT SUPPORTED** - No handler

**Conflicts:**
- ❌ Weather elements completely ignored by both controllers

---

### 5. SENSOR Element

**Saved Structure:**
```python
{
  "type": "sensor",
  "properties": {
    "sensor": {
      "sensor_type": "temp|Air Humidity|PM2.5|...",
      "fixed_text": "The Temperature",
      "font_family": "Arial",
      "font_color": "#FFFFFF",
      "unit": "°C",
      "value": 25.0
    }
  }
}
```

**HuiduController Expects:**
```python
{
  "properties": {
    "sensor_type": 0,  # Integer index, not string
    "font_family": "Arial",
    "font_size": 24,
    "color": "#FFFFFF"
  }
}
```

**NovaStarController:**
- ❌ **NOT SUPPORTED** - No handler

**Conflicts:**
- ❌ Huidu expects `sensor_type` as integer, but saved as string ("temp", "Air Humidity", etc.)
- ❌ Huidu expects flat `color`, but saved as `sensor.font_color`
- ❌ Huidu doesn't access `fixed_text`, `unit`, `value`
- ❌ NovaStar completely ignores sensor elements

---

### 6. PHOTO Element

**Saved Structure:**
```python
{
  "type": "photo",
  "properties": {
    "photo": {
      "file_path": "/path/to/image.jpg",
      # ... other photo properties
    }
  }
}
```

**HuiduController Expects:**
```python
{
  "properties": {
    "file_path": "/path/to/image.jpg"  # At properties root
  }
}
```

**NovaStarController Expects:**
```python
{
  "properties": {
    "file_path": "/path/to/image.jpg"  # At properties root
  }
}
```

**Conflicts:**
- ❌ Controllers expect `properties.file_path`, but saved as `properties.photo.file_path`
- ⚠️ Controllers access works with `properties.get("file_path")` which will return None

---

### 7. VIDEO Element

**Saved Structure:**
```python
{
  "type": "video",
  "properties": {
    "video": {
      "file_path": "/path/to/video.mp4",
      # ... other video properties
    }
  }
}
```

**NovaStarController Expects:**
```python
{
  "properties": {
    "file_path": "/path/to/video.mp4"  # At properties root
  }
}
```

**HuiduController:**
- ❌ **NOT SUPPORTED** - No handler

**Conflicts:**
- ❌ NovaStar expects `properties.file_path`, but saved as `properties.video.file_path`
- ❌ Huidu completely ignores video elements

---

### 8. CLOCK Element

**Saved Structure:**
```python
{
  "type": "clock",
  "properties": {
    "clock": {
      "show_date": True,
      "font_family": "Arial",
      "font_size": 48,
      "color": "#000000",
      # ... other clock properties
    }
  }
}
```

**HuiduController Expects:**
```python
{
  "properties": {
    "show_date": True,    # At properties root
    "font_family": "Arial",
    "font_size": 48,
    "color": "#000000"
  }
}
```

**NovaStarController:**
- ✅ **SUPPORTED** - Creates CLOCK widget (but doesn't use properties)

**Conflicts:**
- ❌ Huidu expects flat properties, but saved as `properties.clock.show_date`, `properties.clock.font_family`, etc.

---

### 9. HTML Element

**Saved Structure:**
```python
{
  "type": "html",
  "properties": {
    "html": {
      "url": "https://www.google.com/",
      "time_refresh_enabled": False,
      "time_refresh_value": 15.0
    }
  }
}
```

**NovaStarController Expects:**
```python
{
  "properties": {
    "file_path": "url_or_path"  # Uses file_path property
  }
}
```

**HuiduController:**
- ❌ **NOT SUPPORTED** - No handler

**Conflicts:**
- ❌ NovaStar expects `properties.file_path`, but saved as `properties.html.url`
- ❌ Huidu completely ignores HTML elements

---

### 10. HDMI Element

**Saved Structure:**
```python
{
  "type": "hdmi",
  "properties": {
    "hdmi": {
      "display_mode": "Full Screen Zoom|Screen Capture"
    }
  }
}
```

**NovaStarController:**
- ⚠️ **PARTIALLY SUPPORTED** - Creates HDMI widget but doesn't use properties

**HuiduController:**
- ❌ **NOT SUPPORTED** - No handler

**Conflicts:**
- ❌ Controllers don't access `display_mode` property

---

## Summary of Conflicts

### Structure Mismatches

1. **Nested vs Flat Properties:**
   - **Saved**: `properties.text.content`, `properties.text.format.font_family`
   - **Controllers Expect**: `properties.text`, `properties.font_family`

2. **Property Name Mismatches:**
   - **Saved**: `properties.text.format.font_color`
   - **Controllers Expect**: `properties.color`

3. **Missing Element Types:**
   - Animation: Not supported by either controller
   - Weather: Not supported by either controller
   - Singleline Text: Partially supported (treated as text)
   - Timing: Partially supported (Huidu only, with wrong structure)
   - HTML: Partially supported (NovaStar only, wrong property path)
   - HDMI: Partially supported (NovaStar only, properties ignored)

### Missing Property Mappings

1. **Text Elements:**
   - Format properties (bold, italic, underline, alignment) not accessed by controllers
   - Color property path mismatch (`font_color` vs `color`)

2. **Animation Elements:**
   - Not converted at all
   - Text content nested differently than expected
   - Animation style properties not mapped

3. **Timing Elements:**
   - Complex nested structure not mapped to SDK format
   - Top text, multiline, display style ignored

4. **Sensor Elements:**
   - Sensor type mapping (string to integer) missing
   - Fixed text, unit, value properties ignored

5. **Photo/Video Elements:**
   - File path nested under `properties.photo.file_path` vs expected `properties.file_path`

---

## Recommended Solutions

### Option 1: Create Property Adapter Layer
Create a mapping layer that converts saved nested structure to flat structure expected by controllers:

```python
def adapt_element_for_controller(element: Dict, controller_type: str) -> Dict:
    """Convert saved element structure to controller-expected format"""
    adapted = element.copy()
    props = element.get("properties", {})
    element_type = element.get("type")
    
    if element_type == "text":
        text_props = props.get("text", {})
        format_props = text_props.get("format", {})
        adapted["properties"] = {
            "text": text_props.get("content", ""),
            "font_family": format_props.get("font_family", "Arial"),
            "font_size": format_props.get("font_size", 24),
            "color": format_props.get("font_color", "#000000")
        }
    # ... handle other types
    
    return adapted
```

### Option 2: Update Controllers to Access Nested Structure
Modify controllers to access properties from nested structure:

```python
# Instead of:
text = properties.get("text", "")

# Use:
text_props = properties.get("text", {})
text = text_props.get("content", "") if isinstance(text_props, dict) else (text_props if isinstance(text_props, str) else "")
```

### Option 3: Hybrid Approach
- Keep nested structure in saved files (current state)
- Add adapter methods in controllers to extract needed values
- Map unsupported element types to closest supported type or skip them

---

## Critical Missing Implementations

1. **Animation Element Support:**
   - No controller handles animation type
   - Need to map animation_style to SDK format
   - Text content extraction from nested structure

2. **Weather Element Support:**
   - Not handled by any controller
   - Need to decide if converted to text or skipped

3. **Timing Element Full Support:**
   - Huidu has partial support but wrong structure access
   - NovaStar has no support
   - Need proper mapping of timing modes to SDK count types

4. **Sensor Element Mapping:**
   - Sensor type string-to-integer mapping needed
   - Fixed text and unit handling missing

5. **Property Path Standardization:**
   - File path should be consistently accessed
   - Color properties should use consistent naming

---

## Testing Recommendations

1. Create test cases for each element type upload
2. Verify property extraction from nested structure
3. Test with saved files containing all element types
4. Validate controller uploads match saved data

