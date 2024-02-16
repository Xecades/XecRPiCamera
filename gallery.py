import util
import time
import os
import humanize
from PIL import Image
from props import *
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QPixmap


class GalleryView:
    def __init__(self, parent):
        self.pos = 0

        self.preview = PreviewLabel(parent)
        self.info = InfoLabel(parent)

        self.exit = RawButton(parent, 0, 5, "EXIT", parent.exitGallery)
        self.prev = RawButton(parent, 1, 5, "PREV", self.navigate(-1))
        self.next = RawButton(parent, 2, 5, "NEXT", self.navigate(1))
        self.send = RawButton(parent, 3, 5, "SEND", self.send)
        self.delete = RawButton(parent, 4, 5, "DELETE", self.delete)

        self.refreshList()
        self.update()
        self.show()

    def send(self):
        pass

    def delete(self):
        pass

    def navigate(self, direction):
        def wrap():
            self.pos = (self.pos + direction) % len(self.imgs)
            self.update()

        return wrap

    def refreshList(self):
        self.imgs = util.fetchLocalImages(DCIM)

    def update(self):
        img = self.imgs[self.pos] if self.imgs else None
        self.preview.loadImage(img)
        self.info.updateInfo(self.pos + 1, len(self.imgs), img)

    def __apply__(self, fn):
        getattr(self.preview, fn)()
        getattr(self.info, fn)()

        for button in [self.exit, self.prev, self.next, self.send, self.delete]:
            getattr(button, fn)()
    
    def show(self): self.__apply__("show")
    def hide(self): self.__apply__("hide")


class PreviewLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        util.log(f"Rendering gallery preview, width={G_PREVIEW_W}, height={G_PREVIEW_H}")

        self.setScaledContents(True)
        self.setGeometry(MARGIN, MARGIN, G_PREVIEW_W, G_PREVIEW_H)
        self.setStyleSheet(f"border: 1px solid {BORDER_COLOR}")

        self.loadImage()

    def loadImage(self, img=None):
        util.log(f"Loading gallery preview from {img or 'N/A'}")

        self.setPixmap(QPixmap(img) if img else QPixmap())


class InfoLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        W = G_PREVIEW_W
        H = SCREEN_H - G_PREVIEW_H - MARGIN * 3
        X = MARGIN
        Y = G_PREVIEW_H + MARGIN * 2

        util.log(f"Rendering gallery info, width={W}, height={H}, x={X}, y={Y}")

        self.setGeometry(X, Y, W, H)
        self.setStyleSheet(f"color: {TEXT_COLOR}")

    def updateInfo(self, nth, total, img=None):
        if not img:
            self.setText("No images found")
            return

        filename = img.split("/")[-1]
        size = humanize.naturalsize(os.path.getsize(img))

        d = time.localtime(os.path.getctime(img))
        date = time.strftime("%Y-%m-%d %H:%M:%S", d)

        exif = Image.open(img)._getexif()
        iso = int(exif[34855])
        aperture = round(float(exif[33437]), 1)
        shutter = round(1 / float(exif[33434]))
        model = exif[272]

        content = f"""
            <b>{nth}/{total} {filename}</b> ({size})
            <br>{date}
            <br>ISO {iso} | f/{aperture} | 1/{shutter}s
            <br>Captured by {model}"""
        self.setText(content)


class RawButton(QPushButton):
    def __init__(self, parent, nth, total, text, action):
        super().__init__(parent)

        W = SCREEN_W - G_PREVIEW_W - MARGIN * 3
        H = int((SCREEN_H - MARGIN) / total - MARGIN)
        X = G_PREVIEW_W + MARGIN * 2
        Y = nth * (H + MARGIN) + MARGIN

        util.log(f"Rendering gallery button {text}, width={W}, height={H}, x={X}, y={Y}")

        self.setGeometry(X, Y, W, H)
        self.setStyleSheet(f"""
            color: {TEXT_COLOR};
            background-color: {BUTTON_COLOR};
            font-size: 20px;
            font-weight: bold;""")
        self.setText(text)
        self.clicked.connect(action)
