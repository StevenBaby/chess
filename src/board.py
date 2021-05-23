
import os
import ctypes

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QPixmap

import numpy as np
from numpy import mat
from numpy import zeros

from chess import Chess
from logger import logger

from attrdict import attrdict
from version import VERSION
import system

dirpath = system.get_dirpath()


class Signal(QtCore.QObject):

    refresh = QtCore.Signal(None)


class Board(QLabel):

    BOARD = str(dirpath / u"images/board.png")
    MARK = str(dirpath / u"images/mark.png")
    CHECK = str(dirpath / u"images/check.png")
    FAVICON = str(dirpath / u"images/black_bishop.png")

    IMAGES = {
        Chess.R: str(dirpath / 'images/red_rook.png'),
        Chess.N: str(dirpath / 'images/red_knight.png'),
        Chess.B: str(dirpath / 'images/red_bishop.png'),
        Chess.A: str(dirpath / 'images/red_advisor.png'),
        Chess.K: str(dirpath / 'images/red_king.png'),
        Chess.C: str(dirpath / 'images/red_cannon.png'),
        Chess.P: str(dirpath / 'images/red_pawn.png'),
        Chess.r: str(dirpath / 'images/black_rook.png'),
        Chess.n: str(dirpath / 'images/black_knight.png'),
        Chess.b: str(dirpath / 'images/black_bishop.png'),
        Chess.a: str(dirpath / 'images/black_advisor.png'),
        Chess.k: str(dirpath / 'images/black_king.png'),
        Chess.c: str(dirpath / 'images/black_cannon.png'),
        Chess.p: str(dirpath / 'images/black_pawn.png'),
    }

    ANIMATION_DURATION = 280

    flags = QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint

    def __init__(self, parent=None, callback=None):
        super().__init__(parent=parent)

        self.csize = 60
        self.board_image = QtGui.QPixmap(self.BOARD)

        if parent is None:
            self.setWindowIcon(QtGui.QIcon(self.FAVICON))
            self.setWindowTitle(u"Chinese Chess")
            # self.setWindowFlags(self.flags)

        # https://www.mfitzp.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/

        app = QtWidgets.QApplication.instance()
        if app:
            app.setWindowIcon(QtGui.QIcon(self.FAVICON))

        if os.name == 'nt':
            logger.info("set model id")
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                f'StevenBaby.Chess.{VERSION}'
            )

        self.setObjectName(u"Board")
        self.setScaledContents(True)

        self.resize(self.csize * Chess.W, self.csize * Chess.H)

        for chess, path in self.IMAGES.items():
            self.IMAGES[chess] = QPixmap(path)

        mark = QPixmap(self.MARK)
        self.mark1 = QLabel(self)
        self.mark1.setPixmap(mark)
        self.mark1.setScaledContents(True)
        self.mark1.setVisible(False)

        self.mark2 = QLabel(self)
        self.mark2.setPixmap(mark)
        self.mark2.setScaledContents(True)
        self.mark2.setVisible(False)

        check = QPixmap(self.CHECK)
        self.mark3 = QLabel(self)
        self.mark3.setPixmap(check)
        self.mark3.setScaledContents(True)
        self.mark3.setVisible(False)

        self.signal = Signal()
        self.signal.refresh.connect(self.refresh)

        self.labels = mat(zeros((Chess.W, Chess.H,)), dtype=QtWidgets.QLabel)
        self.board = mat(zeros((Chess.W, Chess.H,)), dtype=int)

        self.fpos = None
        self.tpos = None
        self.check = None

        self.update()

        self.callback = callback

    def setBoard(self, board, fpos=None, tpos=None):
        self.board = board
        self.fpos = fpos
        self.tpos = tpos
        self.signal.refresh.emit()

    def setCheck(self, check):
        self.check = check
        self.signal.refresh.emit()

    def move(self, board, fpos, tpos, callback=None):
        label = self.getLabel(fpos)
        if not label:
            return

        label.setVisible(True)
        label.raise_()  # 将控件提到前面
        ani = QtCore.QPropertyAnimation(label, b'geometry', self)
        ani.setTargetObject(label)
        ani.setDuration(self.ANIMATION_DURATION)
        ani.setStartValue(QtCore.QRect(self.getChessGeometry(fpos)))
        ani.setEndValue(QtCore.QRect(self.getChessGeometry(tpos)))
        ani.start()

        if callable(callback):
            QtCore.QTimer.singleShot(self.ANIMATION_DURATION, callback)

    @QtCore.Slot()
    def refresh(self):
        self.setPixmap(self.board_image)
        for x in range(Chess.W):
            for y in range(Chess.H):
                pos = (x, y)
                self.setChess(pos, self.board[pos])

        if self.fpos:
            self.mark1.setGeometry(self.getChessGeometry(self.fpos))
            self.mark1.setVisible(True)
        else:
            self.mark1.setVisible(False)

        if self.tpos:
            self.mark2.setGeometry(self.getChessGeometry(self.tpos))
            self.mark2.setVisible(True)
        else:
            self.mark2.setVisible(False)

        if self.check:
            self.mark3.setGeometry(self.getChessGeometry(self.check))
            self.mark3.setVisible(True)
        else:
            self.mark3.setVisible(False)

        super().update()

    def resizeEvent(self, event):
        w = self.parentWidget().width()
        h = self.parentWidget().height()

        height = h
        width = h / Chess.H * Chess.W

        if width > w:
            width = w
            height = width / Chess.W * Chess.H

        width = int(width)
        height = int(height)

        x = (w - width) // 2
        y = (h - height) // 2
        self.setGeometry(x, y, width, height)

        self.csize = width // Chess.W

        self.refresh()

    def mousePressEvent(self, event):
        if event.buttons() != QtCore.Qt.LeftButton:
            return super().mousePressEvent(event)

        pos = self.getPosition(event)
        if not pos:
            return
        # logger.debug("click %s", pos)
        self.clickPosition(pos)

    def clickPosition(self, pos):
        if callable(self.callback):
            self.callback(pos)

    def getLabel(self, pos):
        if not pos:
            return None
        label = self.labels[tuple(pos)]
        if not label:
            return None
        return label

    def setChess(self, pos, chess):
        label = self.labels[pos]
        if not label:
            label = QLabel(self)
            label.pos = pos
            self.labels[pos] = label

        if not chess:
            label.setVisible(False)
            return

        image = self.IMAGES[chess]
        label.setPixmap(image)
        label.setScaledContents(True)
        label.setGeometry(self.getChessGeometry(pos))
        label.setVisible(True)

    def getChessGeometry(self, pos):
        return QtCore.QRect(
            pos[0] * self.csize,
            pos[1] * self.csize,
            self.csize,
            self.csize
        )

    def getPosition(self, event):
        x = event.x() // self.csize
        y = event.y() // self.csize

        if x < 0 or x >= Chess.W:
            return None
        if y < 0 or y >= Chess.H:
            return None

        return (int(x), int(y))


class BoardFrame(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board = Board(self)
        # self.setWindowOpacity(0.85)
        if parent is None:
            self.setWindowIcon(QtGui.QIcon(self.board.FAVICON))
            self.setWindowTitle(u"中国象棋")
        self.resize(self.board.size())

    def resizeEvent(self, event):
        self.board.resizeEvent(event)
        return super().resizeEvent(event)


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = BoardFrame()
    ui.show()
    app.exec_()


if __name__ == '__main__':
    main()
