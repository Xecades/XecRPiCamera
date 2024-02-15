import cv2
import sys
import subprocess
import util
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from pidng.core import RPICAM2DNG


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setVariables()

        util.log("Starting Xecades Camera")
        util.ensureFolder(self.DCIM)

        self.setWindowTitle("Xecades Camera")

        self.renderCameraView()
        self.renderGalleryButton()

        self.showFullScreen()

    def setVariables(self):
        self.W = 480
        self.H = 320
        self.UPDATE_DELAY = 70
        self.DISPLAY_W = 160
        self.DISPLAY_H = 120
        self.DCIM = "~/DCIM"
        self.DNG = RPICAM2DNG()

        self.camlock = False

    def renderCameraView(self):
        util.log("Rendering camera view")
        util.log(f"Display width={self.W}, height={self.H}")

        self.cameraLabel = QLabel(self)
        self.cameraLabel.setScaledContents(True)
        self.cameraLabel.setGeometry(0, 0, self.W, self.H)

        self.cap = cv2.VideoCapture(0)
        self.configureCap()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateImage)
        self.timer.start(self.UPDATE_DELAY)

    def configureCap(self):
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.DISPLAY_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.DISPLAY_H)

    def updateImage(self):
        ret, frame = self.cap.read()
        if ret:
            rgbf = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbf.shape
            img = QImage(rgbf.data, w, h, ch * w, QImage.Format_RGB888)

            self.cameraLabel.setPixmap(QPixmap.fromImage(img))

    def renderGalleryButton(self):
        w, h = 120, 90
        x = int(self.W - w - 10)
        y = int(self.H - h - 10)

        util.log("Rendering gallery button")
        util.log(f"Gallery button width={w}, height={h}, x={x}, y={y}")

        self.button = QPushButton("", self)
        self.button.setGeometry(x, y, w, h)
        self.button.clicked.connect(self.renderGallery)

        loc = util.fetchLocalImages()
        self.updateGalleryImage(loc[-1] if loc else None)

    def updateGalleryImage(self, img=None):
        util.log(f"Updating gallery image to {img or 'EMPTY'}")

        style = f"border-image: url({img})" if img else "background: #fff"
        self.button.setStyleSheet(style)

    def renderGallery(self):
        util.log("Rendering gallery")

        self.timer.stop()

        self.g_bg = QLabel(self)
        self.g_bg.setGeometry(0, 0, self.W, self.H)

        # todo: bluetooth

        # self.g_exit = QPushButton("EXIT", self)
        # self.g_exit.setGeometry(10, 10, 100, 30)

        self.timer.start(self.UPDATE_DELAY)

    def takeSnapshot(self):
        util.log("Taking snapshot")

        self.camlock = True
        self.timer.stop()
        self.cap.release()

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file = f"snapshot_{timestamp}.jpg"
        path = f"{self.DCIM}/{file}"

        ret = subprocess.call(["raspistill", "--raw", "-n", "-o", path])
        if ret == 0:
            util.log(f"Snapshot taken and saved at {path}")
            self.updateGalleryImage(path)
        else:
            util.error(f"Failed to take snapshot")

        self.cap = cv2.VideoCapture(0)
        self.configureCap()
        self.timer.start(self.UPDATE_DELAY)
        self.camlock = False

        if ret == 0:
            util.log(f"Converting {file} to DNG")
            self.DNG.convert(path)
            util.log(f"DNG file saved at {path.replace('.jpg', '.dng')}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.cameraLabel.underMouse() and not self.camlock:
            self.takeSnapshot()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
