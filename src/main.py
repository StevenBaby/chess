# coding=utf-8
import os
import sys

import logging


import numpy as np
from numpy import mat
from numpy import zeros

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
# from PySide6.QtWidgets import QSizePolicy


dirname = os.path.dirname(__file__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


class Chess(object):

    RED = 1
    BLACK = -1

    PAWN = 1
    ROOK = 2
    HORSE = 3
    BISHOP = 4
    KNIGHT = 5
    CANNON = 6
    KING = 7

    WIDTH = 9
    HEIGHT = 10
    W = WIDTH
    H = HEIGHT


class Game(Chess):

    ORIGIN = {
        (0, 0): Chess.BLACK * Chess.ROOK,
        (1, 0): Chess.BLACK * Chess.HORSE,
        (2, 0): Chess.BLACK * Chess.BISHOP,
        (3, 0): Chess.BLACK * Chess.KNIGHT,
        (4, 0): Chess.BLACK * Chess.KING,
        (5, 0): Chess.BLACK * Chess.KNIGHT,
        (6, 0): Chess.BLACK * Chess.BISHOP,
        (7, 0): Chess.BLACK * Chess.HORSE,
        (8, 0): Chess.BLACK * Chess.ROOK,

        (1, 2): Chess.BLACK * Chess.CANNON,
        (7, 2): Chess.BLACK * Chess.CANNON,

        (0, 3): Chess.BLACK * Chess.PAWN,
        (2, 3): Chess.BLACK * Chess.PAWN,
        (4, 3): Chess.BLACK * Chess.PAWN,
        (6, 3): Chess.BLACK * Chess.PAWN,
        (8, 3): Chess.BLACK * Chess.PAWN,

        (0, 9): Chess.RED * Chess.ROOK,
        (1, 9): Chess.RED * Chess.HORSE,
        (2, 9): Chess.RED * Chess.BISHOP,
        (3, 9): Chess.RED * Chess.KNIGHT,
        (4, 9): Chess.RED * Chess.KING,
        (5, 9): Chess.RED * Chess.KNIGHT,
        (6, 9): Chess.RED * Chess.BISHOP,
        (7, 9): Chess.RED * Chess.HORSE,
        (8, 9): Chess.RED * Chess.ROOK,

        (1, 7): Chess.RED * Chess.CANNON,
        (7, 7): Chess.RED * Chess.CANNON,

        (0, 6): Chess.RED * Chess.PAWN,
        (2, 6): Chess.RED * Chess.PAWN,
        (4, 6): Chess.RED * Chess.PAWN,
        (6, 6): Chess.RED * Chess.PAWN,
        (8, 6): Chess.RED * Chess.PAWN,
    }

    def __init__(self):
        self.board = mat(zeros((Chess.W, Chess.H)), dtype=int)

        for pos, chess in self.ORIGIN.items():
            self.board[pos] = chess

    def move(self, first, second):
        chess = self.board[first]
        self.board[first] = 0
        self.board[second] = chess


class Board(QLabel):

    flags = QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint

    FAVICON = os.path.join(dirname, 'images/favicon.ico')
    BOARD = os.path.join(dirname, u"images/board.png")
    MARK = os.path.join(dirname, 'images/mark.png')
    ROOK1 = os.path.join(dirname, 'images/black_rook.png')

    IMAGES = {
        Chess.RED: {
            Chess.ROOK: os.path.join(dirname, 'images/red_rook.png'),
            Chess.HORSE: os.path.join(dirname, 'images/red_horse.png'),
            Chess.BISHOP: os.path.join(dirname, 'images/red_bishop.png'),
            Chess.KNIGHT: os.path.join(dirname, 'images/red_knight.png'),
            Chess.KING: os.path.join(dirname, 'images/red_king.png'),
            Chess.CANNON: os.path.join(dirname, 'images/red_cannon.png'),
            Chess.PAWN: os.path.join(dirname, 'images/red_pawn.png'),
        },
        Chess.BLACK: {
            Chess.ROOK: os.path.join(dirname, 'images/black_rook.png'),
            Chess.HORSE: os.path.join(dirname, 'images/black_horse.png'),
            Chess.BISHOP: os.path.join(dirname, 'images/black_bishop.png'),
            Chess.KNIGHT: os.path.join(dirname, 'images/black_knight.png'),
            Chess.KING: os.path.join(dirname, 'images/black_king.png'),
            Chess.CANNON: os.path.join(dirname, 'images/black_cannon.png'),
            Chess.PAWN: os.path.join(dirname, 'images/black_pawn.png'),
        }
    }

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(self.FAVICON))
        self.setWindowTitle(u"Chinese Chess")
        self.setPixmap(QtGui.QPixmap(self.BOARD))
        self.setObjectName(u"Chess")
        self.setScaledContents(True)
        self.resize(810, 900)
        self.setWindowFlags(self.flags)

        for _, paths in self.IMAGES.items():
            for chess, path in paths.items():
                paths[chess] = QPixmap(path)

        mark = QPixmap(self.MARK)
        self.mark1 = QLabel(self)
        self.mark1.setPixmap(mark)
        self.mark1.setScaledContents(True)
        self.mark1.setVisible(False)

        self.mark2 = QLabel(self)
        self.mark2.setPixmap(mark)
        self.mark2.setScaledContents(True)
        self.mark2.setVisible(False)

        self.csize = 90
        self.labels = mat(zeros((Chess.W, Chess.H,)), dtype=QtWidgets.QLabel)
        self.game = Game()
        self.refresh()

        self.choice = None

    def refresh(self):
        for x in range(Chess.W):
            for y in range(Chess.H):
                pos = (x, y)
                self.setChess(pos, self.game.board[pos])

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        height = h
        width = h / Chess.H * Chess.W

        if width > w:
            width = w
            height = width / Chess.W * Chess.H

        self.resize(int(width), int(height))
        self.csize = width // Chess.W

        for w in range(Chess.W):
            for h in range(Chess.H):
                pos = (w, h)
                label = self.labels[pos]
                if not label:
                    continue
                label.setGeometry(self.getChessGeometry(label.pos))

    def mousePressEvent(self, event):
        pos = self.getPosition(event)
        if not pos:
            return
        logger.debug("click %s", pos)
        chess = self.game.board[pos]

        if not self.choice and not chess:
            return

        if not self.choice:
            self.choice = pos
            self.mark1.setGeometry(self.getChessGeometry(pos))
            self.mark1.setVisible(True)
            self.mark2.setVisible(False)
            return

        if not chess:
            self.game.move(self.choice, pos)
            self.mark2.setGeometry(self.getChessGeometry(pos))
            self.mark2.setVisible(True)
            self.refresh()
            self.choice = None

    def setChess(self, pos, chess):
        label = self.labels[pos]
        if not label:
            label = QLabel(self)
            label.pos = pos
            self.labels[pos] = label

        if not chess:
            label.setVisible(False)
            return
        cside = 1 if chess > 0 else -1
        ctype = abs(chess)

        image = self.IMAGES[cside][ctype]
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    board = Board()
    board.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
