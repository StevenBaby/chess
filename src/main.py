# coding=utf-8

import sys
import time
from functools import partial
import threading

import numpy as np

import keyboard

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from board import BoardFrame

from engine import Engine
from engine import UCCIEngine
from engine import Chess
from engine import dirpath
from engine import logger
from engines import UCCI_ENGINES
from situation import Situation

import audio
import engines
import system
from version import VERSION

from dialogs.settings import SettingsDialog
from dialogs.method import MethodDialog
from toast import Toast

from context import BaseContextMenu
from context import BaseContextMenuMixin

from arrange import ArrangeBoard
from manual import Manual
import qqchess


class GameSignal(QtCore.QObject):

    hint = QtCore.Signal(None)
    undo = QtCore.Signal(None)
    redo = QtCore.Signal(None)
    reset = QtCore.Signal(None)
    debug = QtCore.Signal(None)

    load = QtCore.Signal(None)
    save = QtCore.Signal(None)
    paste = QtCore.Signal(None)
    capture = QtCore.Signal(None)
    connecting = QtCore.Signal(None)

    move = QtCore.Signal(int)
    draw = QtCore.Signal(None)
    resign = QtCore.Signal(None)
    checkmate = QtCore.Signal(None)
    nobestmove = QtCore.Signal(None)

    animate = QtCore.Signal(tuple, tuple)
    settings = QtCore.Signal(None)
    method = QtCore.Signal(None)
    arrange = QtCore.Signal(None)
    thinking = QtCore.Signal(bool)
    reverse = QtCore.Signal(None)


class GameContextMenu(BaseContextMenu):

    items = [
        ('提示', 'Ctrl+H', lambda self: self.signal.hint.emit(), True),
        ('悔棋', 'Ctrl+Z', lambda self: self.signal.undo.emit(), True),
        ('重走', 'Ctrl+Shift+Z', lambda self: self.signal.redo.emit(), True),
        'separator',
        ('重置', 'Ctrl+N', lambda self: self.signal.reset.emit(), False),
        ('布局', 'Ctrl+A', lambda self: self.signal.arrange.emit(), True),
        ('着法', 'Ctrl+M', lambda self: self.signal.method.emit(), False),
        ('反转', 'Ctrl+I', lambda self: self.signal.reverse.emit(), False),
        'separator',
        ('粘贴', 'Ctrl+V', lambda self: self.signal.paste.emit(), True),
        ('载入', 'Ctrl+O', lambda self: self.signal.load.emit(), True),
        ('保存', 'Ctrl+S', lambda self: self.signal.save.emit(), True),
        ('截屏', 'Ctrl+K', lambda self: self.signal.capture.emit(), True),
        ('连线', 'Ctrl+L', lambda self: self.signal.connecting.emit(), True),
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


class Game(BoardFrame, BaseContextMenuMixin):

    def __init__(self, parent=None):
        super().__init__(parent, board_class=ArrangeBoard)
        self.setWindowTitle(f"中国象棋 v{VERSION}")
        self.setupContextMenu()

        audio.init()

        self.image = None

        self.engine = None
        self.engines = {
            Chess.RED: None,
            Chess.BLACK: None,
        }

        self.engine_side = [Chess.BLACK]
        self.human_side = [Chess.RED]

        self.board.csize = 80
        self.board.callback = self.board_callback
        self.resize(self.board.csize * Chess.W, self.board.csize * Chess.H)

        self.game_signal = GameSignal()

        self.method = MethodDialog(self)
        self.method.setWindowIcon(QtGui.QIcon(self.board.FAVICON))

        self.settings = SettingsDialog(self)
        self.settings.setWindowIcon(QtGui.QIcon(self.board.FAVICON))

        self.game_menu = GameContextMenu(self, self.game_signal)

        self.toast = Toast(self)

        # 以下初始化信号

        keyboard.add_hotkey(
            'ctrl+alt+z', lambda: self.game_signal.capture.emit())
        keyboard.add_hotkey(
            'ctrl+alt+x', lambda: self.game_signal.hint.emit())
        keyboard.add_hotkey(
            'ctrl+alt+m', lambda: self.game_signal.method.emit())
        keyboard.add_hotkey(
            'ctrl+alt+l', lambda: self.game_signal.connecting.emit())

        self.game_signal.reverse.connect(self.reverse)
        self.game_signal.thinking.connect(self.set_thinking)
        self.game_signal.settings.connect(self.settings.show)
        self.game_signal.hint.connect(self.hint)
        self.game_signal.undo.connect(self.undo)
        self.game_signal.redo.connect(self.redo)
        self.game_signal.reset.connect(self.reset)
        self.game_signal.debug.connect(self.debug)

        self.game_signal.load.connect(self.load)
        self.game_signal.save.connect(self.save)
        self.game_signal.paste.connect(self.paste)
        self.game_signal.capture.connect(self.capture)

        self.game_signal.move.connect(self.play)

        self.game_signal.checkmate.connect(self.checkmateMessage)
        self.game_signal.checkmate.connect(lambda: self.set_thinking(False))

        self.game_signal.nobestmove.connect(self.nobestmove)

        self.game_signal.draw.connect(lambda: self.toast.message('和棋！！！'))
        self.game_signal.resign.connect(lambda: self.toast.message('认输了！！！'))

        self.game_signal.animate.connect(self.animate)

        self.settings.transprancy.valueChanged.connect(
            lambda e: self.setWindowOpacity((100 - e) / 100)
        )

        self.settings.reverse.stateChanged.connect(
            lambda e: self.board.setReverse(self.settings.reverse.isChecked())
        )

        self.settings.audio.stateChanged.connect(
            lambda e: audio.play(Chess.MOVE) if e else None
        )

        self.settings.standard_method.stateChanged.connect(
            lambda e: self.method.set_standard(e)
        )

        self.settings.ontop.clicked.connect(self.set_on_top)

        self.settings.ok.clicked.connect(self.accepted)
        self.settings.loads()

        self.game_signal.arrange.connect(self.arrange)
        self.board.signal.finish.connect(self.finish_arrange)

        self.game_signal.method.connect(
            lambda: self.method.setVisible(
                not self.method.isVisible()))
        self.method.list.currentItemChanged.connect(self.method_changed)

        self.game_signal.connecting.connect(self.connecting)
        # self.qqboard = qqchess.Capturer(self)
        # logger.info("set qqboard %s", self.settings.qqboard)
        # self.qqboard.setGeometry(*self.settings.qqboard)
        # self.qqboard.signal.capture.connect(self.capture_image)

        self.reset()
        self.accepted()
        self.check_openfile()

    def set_on_top(self):
        logger.info("set on top")
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def check_openfile(self):
        # 直接打开棋谱文件
        if len(sys.argv) > 1:
            with open(sys.argv[1], encoding='utf8') as file:
                content = file.read()
            self.pasre_content(content)

    def show_context_menu(self, point):
        if self.board.arranging:
            return self.board.arrange_menu.exec_(self.mapToGlobal(point))
        self.game_menu.exec(self.mapToGlobal(point))

    def update_action_state(self):
        if len(self.engine_side) == 2 and not self.engine.checkmate:
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
        if len(self.engine_side) == 2 and not self.engine.checkmate:
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
        self.engine = Engine()

        self.engine.sit.board = self.board.board
        self.engine.sit.turn = self.board.first_side
        self.engine.sit.fen = self.engine.sit.format_current_fen()
        self.try_engine_move()
        self.game_menu.setAllShortcutEnabled(True)

    def method_changed(self, item: QtWidgets.QListWidgetItem):
        index = self.method.list.indexFromItem(item).row()
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

        idx = self.settings.red_engine.currentIndex()
        engine = self.engines[Chess.RED]
        if not isinstance(engine, UCCI_ENGINES[idx]):
            self.init_engines(Chess.RED)

        idx = self.settings.black_engine.currentIndex()
        engine = self.engines[Chess.BLACK]
        if not isinstance(engine, UCCI_ENGINES[idx]):
            self.init_engines(Chess.BLACK)

        if len(self.engine_side) == 2:
            self.method.list.setEnabled(False)
        else:
            self.method.list.setEnabled(True)
        self.update_action_state()

        self.try_engine_move()

    def try_engine_move(self):
        if self.engine.sit.turn not in self.engine_side:
            return
        self.go()

    def go(self):
        if self.engine.checkmate:
            self.game_signal.checkmate.emit()
            logger.debug('engine is checkmated hint ignored...')
            return
        self.game_signal.thinking.emit(True)
        engine = self.current_engine()
        engine.position(self.engine.sit.format_fen())

        params = self.settings.get_params(self.engine.sit.turn)
        engine.go(**params)

    def nobestmove(self):
        if self.engine.sit.turn == Chess.RED:
            side = '黑方'
        else:
            side = '红方'
        logger.debug('nobestmove')
        self.toast.message(f"{side}行棋违例！")

    @QtCore.Slot(int)
    def play(self, audio_type):
        if not self.settings.audio.isChecked():
            return
        audio.play(audio_type)

    def init_engines(self, turn=None):
        turns = []
        if turn == Chess.RED:
            turns = [Chess.RED]
        elif turn == Chess.BLACK:
            turns = [Chess.BLACK]
        else:
            turns = [Chess.RED, Chess.BLACK]
        for turn in turns:
            old = self.engines[turn]
            if old:
                old.close()
            idx = self.settings.get_engine_box(turn).currentIndex()
            new = UCCI_ENGINES[idx](callback=self.engine_callback)
            new.start()
            self.engines[turn] = new

    def current_engine(self) -> Engine:
        return self.engines[self.engine.sit.turn]

    def reverse(self):
        logger.debug("reverse")
        check = self.settings.reverse.isChecked()
        self.settings.reverse.setChecked(not check)
        self.settings.save()

    def reset(self):
        self.init_engines()

        self.engine = Engine()

        self.connected = False
        self.connect_inited = False

        self.fpos = None
        self.board.arranging = False
        self.thinking = False
        self.game_signal.move.emit(Chess.NEWGAME)

        self.updateBoard()
        self.board.setCheck(None)
        self.try_engine_move()

        self.method.refresh(self.engine)

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
            if self.engine.checkmate:
                self.game_signal.checkmate.emit()
            if self.engine.sit.turn in self.human_side:
                break

        self.updateBoard()

    @QtCore.Slot(bool)
    def hint(self):
        if self.thinking:
            logger.debug('engine is thinking hint ignored...')
            return
        self.go()

    @QtCore.Slot(None)
    def debug(self):
        logger.debug("debug slot.....")
        qqchess.show(self.image)
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
            file.write('fen ')
            file.write(fen)
        logger.info("save file %s - fen %s", filename, fen)

    def pasre_content(self, content: str):
        if not content.startswith('fen '):
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
            fen = content[4:]

        self.engine.index = 0
        self.engine.stack = self.engine.stack[:1]
        self.engine.sit = self.engine.stack[0]
        self.updateBoard()
        self.board.setCheck(None)

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
            self.toast.message("加载棋谱失败")

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
        self.pasre_content(content)

    def paste(self):
        content = QtWidgets.QApplication.clipboard().text()
        logger.debug('Clipboard text %s', content)
        if content:
            self.pasre_content(content)
            return

        image = qqchess.ImageGrab.grabclipboard()
        if isinstance(image, qqchess.Image.Image):
            self.paste_image(image)

    def capture(self):
        logger.debug("capture...")
        colors = {0: Chess.RMASK, 1: Chess.BMASK}
        board = np.zeros((9, 10), dtype=np.int8)
        while True:
            pred = qqchess.classifier.get_board()
            board0 = board
            board = np.zeros((9, 10), dtype=np.int8)
            for loc, idx in pred.items():
                board[loc] = (idx[0] + 1) | colors[idx[1]]
            if np.all(board0 == board):
                break

        # 验证数量
        C = Chess
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

        wheres = np.argwhere(board == Chess.K)

        turn = Chess.RED
        self.settings.reverse.setChecked(False)
        if wheres[0][1] < 3:
            logger.debug("reversed")
            board = board[::-1, ::-1]
            self.settings.reverse.setChecked(True)
            turn = Chess.BLACK

        if turn == Chess.RED and self.settings.redside.currentIndex() != 1:
            self.settings.redside.setCurrentIndex(1)
            self.settings.blackside.setCurrentIndex(1)
            self.accepted()
        if turn == Chess.BLACK and self.settings.redside.currentIndex() != 0:
            self.settings.redside.setCurrentIndex(0)
            self.settings.blackside.setCurrentIndex(0)
            self.accepted()

        wheres = np.argwhere((board - self.engine.sit.board) != 0)
        # logger.debug("wheres %s", wheres)
        if len(wheres) == 0:
            return

        if len(wheres) == 2:
            pos1 = tuple(wheres[0])
            pos2 = tuple(wheres[1])
            if board[pos1] != 0 and board[pos2] != 0:
                return

            assert (board[pos1] == 0 or board[pos2] == 0)
            assert (board[pos1] != 0 or board[pos2] != 0)
            if board[pos1] == 0:
                fpos = pos1
                tpos = pos2
            else:
                fpos = pos2
                tpos = pos1
            if Chess.color(board[tpos]) != turn:
                self.move(fpos, tpos)
        elif not self.connect_inited:
            logger.info("reset engine situation")
            # self.engine.close()
            # self.engine = Engine()
            self.engine.index = 0
            self.engine.sit = Situation(board, turn=turn)
            self.engine.stack = [self.engine.sit]
            self.fpos = None

            self.updateBoard()
            self.try_engine_move()
            self.connect_inited = True

    @QtCore.Slot(tuple, tuple)
    def animate(self, fpos, tpos):
        self.board.move(
            self.engine.sit.board, fpos, tpos,
            self.updateBoard,
            self.settings.ui.animate.isChecked(),
        )

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
        else:
            return

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
        if hasattr(self, 'method'):
            self.method.signal.refresh.emit()
        self.board.setBoard(
            self.engine.sit.board,
            self.engine.sit.fpos,
            self.engine.sit.tpos
        )

    @QtCore.Slot(None)
    def checkmateMessage(self):
        if not self.engine.checkmate:
            return
        self.connected = False
        self.connect_inited = False

        if self.engine.sit.turn == Chess.RED:
            self.toast.message("黑方胜!!!")
            # QtWidgets.QMessageBox(self).warning(self, '信息', '')
        else:
            self.toast.message("红方胜!!!")
            # QtWidgets.QMessageBox(self).information(self, '信息', '红方胜!!!')

    def engine_callback(self, type, data):
        if type == Chess.MOVE:
            time.sleep(self.settings.delay.value() / 1000)
            self.move(data[0], data[1])
        elif type == Chess.INFO:
            logger.debug(data)
        elif type == Chess.POPHASH:
            logger.debug(data)
        elif type == Chess.DRAW:
            self.game_signal.draw.emit()
        elif type == Chess.RESIGN:
            self.game_signal.resign.emit()
        elif type == Chess.CHECKMATE:
            pass
            # self.game_signal.checkmate.emit()
        elif type == Chess.NOBESTMOVE:
            self.game_signal.nobestmove.emit()

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

    def connecting(self):
        self.connected = not self.connected
        if not self.connected:
            if hasattr(self, 'connect_task'):
                self.connect_task.join()
            return

        def task():
            while self.connected:
                self.game_signal.capture.emit()
                logger.debug('connecting... task')
                time.sleep(2)

        self.connect_task = threading.Thread(target=task, daemon=True)
        self.connect_task.start()


def main():
    app = QtWidgets.QApplication(sys.argv)

    # import qt_material as material
    # extra = {
    #     'font_family': "dengxian SumHei"
    # }
    # material.apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True, extra=extra)

    window = Game()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
