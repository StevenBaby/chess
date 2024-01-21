
import os
import sys
import pickle
from PySide2.QtGui import QKeyEvent, QMouseEvent
import torch
import torch.nn as nn
import torch.cuda
import torch.nn.functional as F
import torch.utils.data
from PIL import Image
from PIL import ImageGrab
from PIL import ImageQt
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import cv2

from PySide2 import (
    QtWidgets,
    QtGui,
    QtCore,
)

from PySide2.QtGui import (
    QGuiApplication,
)

from PySide2.QtCore import (
    Qt
)

import chess
from chess import Chess as C
import system
from logger import logger
from board import Board

MODELPATH = os.path.join(system.get_dirpath(), 'model.pkl')
QQBOARD = os.path.join(system.get_dirpath(), "images/qqboard.png")

if torch.cuda.is_available():
    device = torch.device("cuda")
    type = torch.cuda.FloatTensor
else:
    device = torch.device("cpu")
    type = torch.FloatTensor
torch.set_default_tensor_type(type)


codes = {key: idx for idx, key in enumerate(C.CHESSES)}
keys = {idx: key for key, idx in codes.items()}
model = None


def make_input(img) -> torch.Tensor:
    img = img.resize((64, 64)).crop((4, 4, 60, 60)).resize((64, 64))
    img = np.asarray(img).copy()
    img[img < 120] = 0

    mask = np.zeros((64, 64))
    mask = cv2.circle(mask, (32, 32), 32, 1, -1)

    for i in range(3):
        img[:, :, i] = img[:, :, i] * mask

    img = img[:, :, 0]
    img = torch.from_numpy(img).float().to(device) / 255.0
    img = img.unsqueeze(0)  # channel only one
    # img = img.permute(2, 0, 1)
    return img


def make_board(image):
    logger.info("make board....")
    image = image.resize((720, 800))
    circled = np.asarray(image)

    gray = circled[:, :, 0]
    # plt.imshow(gray)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, 1,
        minDist=30,
        param1=10,
        param2=30,
        minRadius=25,
        maxRadius=30)

    if circles is None:
        logger.warning("get circles none...")
        return None

    circles = np.uint16(np.around(circles))
    r = round(circles[0][:, 2].mean())

    images = []
    locs = []
    for i in circles[0]:

        x = round(i[0]) - r
        y = round(i[1]) - r

        cv2.circle(circled, (i[0], i[1]), r, (0, 255, 0), 2)

        loc = (i[0] // 80, i[1] // 80)

        img = image.crop((x, y, x + r * 2, y + r * 2))
        img = make_input(img)
        img = img.unsqueeze_(0)
        images.append(img)
        locs.append(loc)
    logger.info("make board finish....")
    return torch.cat(images), locs, circled


class Classifer(nn.Module):

    def forward(self, x):
        return self.model(x)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.model = nn.Sequential(
            nn.Conv2d(1, 64, 4, 2, 1),
            nn.LazyBatchNorm2d(),
            nn.LeakyReLU(0.2),

            nn.Conv2d(64, 32, 4, 2, 1),
            nn.LazyBatchNorm2d(),
            nn.LeakyReLU(0.2),

            nn.Flatten(),

            nn.LazyLinear(64),
            nn.LazyBatchNorm1d(),
            nn.LeakyReLU(0.2),

            nn.LazyLinear(len(codes)),
            nn.Sigmoid(),
        )

    def predict(self, x: torch.Tensor):
        y = self.forward(x)
        return torch.argmax(y, dim=x.dim() - 3)


class Dataset(torch.utils.data.Dataset):

    def __init__(self, image=None, board=None) -> None:
        super().__init__()
        self.labels = []
        self.images = []
        logger.info("load board datasets....")
        qqboard = Image.open(QQBOARD).convert("RGB")

        for offset in range(-20, 20):
            image = qqboard.crop(
                (offset,
                 offset,
                 qqboard.size[0] +
                 offset,
                 qqboard.size[1] +
                 offset))
            images, locs, _ = make_board(image)
            self.images.append(images)
            for loc in locs:
                self.labels.append(codes[C.ORIGIN[loc]])
        self.images = torch.cat(self.images)
        logger.info("load board datasets finished....")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        return self.images[index], self.labels[index]


def train_model(model=None, dataset=None, epoch=20) -> nn.Module:
    dataset = Dataset()

    dataloader = torch.utils.data.DataLoader(
        dataset=dataset,
        batch_size=128,
        shuffle=True,
        generator=torch.Generator(device=device),
    )
    if model is None:
        model = Classifer()

    model.to(device)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.0005,
    )
    criterion = nn.BCELoss()

    bar = tqdm(range(epoch))
    for _ in bar:
        for x, t in dataloader:
            t = F.one_hot(t, len(codes)).float()
            y = model.forward(x)

            loss = criterion(y, t)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            bar.set_postfix(loss=loss.item())

    return model


def save_model(model):
    dirname = os.path.dirname(MODELPATH)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(MODELPATH, 'wb') as file:
        file.write(pickle.dumps(model))


def load_model() -> nn.Module:
    if not os.path.exists(MODELPATH):
        model = train_model(epoch=100)
        save_model(model)
        return model

    with open(MODELPATH, 'rb') as file:
        model = pickle.loads(file.read())
    model.eval()
    return model


def get_model():
    logger.info("get model...")
    global model
    if model is None:
        model = load_model()
    logger.info("get model finish...")
    return model


def get_board(image):
    model = get_model()
    model.eval()

    ret = make_board(image)
    if ret is None:
        return
    images, locs, circled = ret
    pred = model.predict(images)
    board = np.zeros((9, 10), dtype=np.int8)

    for i, k in enumerate(pred):
        board[locs[i]] = keys[int(k)]

    # 验证数量
    wheres = np.argwhere((board == C.K) | (board == C.k))
    if len(wheres) != 2:
        logger.warning("bishop count error %s...", len(wheres))
        return None

    for where in wheres:
        if where[0] < 3 or where[0] > 5:
            logger.warning("king location error %s...", where)
            return None
        if 2 < where[1] < 7:
            logger.warning("king location error %s...", where)
            return None

    counts = {
        C.P: 5,
        C.R: 2,
        C.N: 2,
        C.B: 2,
        C.A: 2,
        C.C: 2,
        C.p: 5,
        C.r: 2,
        C.n: 2,
        C.b: 2,
        C.a: 2,
        C.c: 2,
    }

    for key, count in counts.items():
        wheres = np.argwhere(board == key)
        if len(wheres) > count:
            logger.warning("chess count error %s > %s...", len(wheres), count)
            return None

    wheres = np.argwhere((board == C.B) | (board == C.B))
    for where in wheres:
        if tuple(where) not in {
            (2, 0), (6, 0),
            (0, 2), (4, 2), (8, 2),
            (2, 4), (6, 4),
            (2, 5), (6, 5),
            (0, 7), (4, 7), (8, 7),
            (2, 9), (6, 9),
        }:
            logger.warning("bishop location error %s...", where)
            return None

    wheres = np.argwhere((board == C.A) | (board == C.a))
    for where in wheres:
        if tuple(where) not in {
            (3, 0), (5, 0),
            (4, 1),
            (3, 2), (5, 2),
            (3, 7), (5, 7),
            (4, 8),
            (3, 9), (5, 9),
        }:
            logger.warning("advisor location error %s...", where)
            return None

    return board


def train(image=None, board=None):
    logger.info("train....")
    model = get_model()
    model.train()
    dataset = Dataset(image, board)
    train_model(model, dataset)
    save_model(model)


def show(image):
    if not isinstance(image, Image.Image):
        return
    image = image.resize((720, 800))
    gray = np.asarray(image)[:, :, 0]
    # plt.imshow(gray)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, 1,
        minDist=30,
        param1=30,
        param2=50,
        minRadius=30,
        maxRadius=50)

    img = np.asarray(image)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)

    plt.imshow(img)
    plt.show()


class CapturerSignal(QtCore.QObject):
    capture = QtCore.Signal(Image.Image)


class Capturer(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = None
        self.setWindowTitle(f"截屏")
        self.setWindowIcon(QtGui.QIcon(Board.FAVICON))

        self.signal = CapturerSignal()

        self.capture = None
        self.result = QtWidgets.QLabel()
        self.inited = False

        # self.image = QtGui.QPixmap(QQBOARD)
        # self.setPixmap(self.image)
        # self.setScaledContents(True)
        self.resize(720, 800)
        self.move(
            self.screen().availableGeometry().center() -
            self.rect().center())

        self.setWindowOpacity(0.7)
        # self.setWindowFlag(Qt.WindowType.Tool)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)

        self.gripSize = 16
        self.grips = []
        for i in range(4):
            grip = QtWidgets.QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

    def screenshot(self):
        pscreen = QGuiApplication.screens()[0]
        screen = self.screen()
        rect = self.geometry()
        logger.debug(rect)

        x = rect.x()
        if pscreen != screen:
            x -= pscreen.geometry().width()

        pixmap = self.screen().grabWindow(
            0, x, rect.y(), rect.width(), rect.height())

        # self.result.setPixmap(pixmap)
        # self.result.show()
        # self.result.setScaledContents(True)
        return ImageQt.fromqpixmap(pixmap)

    def keyPressEvent(self, ev: QKeyEvent) -> None:
        if ev.key() == Qt.Key_Escape:
            self.capture = None
            self.close()
        if ev.key() == Qt.Key_Return:
            self.close()
            self.inited = True
            self.signal.capture.emit(self.screenshot())

        return super().keyPressEvent(ev)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        if self.offset is None:
            return
        if ev.type() == QtCore.QEvent.MouseMove and self.offset is not None:
            self.move(self.pos() + ev.pos() - self.offset)

        return super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.offset = None
        # logger.debug("release %s", ev.pos())
        return super().mouseReleaseEvent(ev)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.offset = ev.pos()
        # logger.debug("press %s", ev.pos())
        return super().mousePressEvent(ev)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        rect = self.rect()
        # top left grip doesn't need to be moved...
        # top right
        self.grips[1].move(rect.right() - self.gripSize, 0)
        # bottom right
        self.grips[2].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        # bottom left
        self.grips[3].move(0, rect.bottom() - self.gripSize)


def main():
    app = QtWidgets.QApplication(sys.argv)

    # import qt_material as material
    # extra = {
    #     'font_family': "dengxian SumHei"
    # }
    # material.apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True, extra=extra)

    window = Capturer()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
