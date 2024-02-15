import sys
import subprocess
import util
import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from props import *
from camera import CameraView
from gallery import GalleryView


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.camlock = False

        util.log("Starting Xecades RPi Camera")
        util.ensureFolder(DCIM)

        self.setWindowTitle("Xecades Camera")

        self.cameraView = CameraView(self)

        self.showFullScreen()

    def renderGallery(self):
        util.log("Rendering gallery")

        self.cameraView.preview.pause()
        self.cameraView.hide()

        if not hasattr(self, "galleryView"):
            self.galleryView = GalleryView(self)
        self.galleryView.show()

    def exitGallery(self):
        util.log("Exiting gallery")

        self.cameraView.show()
        self.cameraView.preview.resume()

    def takeSnapshot(self):
        util.log("Taking snapshot")

        self.camlock = True
        self.cameraView.preview.pause()

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file = f"snapshot_{timestamp}.jpg"
        path = f"{DCIM}/{file}"

        cmd = ["raspistill", "--raw", "-vf", "-hf", "-n", "-o", path]
        ret = subprocess.call(cmd)
        if ret == 0:
            util.log(f"Snapshot taken and saved at {path}")
            self.cameraView.button.updateThumbnail(path)
        else:
            util.error(f"Failed to take snapshot")

        if ret == 0:
            util.log(f"Converting {file} to DNG")
            DNG.convert(path)
            util.log(f"DNG file saved at {path.replace('.jpg', '.dng')}")

        self.cameraView.preview.resume()
        self.camlock = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.cameraView.preview.underMouse() and not self.camlock:
                self.takeSnapshot()


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec())
