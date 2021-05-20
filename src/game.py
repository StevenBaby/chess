# coding=utf-8

import sys
import time
from functools import partial

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from board import BoardFrame
from engine import Engine
from engine import UCCIEngine
from engine import Chess
from engine import dirpath
from engine import logger

import audio


class GameSignal(QtCore.QObject):

    hint = QtCore.Signal(bool)
    undo = QtCore.Signal(None)
    reset = QtCore.Signal(None)
    debug = QtCore.Signal(None)
    move = QtCore.Signal(int)

    difficulty = QtCore.Signal(int)


class ContextMenuMixin(QtWidgets.QWidget):

    max_difficulty = 7

    items = [
        ['提示', 'Ctrl+H', lambda self: self.signal.hint.emit(True)],
        ['悔棋', 'Ctrl+Z', lambda self: self.signal.undo.emit()],
        ['重置', 'Ctrl+N', lambda self: self.signal.reset.emit()],
        'separator',
        ['调试', 'Ctrl+D', lambda self: self.signal.debug.emit()],
        'separator',
    ]

    def __init__(self, parent=None):
        if not hasattr(self, 'signal'):
            self.signal = GameSignal()

        self.font_families = QtGui.QFont()
        self.font_families.setFamilies([u"DengXian"])
        self.font_families.setPointSize(12)
        self.shortcuts = []
        self.menus = []

    def createShortCut(self):
        for item in self.items:
            if isinstance(item, list) and len(item) == 3:
                name, key, slot = item
                shortcut = QtGui.QShortcut(QtGui.QKeySequence(key), self)
                shortcut.activated.connect(partial(slot, self))
                self.shortcuts.append(shortcut)

    def createContextMenu(self):
        self.createShortCut()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.context_menu = QtWidgets.QMenu(self, title="菜单")

        for item in self.items:
            if isinstance(item, list) and len(item) == 3:
                name, key, slot = item
                action = QtGui.QAction(name, self)
                action.setFont(self.font_families)
                action.setShortcut(key)
                action.triggered.connect(partial(slot, self))
                self.context_menu.addAction(action)

                logger.info(f"add action {len(self.context_menu.actions())} {name}")
                continue
            if item == "separator":
                self.context_menu.addSeparator()
                continue

        self.difficulty_menu = QtWidgets.QMenu(self, title="难度")
        action = self.difficulty_menu.menuAction()
        action.setFont(self.font_families)
        self.context_menu.addAction(action)

        for diff in range(self.max_difficulty):
            difficulty = diff + 1
            action = QtGui.QAction(str(difficulty), self)
            action.setFont(self.font_families)
            action.setCheckable(True)
            self.difficulty_menu.addAction(action)

            action.triggered.connect(partial(self.signal.difficulty.emit, difficulty))

    @QtCore.Slot(int)
    def show_difficulty(self, diff):
        logger.debug('difficulty %s', diff)
        actions = self.difficulty_menu.actions()
        if diff > len(actions):
            return
        for index, action in enumerate(actions):
            if index == (diff - 1):
                action.setChecked(True)
            else:
                action.setChecked(False)

    @QtCore.Slot(None)
    def test_slot(self):
        logger.debug('test slot called!!!')

    def showContextMenu(self, pos):
        self.context_menu.move(QtGui.QCursor().pos())
        self.context_menu.show()

    @QtCore.Slot(bool)
    def contextHint(self, hint=True):
        # logger.debug('context hint ....')
        self.context_menu.actions()[0].setEnabled(not hint)
        self.shortcuts[0].setEnabled(not hint)


class Game(BoardFrame, ContextMenuMixin):

    ELEEYE = dirpath / 'engines/eleeye/eleeye.exe'

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        ContextMenuMixin.__init__(self)

        if not hasattr(self, 'signal'):
            self.signal = GameSignal()

        self.createContextMenu()

        self.board.csize = 50
        self.board.callback = self.board_callback
        self.resize(self.board.csize * Chess.W, self.board.csize * Chess.H)
        self.audioPlay = QtCore.Slot(int)(audio.play)

        self.signal.hint.connect(self.contextHint)
        self.signal.hint.connect(self.hint)
        self.signal.undo.connect(self.undo)
        self.signal.reset.connect(self.reset)
        self.signal.debug.connect(self.debug)

        self.signal.move.connect(self.audioPlay)
        self.signal.difficulty.connect(self.change_difficulty)
        self.signal.difficulty.connect(self.show_difficulty)

        self.delay = 0.7
        self.depth_computer = 1
        self.depth_hint = 7

        audio.init()
        self.reset()

    def reset(self):
        if hasattr(self, 'engine'):
            self.engine.close()

        self.engine = UCCIEngine(filename=self.ELEEYE, callback=self.engine_callback)

        self.engine.fen = self.engine.format_fen()

        logger.debug(self.engine.fen)

        self.engine.start()

        self.fpos = None

        self.signal.difficulty.emit(self.depth_computer)
        self.updateBoard()

    @QtCore.Slot(None)
    def undo(self):
        logger.debug("undo called....")
        for _ in range(2):
            if self.engine.steps:
                self.engine.unmove()
                if self.engine.turn == Chess.RED:
                    break

        self.updateBoard()

    @QtCore.Slot(bool)
    def hint(self, hint=True):
        if hint:
            self.engine.go(depth=self.depth_hint)

    @QtCore.Slot(None)
    def debug(self):
        logger.debug("debug slot.....")
        logger.debug(self.engine.format_fen())

    def move(self, fpos, tpos):
        result = self.engine.move(fpos, tpos)
        if not result:
            return

        logger.debug('move result %d turn %d', result, self.engine.turn)
        self.signal.move.emit(result)

        self.updateBoard()
        if result == Engine.MOVE_DEAD:
            return

        if self.engine.turn == Chess.BLACK:
            self.engine.go(depth=self.depth_computer)

    @QtCore.Slot(int)
    def change_difficulty(self, diff):
        self.depth_computer = diff

    def updateBoard(self):
        self.board.setBoard(self.engine.board, self.engine.fpos, self.engine.tpos)

    def engine_callback(self, move):
        time.sleep(self.delay)
        self.signal.hint.emit(False)
        if move.type == Engine.MOVE_BEST:
            self.move(move.fpos, move.tpos)

    def board_callback(self, pos):
        if self.engine.color(pos) == self.engine.turn:
            self.fpos = pos
            self.board.setBoard(self.engine.board, self.fpos)
            return

        if not self.fpos:
            return

        self.move(self.fpos, pos)

    def closeEvent(self, event):
        self.engine.close()
        return super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Game()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
