#!/usr/bin/env python3

import sys
import util
from PyQt5.QtWidgets import QApplication, QMainWindow
from props import *
from camera import CameraView
from gallery import GalleryView
from snapshot import Snapshot


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        util.log(f"Starting {CAM_NAME}")
        util.ensureFolder(DCIM)

        self.setWindowTitle(CAM_NAME)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.cameraView = CameraView(self)
        self.showFullScreen()

        self.snapshot = Snapshot(self)
        self.galleryView = GalleryView(self)

    def enterGallery(self):
        util.log("Entering gallery")

        self.snapshot.lock = True

        self.cameraView.preview.pause()
        self.cameraView.hide()

        self.galleryView.pos = 0
        self.galleryView.update()
        self.galleryView.show()

    def exitGallery(self):
        util.log("Exiting gallery")

        self.snapshot.lock = False

        self.galleryView.hide()
        self.cameraView.preview.resume()
        self.cameraView.show()

    def minimize(self):
        util.log("Minimizing window")

        self.showMinimized()

    def mousePressEvent(self, event):
        if self.cameraView.preview.underMouse():
            self.cameraView.filter.switch()
        if not self.galleryView.delete.underMouse():
            self.galleryView.restoreDeleteButton()


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec())
