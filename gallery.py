import util
from props import *
from PyQt5.QtWidgets import QLabel, QPushButton


class GalleryView:
    def __init__(self, parent):
        self.pos = 0

        self.preview = PreviewLabel(parent)
        self.exit = RawButton(parent, 10, 260, "EXIT", parent.exitGallery)

        self.refreshList()
        self.update()

    def refreshList(self):
        self.imgs = util.fetchLocalImages(DCIM)

    def update(self):
        self.preview.loadImage(self.imgs[self.pos] if self.imgs else None)

    def show(self):
        pass


class PreviewLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        self.WIDTH = 360
        self.HEIGHT = 240

        util.log("Rendering gallery preview")
        util.log(f"Display width={self.WIDTH}, height={self.HEIGHT}")

        self.setScaledContents(True)
        self.setGeometry(10, 10, self.WIDTH, self.HEIGHT)

        self.loadImage()

    def loadImage(self, img=None):
        util.log(f"Loading gallery preview from {img or 'N/A'}")

        style = f"border-image: url({img})" if img else "border: 1px solid black"
        self.setStyleSheet(style)


class RawButton(QPushButton):
    def __init__(self, parent, nth, total, text, action):
        super().__init__(parent)

        self.setGeometry(10, 260, 100, 30)
        self.setStyleSheet("background: green; border: 2px solid black;")
        self.clicked.connect(action)
        self.setText(text)
