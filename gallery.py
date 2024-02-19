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

        self.margin = MarginLabel(parent)
        self.preview = PreviewLabel(parent)
        self.info = InfoLabel(parent)
        self.meta = MetaLabel(parent)

        rdb = self.restoreDeleteButton
        self.exit = RawButton(parent, 0, 5, "Exit", util.both(rdb, parent.exitGallery))
        self.prev = RawButton(parent, 1, 5, "Previous", util.both(rdb, self.navigate(-1)))
        self.next = RawButton(parent, 2, 5, "Next", util.both(rdb, self.navigate(1)))
        self.minimize = RawButton(parent, 3, 5, "Minimize", parent.minimize)
        self.delete = RawButton(parent, 4, 5, "Delete", self.deleteImg)

        self.refreshList()
        self.update()

    def restoreDeleteButton(self):
        self.readyToDelete = False
        self.delete.setStyle(BUTTON_COLOR)
        self.delete.setText("Delete")

    def deleteImg(self):
        if self.readyToDelete:
            self.restoreDeleteButton()

            img = self.imgs[self.pos]
            
            util.log(f"Deleting image {img}")

            os.remove(img)

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

        for btn in [self.prev, self.next, self.minimize, self.delete]:
            btn.setDisabled(not self.imgs)

    def __apply_all__(self, fn, *args):
        getattr(self.margin, fn)(*args)
        getattr(self.preview, fn)(*args)
        getattr(self.info, fn)(*args)
        getattr(self.meta, fn)(*args)

        for btn in [self.exit, self.prev, self.next, self.minimize, self.delete]:
            getattr(btn, fn)(*args)

    def show(self): self.__apply_all__("show")
    def hide(self): self.__apply_all__("hide")


class PreviewLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        W, H = G_PREVIEW_W, G_PREVIEW_H
        X, Y = G_MARGIN, G_META_H

        util.log(f"Rendering gallery preview, width={W}, height={H}, x={X}, y={Y}")

        self.setScaledContents(True)
        self.setGeometry(X, Y, W, H)

        self.loadImage()

    def loadImage(self, img=None):
        util.log(f"Loading gallery preview from {img or 'N/A'}")

        self.setPixmap(QPixmap(img) if img else QPixmap())


class MarginLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        W, H = G_MARGIN * 2 + G_PREVIEW_W, SCREEN_H
        X, Y = 0, 0

        util.log(f"Rendering gallery margin, width={W}, height={H}, x={X}, y={Y}")

        self.setGeometry(X, Y, W, H)
        self.setStyleSheet(f"background-color: {INFO_COLOR}; border: 1px solid {BORDER_COLOR};")


class MetaLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        W, H = G_PREVIEW_W, G_META_H
        X, Y = G_MARGIN, 0

        util.log(f"Rendering photo meta, width={W}, height={H}, x={X}, y={Y}")

        style = f"""
            color: {TEXT_COLOR};
            background-color: transparent;
            padding: 2px;
            font-size: 11px;"""
        self.setGeometry(X, Y, W, H)
        self.setStyleSheet(style)

    def updateMeta(self, img=None):
        if not img:
            return

        d = time.localtime(os.path.getmtime(img))
        date = time.strftime("%Y-%m-%d %H:%M:%S", d)

        ip = util.ip()

        text = date
        if ip: text += f" - {ip}"
        if ip and PORT != 80: text += f":{PORT}"

        self.setText(text)


class InfoLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        W, H = G_PREVIEW_W, G_INFO_H
        X, Y = G_MARGIN, G_PREVIEW_H + G_META_H

        util.log(f"Rendering gallery info, width={W}, height={H}, x={X}, y={Y}")

        style = f"""
            color: {TEXT_COLOR};
            background-color: transparent;
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

        pil = Image.open(img)

        exif = pil.getexif()
        iso = f"ISO {exif[34855]} | " if exif.get(34855) else ""
        aperture = f"f/{round(float(exif[33437]), 1)} | " if exif.get(33437) else ""
        shutter = f"1/{round(1 / float(exif[33434]))}s | " if exif.get(33434) else ""

        width = pil.width
        height = pil.height

        make = exif[271] if exif.get(271) else CAM_NAME
        model = f" ({exif[272]})" if exif.get(272) else ""

        content = f"""
            <b>{nth}/{total} {filename}</b> ({size})
            <br>{iso}{aperture}{shutter}{width}x{height}
            <br>Captured by {make}{model}"""
        self.setText(content)


class RawButton(QPushButton):
    def __init__(self, parent, nth, total, text, action):
        super().__init__(parent)

        W = SCREEN_W - G_PREVIEW_W - MARGIN - G_MARGIN * 2
        H = int((SCREEN_H + MARGIN) / total - MARGIN)
        X = G_PREVIEW_W + MARGIN + G_MARGIN * 2
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
