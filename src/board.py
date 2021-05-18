
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap

import numpy as np
from numpy import mat
from numpy import zeros

from engine import dirpath
from engine import Chess
from engine import logger

from attrdict import attrdict


class Singal(QtCore.QObject):

    refresh = QtCore.Signal(None)


class Board(QLabel):

    BOARD = str(dirpath / u"images/board.png")
    MARK = str(dirpath / u"images/mark.png")
    FAVICON = str(dirpath / u"images/favicon.ico")

    IMAGES = {
        Chess.RED: {
            Chess.ROOK: str(dirpath / 'images/red_rook.png'),
            Chess.KNIGHT: str(dirpath / 'images/red_knight.png'),
            Chess.BISHOP: str(dirpath / 'images/red_bishop.png'),
            Chess.ADVISOR: str(dirpath / 'images/red_advisor.png'),
            Chess.KING: str(dirpath / 'images/red_king.png'),
            Chess.CANNON: str(dirpath / 'images/red_cannon.png'),
            Chess.PAWN: str(dirpath / 'images/red_pawn.png'),
        },
        Chess.BLACK: {
            Chess.ROOK: str(dirpath / 'images/black_rook.png'),
            Chess.KNIGHT: str(dirpath / 'images/black_knight.png'),
            Chess.BISHOP: str(dirpath / 'images/black_bishop.png'),
            Chess.ADVISOR: str(dirpath / 'images/black_advisor.png'),
            Chess.KING: str(dirpath / 'images/black_king.png'),
            Chess.CANNON: str(dirpath / 'images/black_cannon.png'),
            Chess.PAWN: str(dirpath / 'images/black_pawn.png'),
        }
    }

    flags = QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint

    def __init__(self, parent=None, callback=None):
        super().__init__(parent=parent)

        self.csize = 60
        self.board_image = QtGui.QPixmap(self.BOARD)

        if parent is None:
            self.setWindowIcon(QtGui.QIcon(self.FAVICON))
            self.setWindowTitle(u"Chinese Chess")
            # self.setWindowFlags(self.flags)

        self.setObjectName(u"Board")
        self.setScaledContents(True)

        self.resize(self.csize * Chess.W, self.csize * Chess.H)

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

        self.signal = Singal()
        self.signal.refresh.connect(self.refresh)

        self.labels = mat(zeros((Chess.W, Chess.H,)), dtype=QtWidgets.QLabel)
        self.board = mat(zeros((Chess.W, Chess.H,)), dtype=int)

        self.fpos = None
        self.tpos = None

        self.update()

        self.callback = callback

    def setBoard(self, board, fpos=None, tpos=None):
        self.board = board
        self.fpos = fpos
        self.tpos = tpos
        self.signal.refresh.emit()

    @QtCore.Slot()
    def refresh(self):
        self.update()

    def update(self):
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

        for w in range(Chess.W):
            for h in range(Chess.H):
                pos = (w, h)
                label = self.labels[pos]
                if not label:
                    continue
                label.setGeometry(self.getChessGeometry(label.pos))

        self.update()

    def mousePressEvent(self, event):
        pos = self.getPosition(event)
        if not pos:
            return
        # logger.debug("click %s", pos)
        self.clickPosition(pos)

    def clickPosition(self, pos):
        if callable(self.callback):
            self.callback(pos)

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


class BoardFrame(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board = Board(self)
        if parent is None:
            self.setWindowIcon(QtGui.QIcon(self.board.FAVICON))
            self.setWindowTitle(u"Chinese Chess")
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
