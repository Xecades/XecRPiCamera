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
        self.readyToDelete = False

        self.pa = parent

        self.preview = PreviewLabel(parent)
        self.info = InfoLabel(parent)
        self.meta = MetaLabel(parent)

        rdb = self.restoreDeleteButton
        self.exit = RawButton(parent, 0, 5, "Exit", util.hook(rdb, parent.exitGallery))
        self.prev = RawButton(parent, 1, 5, "Previous", util.hook(rdb, self.navigate(-1)))
        self.next = RawButton(parent, 2, 5, "Next", util.hook(rdb, self.navigate(1)))
        self.send = RawButton(parent, 3, 5, "Send", util.hook(rdb, self.sendImg))
        self.delete = RawButton(parent, 4, 5, "Delete", self.deleteImg)

        self.refreshList()
        self.update()

    def sendImg(self):
        pass

    def restoreDeleteButton(self):
        self.readyToDelete = False
        self.delete.setStyle(BUTTON_COLOR)
        self.delete.setText("Delete")

    def deleteImg(self):
        if self.readyToDelete:
            self.restoreDeleteButton()

            img = self.imgs[self.pos]
            
            util.log(f"Deleting image {img} and its DNG file")

            os.remove(img)
            os.remove(img.replace(".jpg", ".dng"))

            self.refreshList()
            self.pos = min(self.pos, len(self.imgs) - 1)
            self.update()

            new_thumb = self.imgs[0] if self.imgs else None
            self.pa.cameraView.button.updateThumbnail(new_thumb)

            return

        self.readyToDelete = True
        self.delete.setStyle(BUTTON_WARN_COLOR)
        self.delete.setText("Confirm")

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
        self.meta.updateMeta(img)

        for btn in [self.prev, self.next, self.send, self.delete]:
            btn.setDisabled(not self.imgs)

    def __apply_all__(self, fn, *args):
        getattr(self.preview, fn)(*args)
        getattr(self.info, fn)(*args)
        getattr(self.meta, fn)(*args)

        for btn in [self.exit, self.prev, self.next, self.send, self.delete]:
            getattr(btn, fn)(*args)

    def show(self): self.__apply_all__("show")
    def hide(self): self.__apply_all__("hide")


class PreviewLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        util.log(f"Rendering gallery preview, width={G_PREVIEW_W}, height={G_PREVIEW_H}")

        self.setScaledContents(True)
        self.setGeometry(0, G_META_H, G_PREVIEW_W, G_PREVIEW_H)
        self.setStyleSheet(f"""
            border: 1px solid {BORDER_COLOR};
            border-bottom: none;
            border-top: none;""")

        self.loadImage()

    def loadImage(self, img=None):
        util.log(f"Loading gallery preview from {img or 'N/A'}")

        self.setPixmap(QPixmap(img) if img else QPixmap())


class MetaLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        W, H = G_PREVIEW_W, G_META_H
        X, Y = 0, 0

        util.log(f"Rendering photo meta, width={W}, height={H}, x={X}, y={Y}")

        style = f"""
            color: {TEXT_COLOR};
            background-color: {INFO_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-bottom: none;
            padding: 2px;
            font-size: 11px;"""
        self.setGeometry(X, Y, W, H)
        self.setStyleSheet(style)

    def updateMeta(self, img=None):
        if not img:
            self.setText("No images found")
            return

        d = time.localtime(os.path.getctime(img))
        date = time.strftime("%Y-%m-%d %H:%M:%S", d)

        self.setText(date)


class InfoLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        W, H = G_PREVIEW_W, G_INFO_H
        X, Y = 0, G_PREVIEW_H + G_META_H

        util.log(f"Rendering gallery info, width={W}, height={H}, x={X}, y={Y}")

        style = f"""
            color: {TEXT_COLOR};
            background-color: {INFO_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-top: none;
            padding: 2px;
            font-size: 11px;"""
        self.setGeometry(X, Y, W, H)
        self.setStyleSheet(style)

    def updateInfo(self, nth, total, img=None):
        if not img:
            self.setText("No images found")
            return

        filename = img.split("/")[-1]
        size = humanize.naturalsize(os.path.getsize(img))

        exif = Image.open(img)._getexif()
        iso = int(exif[34855])
        aperture = round(float(exif[33437]), 1)
        shutter = round(1 / float(exif[33434]))
        width = exif[256]
        height = exif[257]

        model = exif[272]
        make = exif[271]

        content = f"""
            <b>{nth}/{total} {filename}</b> ({size})
            <br>ISO {iso} | f/{aperture} | 1/{shutter}s | {width}x{height}
            <br>Captured by {make} ({model})"""
        self.setText(content)


class RawButton(QPushButton):
    def __init__(self, parent, nth, total, text, action):
        super().__init__(parent)

        W = SCREEN_W - G_PREVIEW_W - MARGIN
        H = int((SCREEN_H + MARGIN) / total - MARGIN)
        X = G_PREVIEW_W + MARGIN
        Y = nth * (H + MARGIN)

        util.log(f"Rendering gallery button {text}, width={W}, height={H}, x={X}, y={Y}")

        self.style = """
            QPushButton {{
                color: {};
                background-color: {};
                border-width: 3px;
                border-style: solid;
                border-top-color: #595959;
                border-right-color: #363636;
                border-bottom-color: #1c1c1c;
                border-left-color: #363636;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {};
            }}"""

        self.setGeometry(X, Y, W, H)
        self.setStyle(BUTTON_COLOR)
        self.setText(text)
        self.clicked.connect(action)

    def setStyle(self, BGColor):
        self.setStyleSheet(self.style.format(TEXT_COLOR, BGColor, BUTTON_ACTIVE_COLOR))
