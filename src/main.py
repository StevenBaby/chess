# coding=utf-8

import sys
import time
from functools import partial

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from board import BoardFrame
from settings import Settings

from engine import Engine
from engine import UCCIEngine
from engine import Chess
from engine import dirpath
from engine import logger

import audio
import system


class GameSignal(QtCore.QObject):

    hint = QtCore.Signal(bool)
    undo = QtCore.Signal(None)
    redo = QtCore.Signal(None)
    reset = QtCore.Signal(None)
    debug = QtCore.Signal(None)

    load = QtCore.Signal(None)
    save = QtCore.Signal(None)

    move = QtCore.Signal(int)
    difficulty = QtCore.Signal(int)
    checkmate = QtCore.Signal(None)
    animate = QtCore.Signal(tuple, tuple)
    settings = QtCore.Signal(None)


class ContextMenuMixin(QtWidgets.QWidget):

    max_difficulty = 7

    items = [
        ['提示', 'Ctrl+H', lambda self: self.signal.hint.emit(True)],
        ['悔棋', 'Ctrl+Z', lambda self: self.signal.undo.emit()],
        ['重走', 'Ctrl+Shift+Z', lambda self: self.signal.redo.emit()],
        ['重置', 'Ctrl+N', lambda self: self.signal.reset.emit()],
        'separator',
        ['载入', 'Ctrl+O', lambda self: self.signal.load.emit()],
        ['保存', 'Ctrl+S', lambda self: self.signal.save.emit()],
        'separator',
        ['设置', '', lambda self: self.signal.settings.emit()],
    ]

    if system.DEBUG:
        items.extend(
            [
                ['调试', 'Ctrl+D', lambda self: self.signal.debug.emit()],
                'separator',
            ]
        )

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
                if not key:
                    continue
                shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(key), self)
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
                action = QtWidgets.QAction(name, self)
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
            action = QtWidgets.QAction(str(difficulty), self)
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

        self.settings = Settings(self)
        self.settings.setWindowIcon(QtGui.QIcon(self.board.FAVICON))
        self.settings.transprancy.valueChanged.connect(
            lambda e: self.setWindowOpacity((100 - e) / 100)
        )

        self.settings.reverse.stateChanged.connect(
            lambda e: self.board.setReverse(self.settings.reverse.isChecked())
        )

        self.settings.buttonBox.accepted.connect(self.accepted)

        self.signal.settings.connect(self.settings.show)

        self.board.csize = 80
        self.board.callback = self.board_callback
        self.resize(self.board.csize * Chess.W, self.board.csize * Chess.H)
        self.audioPlay = QtCore.Slot(int)(audio.play)

        self.signal.hint.connect(self.contextHint)
        self.signal.hint.connect(self.hint)
        self.signal.undo.connect(self.undo)
        self.signal.redo.connect(self.redo)
        self.signal.reset.connect(self.reset)
        self.signal.debug.connect(self.debug)

        self.signal.load.connect(self.load)
        self.signal.save.connect(self.save)

        self.signal.move.connect(self.audioPlay)
        self.signal.difficulty.connect(self.change_difficulty)
        self.signal.difficulty.connect(self.show_difficulty)

        self.signal.checkmate.connect(self.checkmateMessage)

        self.signal.animate.connect(self.animate)

        self.signal.hint.emit(False)

        self.delay = 0.3
        self.depth_computer = 1
        self.depth_hint = 7

        self.engine_side = [Chess.BLACK]
        self.human_side = [Chess.RED]

        audio.init()
        self.reset()

    def accepted(self):
        logger.info("setting accepted....")

        # 设置棋手或AI
        self.engine_side = []
        self.human_side = []

        if self.settings.redside.currentText() == '棋手':
            self.human_side.append(Chess.RED)
        else:
            self.engine_side.append(Chess.RED)

        if self.settings.blackside.currentText() == '棋手':
            self.human_side.append(Chess.BLACK)
        else:
            self.engine_side.append(Chess.BLACK)

        self.try_engine_move()

    def try_engine_move(self):
        if self.engine.sit.turn in self.engine_side:
            self.engine.go(depth=self.depth_computer)

    def reset(self):
        if hasattr(self, 'engine'):
            self.engine.close()

        self.engine = UCCIEngine(filename=self.ELEEYE, callback=self.engine_callback)
        self.engine.start()

        self.fpos = None

        self.signal.move.emit(Chess.NEWGAME)

        self.signal.difficulty.emit(self.depth_computer)
        self.updateBoard()
        self.board.setCheck(None)
        self.try_engine_move()

    @QtCore.Slot(None)
    def undo(self):
        for _ in range(2):
            self.engine.undo()
            if self.engine.sit.turn in self.human_side:
                break

        self.signal.hint.emit(False)
        self.updateBoard()

    @QtCore.Slot(None)
    def redo(self):
        for _ in range(2):
            self.engine.redo()
            logger.debug('engine redo result %d', self.engine.sit.result)
            self.signal.move.emit(self.engine.sit.result)
            if self.engine.sit.turn in self.human_side:
                break

        self.signal.hint.emit(False)
        self.updateBoard()

    @QtCore.Slot(bool)
    def hint(self, hint=True):
        if hint:
            self.engine.go(depth=self.depth_hint)

    @QtCore.Slot(None)
    def debug(self):
        logger.debug("debug slot.....")
        logger.debug(self.engine.sit.format_fen())

    @QtCore.Slot(None)
    def save(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filename = dialog.getSaveFileName(
            self, "保存中国象棋文件 Fen", ".", "文件 (*.fen)")[0]
        if not filename:
            return
        fen = self.engine.sit.format_fen()
        with open(filename, 'w') as file:
            file.write(fen)
        logger.info("save file %s - fen %s", filename, fen)

    @QtCore.Slot(None)
    def load(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filename = dialog.getOpenFileName(
            self, "打开中国象棋文件 Fen", ".", "文件 (*.fen)")[0]
        if not filename:
            return
        with open(filename, 'r') as file:
            fen = file.read()

        if self.engine.sit.parse_fen(fen, load=True):
            moves = self.engine.sit.moves
            self.engine.sit.moves = []
            for fpos, tpos in moves:
                result = self.engine.move(fpos, tpos)
                if result == Chess.CHECKMATE:
                    self.signal.checkmate.emit()
                    break

            self.updateBoard()
        else:
            QtWidgets.QMessageBox().warning(self, 'Warning', 'Load file failure!!!')

    @QtCore.Slot(tuple, tuple)
    def animate(self, fpos, tpos):
        self.board.move(self.engine.sit.board, fpos, tpos, self.updateBoard)

    def move(self, fpos, tpos):
        if self.engine.checkmate:
            self.signal.checkmate.emit()
            return

        result = self.engine.move(fpos, tpos)
        logger.debug('move result %s', result)
        if not result:
            return

        if result != Chess.INVALID:
            self.signal.animate.emit(fpos, tpos)

        if self.engine.sit.check:
            self.board.setCheck(self.engine.sit.check)
            logger.debug('invalid ... %s', self.engine.sit.check)
        else:
            self.board.setCheck(None)

        self.signal.move.emit(result)

        if result == Chess.CHECKMATE:
            logger.debug("emit checkmate")
            self.signal.checkmate.emit()
            return

        self.try_engine_move()

    @QtCore.Slot(int)
    def change_difficulty(self, diff):
        self.depth_computer = diff

    def updateBoard(self):
        self.board.setBoard(
            self.engine.sit.board,
            self.engine.sit.fpos,
            self.engine.sit.tpos
        )

    @QtCore.Slot(None)
    def checkmateMessage(self):
        if not self.engine.checkmate:
            return
        if self.engine.sit.turn == Chess.RED:
            QtWidgets.QMessageBox(self).warning(self, '信息', '黑方胜!!!')
        else:
            QtWidgets.QMessageBox(self).information(self, '信息', '红方胜!!!')

    def engine_callback(self, move_type, fpos, tpos):
        time.sleep(self.delay)
        self.signal.hint.emit(False)
        if move_type == Chess.MOVE:
            self.move(fpos, tpos)
        # if move_type == Chess.CHECKMATE:
        #     self.signal.checkmate.emit()

    def board_callback(self, pos):
        if self.engine.sit.where_turn(pos) == self.engine.sit.turn:
            self.fpos = pos
            self.board.setBoard(self.engine.sit.board, self.fpos)
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
