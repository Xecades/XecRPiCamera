import cv2
import util
from props import *
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


class CameraView:
    def __init__(self, parent):
        self.preview = PreviewLabel(parent)
        self.button = GalleryButton(parent, parent.enterGallery)

    def hide(self):
        self.preview.hide()
        self.button.hide()

    def show(self):
        self.preview.show()
        self.button.show()


class PreviewLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        util.log(f"Rendering camera view, width={SCREEN_W}, height={SCREEN_H}")

        self.setGeometry(0, 0, SCREEN_W, SCREEN_H)
        self.setScaledContents(True)

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
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def configureTimer(self):
        util.log("Configuring timer")

        if not hasattr(self, "timer"):
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateImage)
            self.timer.start(UPDATE_DELAY)

        self.stopTimer = False

    def pause(self):
        self.cap.release()
        self.stopTimer = True

    def resume(self):
        self.configureCap()
        self.configureTimer()

    def updateImage(self):
        if self.stopTimer:
            return

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

        W, H = 120, 90
        X = SCREEN_W - W - 10
        Y = SCREEN_H - H - 10

        util.log(f"Rendering gallery switcher button, width={W}, height={H}, x={X}, y={Y}")

        self.setGeometry(X, Y, W, H)
        self.clicked.connect(action)

        imgs = util.fetchLocalImages(DCIM)
        self.updateThumbnail(imgs[0] if imgs else None)

    def updateThumbnail(self, img=None):
        util.log(f"Updating gallery thumbnail to {img or 'N/A'}")

        style = f"border-image: url({img})" if img else "background: #fff"
        self.setStyleSheet(style)
