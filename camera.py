import cv2
import util
from props import *
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


class CameraView:
    def __init__(self, parent):
        self.preview = PreviewLabel(parent)
        self.button = GalleryButton(parent, parent.renderGallery)

    def hide(self):
        self.preview.hide()
        self.button.hide()

    def show(self):
        self.preview.show()
        self.button.show()


class PreviewLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        util.log("Rendering camera view")
        util.log(f"Display width={SCREEN_W}, height={SCREEN_H}")

        self.setScaledContents(True)
        self.setGeometry(0, 0, SCREEN_W, SCREEN_H)

        self.configureCap()
        self.configureTimer()

    def configureCap(self):
        util.log("Configuring capturer")

        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()

        self.cap = cv2.VideoCapture(0)

        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_H)

    def configureTimer(self):
        util.log("Configuring timer")

        if not hasattr(self, "timer"):
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateImage)
        self.timer.start(UPDATE_DELAY)

    def pause(self):
        self.cap.release()
        self.timer.stop()

    def resume(self):
        self.configureCap()
        self.configureTimer()

    def updateImage(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, -1)

        if ret:
            rgbf = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbf.shape
            img = QImage(rgbf.data, w, h, ch * w, QImage.Format_RGB888)

            self.setPixmap(QPixmap.fromImage(img))
        else:
            util.error("Failed to capture frame")


class GalleryButton(QPushButton):
    def __init__(self, parent, action):
        super().__init__(parent)

        w, h = 120, 90
        x = int(SCREEN_W - w - 10)
        y = int(SCREEN_H - h - 10)

        util.log("Rendering gallery switcher button")
        util.log(f"Gallery button width={w}, height={h}, x={x}, y={y}")

        self.setGeometry(x, y, w, h)
        self.clicked.connect(action)

        imgs = util.fetchLocalImages(DCIM)
        self.updateThumbnail(imgs[0] if imgs else None)

    def updateThumbnail(self, img=None):
        util.log(f"Updating gallery thumbnail to {img or 'N/A'}")

        style = f"border-image: url({img})" if img else "background: #fff"
        self.setStyleSheet(style)
