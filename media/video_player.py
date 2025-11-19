from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)


class VideoPlayer(QWidget):
    # Signals for external use
    videoFinished = pyqtSignal()
    videoError = pyqtSignal(str)

    def __init__(self, parent=None, show_controls: bool = False):
        super(VideoPlayer, self).__init__(parent)

        # Use VideoSurface flag as in the sample code
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  # type: ignore

        self.videoWidget = QVideoWidget()
        # Set attributes to prevent flickering and improve performance
        self.videoWidget.setAttribute(Qt.WA_OpaquePaintEvent, True)  # type: ignore
        self.videoWidget.setAttribute(Qt.WA_NoSystemBackground, True)  # type: ignore
        self.videoWidget.setAutoFillBackground(False)
        self.videoWidget.setUpdatesEnabled(True)

        openButton = QPushButton("Open...")
        openButton.clicked.connect(self.openFile)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))  # type: ignore
        self.playButton.clicked.connect(self._togglePlayPause)

        self.positionSlider = QSlider(Qt.Horizontal)  # type: ignore
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

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
        """Handle media state changes"""
        # Emit finished signal when stopped (if not manually stopped)
        if state == QMediaPlayer.StoppedState:  # type: ignore
            # Check if we reached the end
            if self.mediaPlayer.position() >= self.mediaPlayer.duration() - 100:
                self.videoFinished.emit()
        
        # Update play button icon as in sample code
        if hasattr(self, 'playButton'):
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:  # type: ignore
                self.playButton.setIcon(
                        self.style().standardIcon(QStyle.SP_MediaPause))  # type: ignore
            else:
                self.playButton.setIcon(
                        self.style().standardIcon(QStyle.SP_MediaPlay))  # type: ignore

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

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


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    player = VideoPlayer()
    player.resize(320, 240)
    player.show()

    sys.exit(app.exec_())