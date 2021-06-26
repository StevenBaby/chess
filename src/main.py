# coding=utf-8

import sys
import time
from functools import partial

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from board import BoardFrame

from engine import Engine
from engine import UCCIEngine
from engine import Chess
from engine import dirpath
from engine import logger

import audio
import system
from version import VERSION

from dialog import Settings
from dialog import Comments
from toast import Toast

from context import BaseContextMenu
from context import BaseContextMenuWidget

from arrange import ArrangeBoard
from manual import Manual


class GameSignal(QtCore.QObject):

    hint = QtCore.Signal(None)
    undo = QtCore.Signal(None)
    redo = QtCore.Signal(None)
    reset = QtCore.Signal(None)
    debug = QtCore.Signal(None)

    load = QtCore.Signal(None)
    save = QtCore.Signal(None)

    move = QtCore.Signal(int)

    checkmate = QtCore.Signal(None)
    animate = QtCore.Signal(tuple, tuple)
    settings = QtCore.Signal(None)
    comments = QtCore.Signal(None)
    arrange = QtCore.Signal(None)
    thinking = QtCore.Signal(bool)


class GameContextMenu(BaseContextMenu):

    items = [
        ('提示', 'Ctrl+H', lambda self: self.signal.hint.emit(), True),
        ('悔棋', 'Ctrl+Z', lambda self: self.signal.undo.emit(), True),
        ('重走', 'Ctrl+Shift+Z', lambda self: self.signal.redo.emit(), True),
        ('重置', 'Ctrl+N', lambda self: self.signal.reset.emit(), True),
        'separator',
        ('布局', 'Ctrl+A', lambda self: self.signal.arrange.emit(), True),
        ('着法', 'Ctrl+M', lambda self: self.signal.comments.emit(), True),
        ('载入', 'Ctrl+O', lambda self: self.signal.load.emit(), True),
        ('保存', 'Ctrl+S', lambda self: self.signal.save.emit(), True),
        'separator',
        ('设置', 'Ctrl+,', lambda self: self.signal.settings.emit(), False),
    ]

    if system.DEBUG:
        items.extend(
            [
                ('调试', 'Ctrl+D', lambda self: self.signal.debug.emit(), False),
                'separator',
            ]
        )


class Game(BoardFrame, BaseContextMenuWidget):

    ELEEYE = dirpath / 'engines/eleeye/eleeye.exe'

    def __init__(self, parent=None):
        super().__init__(parent, board_class=ArrangeBoard)
        self.setWindowTitle(f"中国象棋 v{VERSION}")
        self.setupContextMenu()

        self.game_signal = GameSignal()

        self.game_signal.thinking.connect(self.set_thinking)

        self.game_menu = GameContextMenu(self, self.game_signal)

        self.settings = Settings(self)
        self.settings.setWindowIcon(QtGui.QIcon(self.board.FAVICON))
        self.settings.transprancy.valueChanged.connect(
            lambda e: self.setWindowOpacity((100 - e) / 100)
        )

        self.settings.reverse.stateChanged.connect(
            lambda e: self.board.setReverse(self.settings.reverse.isChecked())
        )

        self.settings.audio.stateChanged.connect(
            lambda e: audio.play(Chess.MOVE) if e else None
        )

        self.settings.ok.clicked.connect(self.accepted)
        self.settings.loads()

        self.game_signal.settings.connect(self.settings.show)

        self.board.csize = 80
        self.board.callback = self.board_callback
        self.resize(self.board.csize * Chess.W, self.board.csize * Chess.H)

        self.game_signal.hint.connect(self.hint)
        self.game_signal.undo.connect(self.undo)
        self.game_signal.redo.connect(self.redo)
        self.game_signal.reset.connect(self.reset)
        self.game_signal.debug.connect(self.debug)

        self.game_signal.load.connect(self.load)
        self.game_signal.save.connect(self.save)

        self.game_signal.move.connect(self.play)

        self.game_signal.checkmate.connect(self.checkmateMessage)

        self.game_signal.animate.connect(self.animate)

        self.engine_side = [Chess.BLACK]
        self.human_side = [Chess.RED]

        self.game_signal.arrange.connect(self.arrange)
        self.board.signal.finish.connect(self.finish_arrange)

        audio.init()
        self.reset()

        self.toast = Toast(self)

        self.comments = Comments(self)
        self.comments.setWindowIcon(QtGui.QIcon(self.board.FAVICON))
        # self.signal.comments.connect()
        self.game_signal.comments.connect(lambda: [self.comments.refresh(self.engine), self.comments.show()])
        self.game_signal.undo.connect(lambda: self.comments.refresh(self.engine))
        self.game_signal.redo.connect(lambda: self.comments.refresh(self.engine))
        self.game_signal.move.connect(lambda: self.comments.refresh(self.engine))
        self.comments.ui.comments.currentItemChanged.connect(self.comments_changed)
        self.comments.refresh(self.engine)

        self.accepted()

    def show_context_menu(self, point):
        if self.board.arranging:
            return self.board.arrange_menu.exec_(self.mapToGlobal(point))
        self.game_menu.exec_(self.mapToGlobal(point))

    def update_action_state(self):
        if len(self.engine_side) == 2:
            self.game_menu.setAllMenuEnabled(False)
            self.game_menu.setAllShortcutEnabled(False)
        elif self.thinking:
            self.game_menu.setAllMenuEnabled(False)
            self.game_menu.setAllShortcutEnabled(False)
        else:
            self.game_menu.setAllMenuEnabled(True)
            self.game_menu.setAllShortcutEnabled(True)

    def set_thinking(self, thinking):
        self.thinking = thinking
        logger.debug("set thinking %s", self.thinking)
        if len(self.engine_side) == 2:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)
        elif self.thinking:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)
        else:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
        self.update_action_state()

    def arrange(self):
        self.board.arranging = True
        self.board.setBoard(self.board.board)
        self.board.setCheck(None)
        self.game_menu.setAllShortcutEnabled(False)

    def finish_arrange(self, finished):
        if not finished:
            return
        logger.debug('finish arrange')
        self.engine.close()
        self.engine = UCCIEngine(filename=self.ELEEYE, callback=self.engine_callback)
        self.engine.start()

        self.engine.sit.board = self.board.board
        self.engine.sit.turn = self.board.first_side
        self.engine.sit.fen = self.engine.sit.format_current_fen()
        self.try_engine_move()
        self.game_menu.setAllShortcutEnabled(True)

    def comments_changed(self, item: QtWidgets.QListWidgetItem):
        index = self.comments.ui.comments.indexFromItem(item).row()
        self.engine.set_index(index)
        if self.board.animate.state() == QtCore.QAbstractAnimation.State.Running:
            return
        self.updateBoard()

    def accepted(self):
        logger.info("setting accepted....")

        # 设置棋手或AI
        self.engine_side = []
        self.human_side = []

        if self.settings.redside.currentIndex() == 0:
            self.human_side.append(Chess.RED)
        else:
            self.engine_side.append(Chess.RED)

        if self.settings.blackside.currentIndex() == 0:
            self.engine_side.append(Chess.BLACK)
        else:
            self.human_side.append(Chess.BLACK)

        if len(self.engine_side) == 2:
            self.comments.ui.comments.setEnabled(False)
        else:
            self.comments.ui.comments.setEnabled(True)
        self.update_action_state()

        self.try_engine_move()

    def try_engine_move(self):
        if self.engine.sit.turn not in self.engine_side:
            return
        self.game_signal.thinking.emit(True)
        if self.engine.sit.turn == Chess.RED:
            self.engine.go(depth=self.settings.red_depth.value())
        else:
            self.engine.go(depth=self.settings.black_depth.value())

    @QtCore.Slot(int)
    def play(self, audio_type):
        if not self.settings.audio.isChecked():
            return
        audio.play(audio_type)

    def reset(self):
        if hasattr(self, 'engine'):
            self.engine.close()

        self.engine = UCCIEngine(filename=self.ELEEYE, callback=self.engine_callback)
        self.engine.start()

        self.fpos = None
        self.board.arranging = False
        self.thinking = False
        self.game_signal.move.emit(Chess.NEWGAME)

        self.updateBoard()
        self.board.setCheck(None)
        self.try_engine_move()

    @QtCore.Slot(None)
    def undo(self):
        for _ in range(2):
            self.engine.undo()
            if self.engine.sit.turn in self.human_side:
                break

        self.updateBoard()

    @QtCore.Slot(None)
    def redo(self):
        for _ in range(2):
            self.engine.redo()
            logger.debug('engine redo result %d', self.engine.sit.result)
            self.game_signal.move.emit(self.engine.sit.result)
            if self.engine.sit.turn in self.human_side:
                break

        self.updateBoard()

    @QtCore.Slot(bool)
    def hint(self):
        if self.thinking:
            logger.debug('engine is thinking hint ignored...')
            return
        self.game_signal.thinking.emit(True)
        if self.engine.sit.turn == Chess.RED:
            self.engine.go(depth=self.settings.red_depth.value())
        else:
            self.engine.go(depth=self.settings.black_depth.value())

    @QtCore.Slot(None)
    def debug(self):
        logger.debug("debug slot.....")
        # logger.debug(self.engine.sit.format_fen())

    @QtCore.Slot(None)
    def save(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filename = dialog.getSaveFileName(
            self, "保存中国象棋文件 Fen", ".", "文件 (*.fen)")[0]
        if not filename:
            return
        fen = self.engine.sit.format_fen()
        with open(filename, 'w', encoding='utf8') as file:
            file.write(fen)
        logger.info("save file %s - fen %s", filename, fen)

    @QtCore.Slot(None)
    def load(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filename = dialog.getOpenFileName(
            self, "打开中国象棋文件 Fen", ".", "fen 文件 (*.fen);;txt 文件 (*.txt)")[0]
        if not filename:
            return
        with open(filename, 'r', encoding='utf8') as file:
            content = file.read()

        if filename.endswith('.txt'):
            manual = Manual()
            try:
                manual.callback = lambda fpos, tpos: self.board.setBoard(
                    manual.sit.board,
                    manual.sit.fpos,
                    manual.sit.tpos
                )
                manual.parse(content)
            except Exception as e:
                self.toast.message(str(e))
                return
            fen = manual.sit.format_fen()
        else:
            fen = content

        self.engine.index = 0
        self.engine.stack = self.engine.stack[:1]
        self.engine.sit = self.engine.stack[0]

        if self.engine.sit.parse_fen(fen, load=True):
            moves = self.engine.sit.moves
            self.engine.sit.moves = []
            for fpos, tpos in moves:
                result = self.engine.move(fpos, tpos)
                if result == Chess.CHECKMATE:
                    self.game_signal.checkmate.emit()
                    break
            self.updateBoard()
        else:
            self.toast.message("加载文件失败")

    @QtCore.Slot(tuple, tuple)
    def animate(self, fpos, tpos):
        self.board.move(self.engine.sit.board, fpos, tpos, self.updateBoard)

    def move(self, fpos, tpos):
        self.game_signal.thinking.emit(False)
        if self.engine.checkmate:
            self.game_signal.checkmate.emit()
            return

        result = self.engine.move(fpos, tpos)
        logger.debug('move result %s', result)
        if not result:
            return

        if result != Chess.INVALID:
            self.game_signal.animate.emit(fpos, tpos)

        if self.engine.sit.check:
            self.board.setCheck(self.engine.sit.check)
            logger.debug('check ... %s', self.engine.sit.check)
        else:
            self.board.setCheck(None)

        self.game_signal.move.emit(result)

        if result == Chess.CHECKMATE:
            logger.debug("emit checkmate")
            self.game_signal.checkmate.emit()
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
            self.toast.message("黑方胜!!!")
            # QtWidgets.QMessageBox(self).warning(self, '信息', '')
        else:
            self.toast.message("红方胜!!!")
            # QtWidgets.QMessageBox(self).information(self, '信息', '红方胜!!!')

    def engine_callback(self, move_type, fpos, tpos):
        time.sleep(self.settings.delay.value() / 1000)
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

    # import qt_material as material
    # extra = {
    #     'font_family': "dengxian SumHei"
    # }
    # material.apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True, extra=extra)

    window = Game()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
