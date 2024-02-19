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
        self.filter = filterLabel(parent)

    def hide(self):
        self.preview.hide()
        self.button.hide()
        self.filter.hide()

    def show(self):
        self.preview.show()
        self.button.show()
        self.filter.show()


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

        self.cap = cv2.VideoCapture(-1)

        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, C_DISPLAY_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, C_DISPLAY_H)
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

        ret, img = self.cap.read()
        img = cv2.flip(img, -1)

        if ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = util.cv2qt(img)

            self.setPixmap(QPixmap.fromImage(img))
        else:
            util.error("Failed to capture frame")


class filterLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        self.method = "vanilla"

        H = C_FILTER_H
        X, Y = MARGIN, SCREEN_H - H - MARGIN

        util.log(f"Rendering filter label, height={H}, x={X}, y={Y}")

        style = f"""
            color: {TEXT_COLOR};
            background-color: rgba(0, 0, 0, 124);
            font-size: 14px;
            padding: 2px;"""
        self.move(X, Y)
        self.setFixedHeight(H)
        self.setStyleSheet(style)

        self.refresh()
    
    def refresh(self):
        self.setText(self.method.capitalize())
        self.adjustSize()

    def switch(self):
        methods = ["vanilla", "greyscale", "sepia", "hdr", "summer", "winter"]
        self.method = methods[(methods.index(self.method) + 1) % len(methods)]
        util.log(f"Switching filter to {self.method}")
        self.refresh()


class GalleryButton(QPushButton):
    def __init__(self, parent, action):
        super().__init__(parent)

        W, H = C_GALLERY_W, C_GALLERY_H
        X = SCREEN_W - W - MARGIN
        Y = SCREEN_H - H - MARGIN

        util.log(f"Rendering gallery switch button, width={W}, height={H}, x={X}, y={Y}")

        self.setGeometry(X, Y, W, H)
        self.clicked.connect(action)

        imgs = util.fetchLocalImages(DCIM)
        self.updateThumbnail(imgs[0] if imgs else None)

    def updateThumbnail(self, img=None):
        util.log(f"Updating gallery thumbnail to {img or 'N/A'}")

        style = f"border-image: url({img})" if img else "background: #000"
        self.setStyleSheet(style)
