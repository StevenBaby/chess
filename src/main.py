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

    NONE = 0
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
        self.turn = Chess.RED

        for pos, chess in self.ORIGIN.items():
            self.board[pos] = chess

    def validate_rook(self, fpos, tpos, chess, color, offset):
        if offset[0] == 0:
            for var in range(min(fpos[1], tpos[1]) + 1, max(fpos[1], tpos[1])):
                pos = (fpos[0], var)
                if self.board[pos]:
                    return False
            return True
        elif offset[1] == 0:
            for var in range(min(fpos[0], tpos[0]) + 1, max(fpos[0], tpos[0])):
                pos = (var, fpos[1])
                if self.board[pos]:
                    return False
            return True
        else:
            return False

    def validate_horse(self, fpos, tpos, chess, color, offset):
        if offset == (1, 2) and not self.board[(fpos[0], (fpos[1] + tpos[1]) // 2)]:
            return True
        elif offset == (2, 1) and not self.board[((fpos[0] + tpos[0]) // 2, fpos[1])]:
            return True
        else:
            return False

    def validate_bishop(self, fpos, tpos, chess, color, offset):
        if offset != (2, 2):
            return False

        if color == Chess.BLACK and tpos[1] > 4:
            return False
        if color == Chess.RED and tpos[1] < 5:
            return False

        pos = ((fpos[0] + tpos[0]) // 2, (fpos[1] + tpos[1]) // 2)
        if self.board[pos]:  # 卡象眼
            return False
        return True

    def validate_knight(self, fpos, tpos, chess, color, offset):
        if offset != (1, 1):
            return False
        if tpos[0] < 3 or tpos[0] > 5:
            return False
        if color == Chess.BLACK and tpos[1] > 2:
            return False
        if color == Chess.RED and tpos[1] < 7:
            return False
        return True

    def validate_king(self, fpos, tpos, chess, color, offset):
        if tpos[0] < 3 or tpos[0] > 5:
            return False
        if color == Chess.BLACK and tpos[1] > 2:
            return False
        if color == Chess.RED and tpos[1] < 7:
            return False

        if fpos[0] == tpos[0] and abs(fpos[1] - tpos[1]) == 1:
            return True
        elif fpos[1] == tpos[1] and abs(fpos[0] - tpos[0]) == 1:
            return True
        else:
            return False

    def validate_cannon(self, fpos, tpos, chess, color, offset):
        if offset[0] == 0:
            barrier = 0
            for var in range(min(fpos[1], tpos[1]) + 1, max(fpos[1], tpos[1])):
                pos = (fpos[0], var)
                if self.board[pos] and barrier == 1:
                    return False
                if self.board[pos]:
                    barrier = 1
        elif offset[1] == 0:
            barrier = 0
            for var in range(min(fpos[0], tpos[0]) + 1, max(fpos[0], tpos[0])):
                pos = (var, fpos[1])
                if self.board[pos] and barrier == 1:
                    return False
                if self.board[pos]:
                    barrier = 1
        else:
            return False

        if barrier == 0 and not self.board[tpos]:
            return True
        elif barrier == 1 and self.board[tpos] and np.sign(self.board[tpos]) != color:
            return True
        return False

    def validate_pawn(self, fpos, tpos, chess, color, offset):
        if offset not in {(0, 1), (1, 0)}:
            return False
        if color == Chess.RED:
            if (tpos[1] - fpos[1]) > 0:
                return False
            if fpos[1] > 4 and fpos[0] - tpos[0] != 0:
                return False
        if color == Chess.BLACK:
            if (tpos[1] - fpos[1]) < 0:
                return False
            if fpos[1] < 5 and fpos[0] - tpos[0] != 0:
                return False

        return True

    def validate(self, fpos, tpos):
        if fpos == tpos:
            return False

        fchess = self.board[fpos]
        tchess = self.board[tpos]

        if np.sign(fchess) == np.sign(tchess):
            return False

        offset = (abs(tpos[0] - fpos[0]), abs(tpos[1] - fpos[1]))
        chess = abs(fchess)
        color = np.sign(fchess)

        if chess == Chess.ROOK:
            return self.validate_rook(fpos, tpos, chess, color, offset)
        elif chess == Chess.HORSE:
            return self.validate_horse(fpos, tpos, chess, color, offset)
        elif chess == Chess.BISHOP:
            return self.validate_bishop(fpos, tpos, chess, color, offset)
        elif chess == Chess.KNIGHT:
            return self.validate_knight(fpos, tpos, chess, color, offset)
        elif chess == Chess.KING:
            return self.validate_king(fpos, tpos, chess, color, offset)
        elif chess == Chess.CANNON:
            return self.validate_cannon(fpos, tpos, chess, color, offset)
        elif chess == Chess.PAWN:
            return self.validate_pawn(fpos, tpos, chess, color, offset)
        else:
            return False

    def move(self, fpos, tpos):
        if not self.validate(fpos, tpos):
            return False

        self.board[tpos] = self.board[fpos]
        self.board[fpos] = Chess.NONE
        self.turn *= -1
        return True


class Board(QLabel):

    flags = QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint

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

    def __init__(self, parent):
        super().__init__(parent)
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

        for w in range(Chess.W):
            for h in range(Chess.H):
                pos = (w, h)
                label = self.labels[pos]
                if not label:
                    continue
                label.setGeometry(self.getChessGeometry(label.pos))

    def setChoice(self, pos):
        if self.game.turn != np.sign(self.game.board[pos]):
            return

        self.choice = pos
        self.mark1.setGeometry(self.getChessGeometry(pos))
        self.mark1.setVisible(True)
        self.mark2.setVisible(False)

    def mousePressEvent(self, event):
        pos = self.getPosition(event)
        if not pos:
            return
        logger.debug("click %s", pos)
        chess = self.game.board[pos]

        if not self.choice and not chess:
            return

        if not self.choice:
            self.setChoice(pos)
            return

        if self.game.move(self.choice, pos):
            self.mark2.setGeometry(self.getChessGeometry(pos))
            self.mark2.setVisible(True)
            self.refresh()
            self.choice = None
        elif chess:
            self.setChoice(pos)

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


class MainWindow(QtWidgets.QMainWindow):

    FAVICON = os.path.join(dirname, 'images/favicon.ico')

    def __init__(self):
        super().__init__()
        self.board = Board(self)
        self.setWindowIcon(QtGui.QIcon(self.FAVICON))
        self.setWindowTitle(u"Chinese Chess")
        self.resize(810, 900)

    def resizeEvent(self, event):
        self.board.resizeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
