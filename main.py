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

        util.log(f"Starting {CAM_NAME}")
        util.ensureFolder(DCIM)

        self.setWindowTitle(CAM_NAME)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.cameraView = CameraView(self)
        self.showFullScreen()

        self.galleryView = GalleryView(self)

    def enterGallery(self):
        util.log("Entering gallery")

        self.cameraView.preview.pause()
        self.cameraView.hide()

        self.galleryView.pos = 0
        self.galleryView.update()
        self.galleryView.show()

    def exitGallery(self):
        util.log("Exiting gallery")

        self.galleryView.hide()
        self.cameraView.preview.resume()
        self.cameraView.show()

    def takeSnapshot(self):
        if self.camlock:
            return

        util.log("Taking snapshot")

        self.camlock = True
        self.cameraView.preview.pause()

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file = f"snapshot_{timestamp}.jpg"
        path = f"{DCIM}/{file}"

        cmd = ["raspistill", "--raw", "-vf", "-hf",
               "-n", "-x", f"IFD0.Make={CAM_NAME}", "-o", path]
        ret = subprocess.call(cmd)
        if ret == 0:
            util.log(f"Snapshot taken and saved at {path}")
            self.cameraView.button.updateThumbnail(path)
            self.galleryView.refreshList()
            self.galleryView.update()
        else:
            util.error(f"Failed to take snapshot")

        if ret == 0:
            util.log(f"Converting {file} to DNG")
            DNG.convert(path)
            util.log(f"DNG file saved at {path.replace('.jpg', '.dng')}")

        self.cameraView.preview.resume()
        self.camlock = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.cameraView.preview.underMouse():
            self.takeSnapshot()
        if event.button() == Qt.LeftButton and not self.galleryView.delete.underMouse():
            self.galleryView.restoreDeleteButton()


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec())
