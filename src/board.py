# coding=utf-8
'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-05-31

PySide2 棋盘基础控件，只用于棋盘的展示，和点击回调。
'''


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


class BoardSignal(QtCore.QObject):

    refresh = QtCore.Signal(None)


class Board(QLabel):

    '''
    棋盘坐标与屏幕坐标类似，左上角为 (0, 0)，右下角为 (8, 9)
    '''

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

    signal_class = BoardSignal

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

        self.animate = QtCore.QPropertyAnimation(self, b'geometry', self)

        self.resize(self.csize * Chess.W, self.csize * Chess.H)

        for chess, path in self.IMAGES.items():
            self.IMAGES[chess] = QPixmap(path)

        mark = QPixmap(self.MARK)

        # 棋盘起始标记
        self.mark1 = QLabel(self)
        self.mark1.setPixmap(mark)
        self.mark1.setScaledContents(True)
        self.mark1.setVisible(False)

        # 棋盘落子标记
        self.mark2 = QLabel(self)
        self.mark2.setPixmap(mark)
        self.mark2.setScaledContents(True)
        self.mark2.setVisible(False)

        check = QPixmap(self.CHECK)
        # 将军棋子标记
        self.mark3 = QLabel(self)
        self.mark3.setPixmap(check)
        self.mark3.setScaledContents(True)
        self.mark3.setVisible(False)

        self.signal = self.signal_class()
        self.signal.refresh.connect(self.refresh)

        self.labels = mat(zeros((Chess.W, Chess.H,)), dtype=QtWidgets.QLabel)
        self.board = mat(zeros((Chess.W, Chess.H,)), dtype=int)

        self.fpos = None
        self.tpos = None
        self.check = None
        self.reverse = False

        font = QtGui.QFont()
        font.setFamily(u"DengXian")
        font.setPointSize(self.csize / 4)
        self.label = QtWidgets.QLabel(parent)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setText("")
        self.label.lower()  # 控件放在最下层

        self.update()

        self.callback = callback

    def setBoard(self, board, fpos=None, tpos=None):
        # 设置 棋盘 board，以及该步，的棋子从哪儿 fpos，到哪儿 tpos
        # 由于 该函数可能在多个线程中调用，所以下面触发 signal.refresh
        # QT 会自动将刷新棋盘的重任放到主线程去做
        # 如果直接在非主线程调用 refresh 函数，程序可能莫名其妙的死掉。

        self.board = board
        self.fpos = fpos
        self.tpos = tpos
        self.signal.refresh.emit()

    def setReverse(self, reverse):
        # 设置棋盘反转 信号解释同 setBoard

        self.reverse = reverse
        self.signal.refresh.emit()

    def setCheck(self, check):
        # 设置将军标记 信号解释同 setBoard

        self.check = check
        self.signal.refresh.emit()

    def move(self, board, fpos, tpos, callback=None, animate=True):
        if not animate and callable(callback):
            callback()
            return

        # 棋盘动画

        label = self.getLabel(fpos)
        if not label:
            return

        label.setVisible(True)
        label.raise_()  # 将控件提到前面

        self.animate.setTargetObject(label)
        self.animate.setDuration(self.ANIMATION_DURATION)
        self.animate.setStartValue(QtCore.QRect(self.getChessGeometry(fpos)))
        self.animate.setEndValue(QtCore.QRect(self.getChessGeometry(tpos)))
        self.animate.start()

        # 动画完成的回调，目前只用于刷新棋盘
        if callable(callback):
            QtCore.QTimer.singleShot(self.ANIMATION_DURATION, callback)

    @QtCore.Slot()
    def refresh(self):
        # 刷新棋盘

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

    def resizeLabel(self):
        w = self.parentWidget().width()
        h = self.parentWidget().height()
        self.label.setGeometry(0, 0, w, h)
        font = self.label.font()
        font.setPointSize(self.csize / 4)
        self.label.setFont(font)

    def resizeEvent(self, event):
        # 窗口大小变化之后，修改棋盘和棋子的大小

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
        self.resizeLabel()
        self.refresh()

    def mousePressEvent(self, event):
        # 鼠标点击事件
        # 只处理鼠标左键点击

        if event.buttons() != QtCore.Qt.LeftButton:
            return super().mousePressEvent(event)

        # 获取点击的棋盘坐标
        pos = self.getPosition(event)
        if not pos:
            return
        # logger.debug("click %s", pos)
        self.clickPosition(pos)

    def clickPosition(self, pos):
        if callable(self.callback):
            self.callback(pos)

    def getLabel(self, pos):
        # 获取某个位置的棋子 Label

        if not pos:
            return None
        label = self.labels[tuple(pos)]
        if not label:
            return None
        return label

    def setChess(self, pos, chess):
        # 将某个位置设置成某个棋子

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
        # 获取某个位置棋子在棋盘的坐标及尺寸

        pos = self.fitPosition(pos)
        return QtCore.QRect(
            pos[0] * self.csize,
            pos[1] * self.csize,
            self.csize,
            self.csize
        )

    def fitPosition(self, pos):
        '''如果旋转棋盘，那么修正棋子的位置'''

        if self.reverse:
            return (Chess.W - pos[0] - 1, Chess.H - pos[1] - 1)
        else:
            return pos

    def getPosition(self, event):
        # 通过鼠标位置，获取棋子坐标的位置

        x = event.x() // self.csize
        y = event.y() // self.csize

        if x < 0 or x >= Chess.W:
            return None
        if y < 0 or y >= Chess.H:
            return None

        pos = (int(x), int(y))
        return self.fitPosition(pos)


class BoardFrame(QtWidgets.QFrame):

    def __init__(self, parent=None, board_class=Board):
        super().__init__(parent)
        self.board = board_class(self)
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
    ui.board.setBoard(Chess.ORIGIN)
    ui.show()
    app.exec_()


if __name__ == '__main__':
    main()
