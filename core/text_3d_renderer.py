"""
3D text rendering using PyOpenGL
"""
from typing import Optional, Dict, Any
# QOpenGLWidget is in QtOpenGLWidgets in PyQt5
try:
    from PyQt5.QtOpenGLWidgets import QOpenGLWidget
except ImportError:
    # Fallback for older PyQt5 versions
    try:
        from PyQt5.QtWidgets import QOpenGLWidget
    except ImportError:
        QOpenGLWidget = None
from PyQt5.QtGui import QFont, QFontMetrics
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    logger.warning("PyOpenGL not available. 3D text rendering will be disabled.")


class Text3DRenderer:
    """3D text renderer using OpenGL"""
    
    def __init__(self):
        self.initialized = False
        if not OPENGL_AVAILABLE:
            logger.warning("OpenGL not available for 3D text rendering")
    
    def initialize(self):
        """Initialize OpenGL state"""
        if not OPENGL_AVAILABLE:
            return False
        
        try:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
            
            # Set up lighting
            light_position = [0.0, 0.0, 5.0, 1.0]
            light_ambient = [0.2, 0.2, 0.2, 1.0]
            light_diffuse = [0.8, 0.8, 0.8, 1.0]
            
            glLightfv(GL_LIGHT0, GL_POSITION, light_position)
            glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
            
            self.initialized = True
            return True
        except Exception as e:
            logger.exception(f"Error initializing 3D renderer: {e}")
            return False
    
    def render_text_3d(self, text: str, x: float, y: float, z: float,
                      properties: Dict[str, Any]) -> bool:
        """
        Render 3D text at specified position.
        Returns True if successful, False otherwise.
        """
        if not OPENGL_AVAILABLE or not self.initialized:
            return False
        
        try:
            # Extract properties
            font_size = properties.get("font_size", 48)
            color = properties.get("color", "#000000")
            depth = properties.get("depth", 10.0)  # 3D extrusion depth
            rotation_x = properties.get("rotation_x", 0.0)
            rotation_y = properties.get("rotation_y", 0.0)
            rotation_z = properties.get("rotation_z", 0.0)
            
            # Parse color
            if isinstance(color, str) and color.startswith("#"):
                r = int(color[1:3], 16) / 255.0
                g = int(color[3:5], 16) / 255.0
                b = int(color[5:7], 16) / 255.0
            else:
                r, g, b = 0.0, 0.0, 0.0
            
            glPushMatrix()
            
            # Translate to position
            glTranslatef(x, y, z)
            
            # Apply rotations
            if rotation_x != 0:
                glRotatef(rotation_x, 1.0, 0.0, 0.0)
            if rotation_y != 0:
                glRotatef(rotation_y, 0.0, 1.0, 0.0)
            if rotation_z != 0:
                glRotatef(rotation_z, 0.0, 0.0, 1.0)
            
            # Set color
            glColor3f(r, g, b)
            
            # Render 3D text (simplified - would need proper text rendering)
            # For now, render as extruded rectangles representing text
            self._render_text_extrusion(text, font_size, depth)
            
            glPopMatrix()
            
            return True
        except Exception as e:
            logger.exception(f"Error rendering 3D text: {e}")
            return False
    
    def _render_text_extrusion(self, text: str, font_size: float, depth: float):
        """Render text as 3D extrusion (simplified implementation)"""
        # This is a simplified implementation
        # A full implementation would use proper font rendering and extrusion
        
        char_width = font_size * 0.6
        char_height = font_size
        
        glBegin(GL_QUADS)
        
        for i, char in enumerate(text):
            char_x = i * char_width
            
            # Front face
            glNormal3f(0.0, 0.0, 1.0)
            glVertex3f(char_x, 0, 0)
            glVertex3f(char_x + char_width, 0, 0)
            glVertex3f(char_x + char_width, char_height, 0)
            glVertex3f(char_x, char_height, 0)
            
            # Back face
            glNormal3f(0.0, 0.0, -1.0)
            glVertex3f(char_x, 0, -depth)
            glVertex3f(char_x, char_height, -depth)
            glVertex3f(char_x + char_width, char_height, -depth)
            glVertex3f(char_x + char_width, 0, -depth)
            
            # Top face
            glNormal3f(0.0, 1.0, 0.0)
            glVertex3f(char_x, char_height, 0)
            glVertex3f(char_x + char_width, char_height, 0)
            glVertex3f(char_x + char_width, char_height, -depth)
            glVertex3f(char_x, char_height, -depth)
            
            # Bottom face
            glNormal3f(0.0, -1.0, 0.0)
            glVertex3f(char_x, 0, 0)
            glVertex3f(char_x, 0, -depth)
            glVertex3f(char_x + char_width, 0, -depth)
            glVertex3f(char_x + char_width, 0, 0)
            
            # Right face
            glNormal3f(1.0, 0.0, 0.0)
            glVertex3f(char_x + char_width, 0, 0)
            glVertex3f(char_x + char_width, 0, -depth)
            glVertex3f(char_x + char_width, char_height, -depth)
            glVertex3f(char_x + char_width, char_height, 0)
            
            # Left face
            glNormal3f(-1.0, 0.0, 0.0)
            glVertex3f(char_x, 0, 0)
            glVertex3f(char_x, char_height, 0)
            glVertex3f(char_x, char_height, -depth)
            glVertex3f(char_x, 0, -depth)
        
        glEnd()
    
    def setup_view(self, width: int, height: int):
        """Setup OpenGL viewport and projection"""
        if not OPENGL_AVAILABLE:
            return
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height if height > 0 else 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def clear(self, r: float = 0.9, g: float = 0.9, b: float = 0.9, a: float = 1.0):
        """Clear the OpenGL buffer"""
        if not OPENGL_AVAILABLE:
            return
        
        glClearColor(r, g, b, a)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

