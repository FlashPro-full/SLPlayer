"""
Colorful emoji rendering engine
Supports rendering emojis in their real colors using system emoji fonts or image conversion
"""
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional
from PyQt6.QtGui import QFont, QFontDatabase, QFontMetrics, QPainter, QPixmap, QImage, QColor
from PyQt6.QtCore import Qt, QSize

try:
    import emoji
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False


class EmojiRenderer:
    """Renders emojis in their real colors"""
    
    # System emoji fonts (platform-specific)
    EMOJI_FONTS = {
        'win32': ['Segoe UI Emoji', 'Segoe UI Symbol', 'Segoe UI'],
        'darwin': ['Apple Color Emoji'],
        'linux': ['Noto Color Emoji', 'EmojiOne Color', 'Twitter Color Emoji']
    }
    
    def __init__(self):
        self.emoji_font = self._find_emoji_font()
        self.emoji_cache = {}  # Cache rendered emoji images
        self.cache_dir = Path.home() / ".slplayer" / "emoji_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _find_emoji_font(self) -> Optional[QFont]:
        """Find and return the best available emoji font"""
        platform = sys.platform
        font_families = self.EMOJI_FONTS.get(platform, [])
        
        # Add generic fallbacks
        font_families.extend(['Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji'])
        
        # QFontDatabase is used as a static class in PyQt6
        available_families = QFontDatabase.families()
        
        for font_family in font_families:
            if font_family in available_families:
                font = QFont(font_family)
                font.setPixelSize(64)  # Default size for emoji rendering
                return font
        
        # Fallback to default font
        return QFont()
    
    def is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji"""
        if not char:
            return False
        
        # Unicode ranges for emojis
        code_point = ord(char[0])
        
        # Emoji ranges (simplified - covers most common emojis)
        emoji_ranges = [
            (0x1F300, 0x1F9FF),  # Miscellaneous Symbols and Pictographs
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
            (0xFE00, 0xFE0F),    # Variation Selectors
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1FA00, 0x1FAFF),  # Chess Symbols, Symbols and Pictographs Extended-A
        ]
        
        for start, end in emoji_ranges:
            if start <= code_point <= end:
                return True
        
        # Check for emoji sequences (skin tones, flags, etc.)
        if len(char) > 1:
            # Check for variation selectors or combining characters
            if any(0xFE00 <= ord(c) <= 0xFE0F for c in char):
                return True
            if any(0x1F3FB <= ord(c) <= 0x1F3FF for c in char):  # Skin tone modifiers
                return True
        
        return False
    
    def extract_emojis(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Extract emojis from text with their positions
        Returns list of (start_pos, end_pos, emoji_text) tuples
        """
        emojis = []
        i = 0
        while i < len(text):
            char = text[i]
            
            # Check for emoji sequences (multiple code points)
            emoji_text = char
            j = i + 1
            
            # Check for variation selectors, skin tones, etc.
            while j < len(text):
                next_char = text[j]
                # Variation selectors
                if 0xFE00 <= ord(next_char) <= 0xFE0F:
                    emoji_text += next_char
                    j += 1
                # Skin tone modifiers
                elif 0x1F3FB <= ord(next_char) <= 0x1F3FF:
                    emoji_text += next_char
                    j += 1
                # Zero-width joiner (for multi-character emojis like flags)
                elif ord(next_char) == 0x200D:
                    emoji_text += next_char
                    j += 1
                    # Continue to get the rest of the emoji
                    if j < len(text):
                        emoji_text += text[j]
                        j += 1
                else:
                    break
            
            if self.is_emoji(emoji_text):
                emojis.append((i, j, emoji_text))
                i = j
            else:
                i += 1
        
        return emojis
    
    def render_emoji_to_image(self, emoji_char: str, size: int = 64, 
                               use_font: bool = True) -> Optional[QPixmap]:
        """
        Render an emoji to an image with its real colors
        Returns QPixmap of the rendered emoji
        """
        cache_key = f"{emoji_char}_{size}"
        
        # Check cache
        if cache_key in self.emoji_cache:
            return self.emoji_cache[cache_key]
        
        # Try to load from disk cache
        cache_file = self.cache_dir / f"{hash(emoji_char)}_{size}.png"
        if cache_file.exists():
            pixmap = QPixmap(str(cache_file))
            if not pixmap.isNull():
                self.emoji_cache[cache_key] = pixmap
                return pixmap
        
        # Render emoji
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        if use_font and self.emoji_font:
            # Use emoji font for colorful rendering
            font = QFont(self.emoji_font)
            font.setPixelSize(int(size * 0.8))  # Slightly smaller for padding
            painter.setFont(font)
            
            # Set text color to ensure proper rendering
            painter.setPen(QColor(0, 0, 0, 0))  # Transparent pen
            
            # Draw emoji
            rect = pixmap.rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, emoji_char)
        else:
            # Fallback: render as text (monochrome)
            font = QFont()
            font.setPixelSize(int(size * 0.8))
            painter.setFont(font)
            painter.setPen(QColor(0, 0, 0))
            rect = pixmap.rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, emoji_char)
        
        painter.end()
        
        # Cache the result
        self.emoji_cache[cache_key] = pixmap
        
        # Save to disk cache
        try:
            pixmap.save(str(cache_file), "PNG")
        except Exception:
            pass  # Ignore cache save errors
        
        return pixmap
    
    def render_text_with_emojis(self, text: str, font: QFont, 
                                text_color: QColor = QColor(0, 0, 0),
                                emoji_size: Optional[int] = None) -> QPixmap:
        """
        Render text with emojis, replacing emojis with colorful images
        Returns a QPixmap with the rendered text and emojis
        """
        if emoji_size is None:
            # Calculate emoji size based on font size
            emoji_size = max(32, font.pixelSize() if font.pixelSize() > 0 else font.pointSize())
        
        # Extract emojis and their positions
        emojis = self.extract_emojis(text)
        
        if not emojis:
            # No emojis, render as normal text
            metrics = QFontMetrics(font)
            text_rect = metrics.boundingRect(text)
            pixmap = QPixmap(text_rect.width() + 20, text_rect.height() + 20)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setFont(font)
            painter.setPen(text_color)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            painter.end()
            return pixmap
        
        # Render text with emoji images
        metrics = QFontMetrics(font)
        lines = text.split('\n')
        line_height = metrics.height()
        total_height = line_height * len(lines)
        max_width = max(metrics.boundingRect(line).width() for line in lines) if lines else 100
        
        # Create pixmap
        pixmap = QPixmap(max_width + 100, total_height + 40)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        y_pos = 20
        for line in lines:
            x_pos = 10
            i = 0
            
            while i < len(line):
                # Check if current position is an emoji
                emoji_found = False
                for start, end, emoji_text in emojis:
                    if start <= i < end and line[start:end] == emoji_text:
                        # Render emoji image
                        emoji_pixmap = self.render_emoji_to_image(emoji_text, emoji_size)
                        if emoji_pixmap and not emoji_pixmap.isNull():
                            # Scale emoji to match text height
                            scaled_size = min(emoji_size, line_height)
                            scaled_emoji = emoji_pixmap.scaled(
                                scaled_size, scaled_size,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            painter.drawPixmap(x_pos, y_pos + (line_height - scaled_size) // 2, scaled_emoji)
                            x_pos += scaled_size
                        else:
                            # Fallback: draw as text
                            painter.drawText(x_pos, y_pos + line_height, emoji_text)
                            x_pos += metrics.horizontalAdvance(emoji_text)
                        i = end
                        emoji_found = True
                        break
                
                if not emoji_found:
                    # Draw regular character
                    char = line[i]
                    painter.drawText(x_pos, y_pos + line_height, char)
                    x_pos += metrics.horizontalAdvance(char)
                    i += 1
            
            y_pos += line_height
        
        painter.end()
        return pixmap


# Global emoji renderer instance
_emoji_renderer = None

def get_emoji_renderer() -> EmojiRenderer:
    """Get the global emoji renderer instance"""
    global _emoji_renderer
    if _emoji_renderer is None:
        _emoji_renderer = EmojiRenderer()
    return _emoji_renderer

