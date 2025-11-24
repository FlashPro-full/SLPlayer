from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtGui import QPalette


class VideoPlayer(QWidget):
    # Signals for external use
    videoFinished = pyqtSignal()
    videoError = pyqtSignal(str)

    def __init__(self, parent=None, show_controls: bool = False):
        super(VideoPlayer, self).__init__(parent)

        # Use VideoSurface flag as in the sample code
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  # type: ignore

        self.videoWidget = QVideoWidget()
        self.videoWidget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.black)
        self.videoWidget.setPalette(palette)
        
        self.videoWidget.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.videoWidget.setAutoFillBackground(False)

        openButton = QPushButton("Open...")
        openButton.clicked.connect(self.openFile)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))  # type: ignore
        self.playButton.clicked.connect(self._togglePlayPause)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderPressed.connect(self._on_slider_pressed)
        self.positionSlider.sliderReleased.connect(self._on_slider_released)
        self.positionSlider.sliderMoved.connect(self._on_slider_moved)
        self._slider_pressed = False

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.videoWidget, stretch=1)
        
        if show_controls:
            layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.mediaStatusChanged.connect(self.mediaStatusChanged)
        self.mediaPlayer.bufferStatusChanged.connect(self.bufferStatusChanged)
        self.mediaPlayer.videoAvailableChanged.connect(self.videoAvailableChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

    def _togglePlayPause(self):
        """Toggle play/pause (called by playButton click) - matches sample code behavior"""
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:  # type: ignore
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def play(self):
        """Play the media (for programmatic control)"""
        self.mediaPlayer.play()

    def pause(self):
        """Pause the media"""
        self.mediaPlayer.pause()

    def stop(self):
        """Stop the media"""
        self.mediaPlayer.stop()

    def setMedia(self, file_path: str):
        """Set media file to play"""
        if file_path:
            media_url = QUrl.fromLocalFile(file_path)
            media_content = QMediaContent(media_url)
            self.mediaPlayer.setMedia(media_content)
            if hasattr(self, 'playButton'):
                self.playButton.setEnabled(True)

    def setVolume(self, volume: int):
        """Set volume (0-100)"""
        self.mediaPlayer.setVolume(volume)

    def getVideoWidget(self) -> QVideoWidget:
        """Get the video widget for external positioning"""
        return self.videoWidget

    def getState(self) -> QMediaPlayer.State:
        """Get current media player state"""
        return self.mediaPlayer.state()

    def getError(self) -> int:
        """Get current media player error"""
        return self.mediaPlayer.error()  # type: ignore

    def getErrorString(self) -> str:
        """Get error string from media player"""
        return self.mediaPlayer.errorString()

    def isPlaying(self) -> bool:
        """Check if video is currently playing"""
        return self.mediaPlayer.state() == QMediaPlayer.PlayingState  # type: ignore

    def mediaStateChanged(self, state):
        if state == QMediaPlayer.StoppedState:
            if self.mediaPlayer.position() >= self.mediaPlayer.duration() - 100:
                self.videoFinished.emit()
        
        if hasattr(self, 'playButton'):
            if state == QMediaPlayer.PlayingState:
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
                self.playButton.setEnabled(True)
            elif state == QMediaPlayer.PausedState:
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
                self.playButton.setEnabled(True)
            else:
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
                self.playButton.setEnabled(True)
    
    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.InvalidMedia:
            self.handleError()
        elif status == QMediaPlayer.EndOfMedia:
            self.videoFinished.emit()
    
    def bufferStatusChanged(self, progress):
        pass
    
    def videoAvailableChanged(self, available):
        if not available and hasattr(self, 'playButton'):
            self.playButton.setEnabled(False)

    def positionChanged(self, position):
        if not self._slider_pressed:
            self.positionSlider.setValue(position // 1000)

    def durationChanged(self, duration):
        if duration > 0:
            self.positionSlider.setRange(0, duration // 1000)

    def _on_slider_pressed(self):
        self._slider_pressed = True

    def _on_slider_released(self):
        self._slider_pressed = False

    def _on_slider_moved(self, position):
        self.mediaPlayer.setPosition(position * 1000)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        """Handle media errors"""
        error_string = self.mediaPlayer.errorString()
        if hasattr(self, 'playButton'):
            self.playButton.setEnabled(False)
        if hasattr(self, 'errorLabel'):
            self.errorLabel.setText("Error: " + error_string)
        self.videoError.emit(error_string)
    
    @staticmethod
    def get_video_thumbnail(video_path: str, frame_time: float = 1.0):
        try:
            import cv2
            import numpy as np
            from PyQt5.QtGui import QPixmap, QImage
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30.0
            
            frame_number = int(frame_time * fps)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = np.ascontiguousarray(frame_rgb)
                height, width = frame_rgb.shape[:2]
                bytes_per_line = 3 * width
                q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                q_image = q_image.copy()
                pixmap = QPixmap.fromImage(q_image)
                if pixmap and not pixmap.isNull():
                    return pixmap
        except ImportError:
            pass
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Failed to extract thumbnail from {video_path}: {e}")
        
        return None


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    player = VideoPlayer()
    player.resize(320, 240)
    player.show()

    sys.exit(app.exec_())