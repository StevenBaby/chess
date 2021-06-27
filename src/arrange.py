# coding=utf-8

'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-25
'''
import numpy as np
from functools import partial
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from board import Board
from board import BoardSignal
from chess import Chess
from logger import logger
from context import BaseContextMenu
from toast import Toast
from situation import Generator


class PositionValidator(object):

    def validateKing(self, pos):
        if pos[1] > 2:
            return False
        if pos[0] < 3:
            return False
        if pos[0] > 5:
            return False
        return True

    def validateAdvisor(self, pos):
        if pos not in {
            (3, 0),
            (5, 0),
            (4, 1),
            (3, 2),
            (5, 2),
        }:
            return False
        return True

    def validateBishop(self, pos):
        if pos not in {
            (2, 0),
            (6, 0),
            (0, 2),
            (4, 2),
            (8, 2),
            (2, 4),
            (6, 4),
        }:
            return False
        return True

    def validatePawn(self, board, pos, chess):
        if pos[1] > 4:
            return True
        if pos[1] < 3:
            return False
        if pos[0] % 2 != 0:
            return False

        if Chess.is_black(chess):
            if board[(pos[0], 3)] == chess:
                return False
            if board[(pos[0], 4)] == chess:
                return False
        else:
            if board[(8 - pos[0], 5)] == chess:
                return False
            if board[(8 - pos[0], 6)] == chess:
                return False

        return True

    def validatePosition(self, board, pos, chess):
        ctype = chess & Chess.CMASK
        if ctype in {Chess.ROOK, Chess.KNIGHT, Chess.CANNON}:
            return True
        if Chess.is_red(chess):
            pos = (8 - pos[0], 9 - pos[1])

        if ctype == Chess.KING:
            return self.validateKing(pos)
        if ctype == Chess.ADVISOR:
            return self.validateAdvisor(pos)
        if ctype == Chess.BISHOP:
            return self.validateBishop(pos)
        if ctype == Chess.PAWN:
            return self.validatePawn(board, pos, chess)
        return False

    def validateArrange(self, board, turn):
        whereK = np.argwhere(board == Chess.K)
        if len(whereK) == 0:
            raise Exception('布局中不能没有帅')
        wherek = np.argwhere(board == Chess.k)
        if len(wherek) == 0:
            raise Exception('布局中不能没有将')

        k = tuple(wherek[0])

        for idx in range(k[1] + 1, 10):
            pos = (k[0], idx)
            if not board[pos]:
                continue
            if board[pos] != Chess.K:
                break
            raise Exception('将帅不能见面')

        generator = Generator()
        check = generator.get_check(board, Chess.invert(turn))
        logger.debug("get check %s", check)
        if check:
            raise Exception('处于将死的状态')
        if generator.is_checkmate(board, turn):
            raise Exception('处于将死的状态')


class ArrangeSignal(BoardSignal):

    side = QtCore.Signal(int)
    finish = QtCore.Signal(bool)
    clear = QtCore.Signal(None)


class ArrangeContextMenu(BaseContextMenu):

    items = [
        ('清空棋盘', '', lambda self: self.signal.clear.emit(), True),
        ('红方先行', '', lambda self: self.signal.side.emit(Chess.RED), True),
        ('黑方先行', '', lambda self: self.signal.side.emit(Chess.BLACK), True),
        'separator',
        ('完成布局', '', lambda self: self.signal.finish.emit(False), True),
    ]


class ClickedLabel(QtWidgets.QLabel):

    clicked = QtCore.Signal(QtWidgets.QLabel)

    def mousePressEvent(self, event) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)


class ChessSelector(QtWidgets.QDialog):

    selected = QtCore.Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.ToolTip)
        style = self.styleSheet()
        self.setStyleSheet(
            '''
            ChessSelector{
                background-clip: border;
                border-radius: 7px;
                border-style: solid;
                border-width: 2px;
                border-color: #82a0b9;
            }
            '''
        )

        self.labels = [ClickedLabel(self) for _ in range(14)]
        for label in self.labels:
            label.clicked.connect(self.labelClick)
            label.setStyleSheet(style)
            label.setVisible(False)
            label.chess = 0

    def labelClick(self, label):
        self.selected.emit(label.chess)
        self.hide()

    def setChess(self, x, y, index, chess):
        # 将某个位置设置成某个棋子

        label = self.labels[index]
        if not chess:
            label.setVisible(False)
            return

        image = self.parentWidget().IMAGES[chess]
        label.setPixmap(image)
        label.setScaledContents(True)
        label.setGeometry(x * self.csize, y * self.csize, self.csize, self.csize)
        label.setVisible(True)
        label.chess = chess

    def show(self, pos, chesses: list):
        length = len(chesses)
        if length == 1:
            w = 1
            h = 1
        elif length < 3:
            w = 2
            h = 1
        else:
            w = (len(chesses) + 1) // 2
            h = 2

        for label in self.labels:
            label.setVisible(False)

        for idx, chess in enumerate(chesses):
            self.setChess(idx % w, idx // w, idx, chess)

        parent = self.parentWidget()
        geo = parent.getChessGeometry(pos)
        pos = parent.mapToGlobal(QtCore.QPoint(0, 0))

        maxpos = parent.mapToGlobal(QtCore.QPoint(parent.width(), parent.height()))
        x = pos.x() + geo.x()
        y = pos.y() + geo.y()

        width = self.csize * w
        height = self.csize * h

        if x + width > maxpos.x():
            x = maxpos.x() - width

        if y + height > maxpos.y():
            y = maxpos.y() - height

        self.setGeometry(x, y, width, height)
        super().show()

    @property
    def csize(self):
        return self.parentWidget().csize


class ArrangeBoard(Board, PositionValidator):

    '''用于排布开局'''
    signal_class = ArrangeSignal

    def __init__(self, parent=None, callback=None):
        super().__init__(parent=parent, callback=callback)
        self.board = np.mat(np.zeros((Chess.WIDTH, Chess.HEIGHT)), dtype=int)
        self.selector = ChessSelector(self)
        self.selector.selected.connect(self.selectChess)
        self.position = None
        self.arranging = False
        self.arrange_menu = ArrangeContextMenu(parent, self.signal)
        self.first_side = Chess.RED

        self.signal.finish.connect(self.finishArrange)
        self.signal.side.connect(self.changeSide)
        self.signal.clear.connect(self.newBoard)

        self.toast = Toast(parent)

    def finishArrange(self, finished):
        if finished:
            return
        try:
            self.validateArrange(self.board, self.first_side)
        except Exception as e:
            logger.debug(e)
            self.toast.message(str(e))
            return

        self.arranging = False
        self.signal.finish.emit(True)

    def changeSide(self, side):
        logger.debug('finish side %s', side)
        self.first_side = side

    def newBoard(self):
        self.board = np.mat(np.zeros((Chess.WIDTH, Chess.HEIGHT)), dtype=int)
        self.signal.refresh.emit()

    def selectChess(self, chess):
        if not self.position:
            return
        self.board[self.position] = chess
        self.signal.refresh.emit()

    def clickPosition(self, pos):
        if not self.arranging:
            return super().clickPosition(pos)

        if self.board[pos]:
            self.board[pos] = 0
            self.signal.refresh.emit()
            self.selector.hide()
            return

        if self.selector.isVisible():
            self.selector.hide()
            return
        self.position = pos

        chesses = []
        for chess in Chess.CHESSES:
            wheres = np.argwhere(self.board == chess)
            origin = np.argwhere(Chess.ORIGIN == chess)
            if len(wheres) < len(origin) and self.validatePosition(self.board, pos, chess):
                chesses.append(chess)
        if not chesses:
            return
        self.selector.show(pos, chesses)

    def resizeEvent(self, event):
        self.selector.hide()
        return super().resizeEvent(event)


def main():
    from context import BaseContextMenuWidget
    from board import BoardFrame

    class Widget(BoardFrame, BaseContextMenuWidget):

        def __init__(self, parent=None) -> None:
            super().__init__(parent=parent, board_class=ArrangeBoard)
            self.menu = self.board.arrange_menu
            self.setupContextMenu()

    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Widget()
    ui.board.arranging = True
    # ui = ChessSelector()
    ui.show()
    app.exec_()


if __name__ == '__main__':
    main()
