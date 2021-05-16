# coding=utf-8
import os
import sys
import subprocess
import time
import threading
import queue
import pygame
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


class attrdict(dict):

    '''
    Use dict key as attribute if available
    '''

    def __init__(self, *args, **kwargs):
        super(attrdict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    @classmethod
    def loads(cls, value):
        if isinstance(value, dict):
            result = cls()
            result.update(value)
            for k, v in result.items():
                result[k] = cls.loads(v)

        elif isinstance(value, list):
            for index, item in enumerate(value):
                if type(item) in (list, dict):
                    value[index] = cls.loads(item)
            result = value
        else:
            result = value
        return result

    @classmethod
    def json_loads(cls, value):
        import json
        data = json.loads(value)
        return cls.loads(data)


class Chess(object):

    NONE = 0
    RED = 1
    BLACK = -1

    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    ADVISOR = 5
    CANNON = 6
    KING = 7

    WIDTH = 9
    HEIGHT = 10
    W = WIDTH
    H = HEIGHT


class Engine(threading.Thread):

    engine_file = os.path.join(dirname, 'engines/eleeye/eleeye.exe')

    SETUP = 0
    READY = 1

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = False
        self.moves = queue.Queue()
        self.ids = []
        self.options = []
        self.last_fen = None

        self.state = self.SETUP

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.pipe = subprocess.Popen(
            [self.engine_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo
        )

        time.sleep(0.5)

        self.stdin = self.pipe.stdin
        self.stdout = self.pipe.stdout
        self.start()

        self.send_command('ucci')

    def run(self):
        self.running = True
        while self.running:
            output = self.stdout.readline().strip().decode("utf-8")
            logger.info(output)
            self.deal_message(output)

    def get_pos(self, move):
        assert(len(move) == 4)
        fpos = (ord(move[0]) - ord('a'), 9 - int(move[1]))
        tpos = (ord(move[2]) - ord('a'), 9 - int(move[3]))
        return [fpos, tpos]

    def deal_message(self, output):
        if not output:
            return
        if output in ['bye', '']:
            self.close()
            return False

        items = output.split()
        action = items[0]
        if self.state == self.SETUP:
            if action == 'ucciok':
                self.state = self.READY
            return

        assert(self.state == self.READY)
        move = attrdict()
        move.action = action
        move.message = output
        move.fen = self.last_fen

        if action == 'bestmove':
            if items[1] in ['null', 'resign']:
                move.action = 'dead'
            elif items[1] == 'draw':
                move.action = 'draw'
            else:
                if len(items) > 2:
                    move.ponder = self.get_pos(items[3])
                move.move = self.get_pos(items[1])

        self.moves.put(move)

    def send_command(self, cmd):
        try:
            bytes = f'{cmd}\n'.encode('utf-8')
            self.stdin.write(bytes)
            self.stdin.flush()
        except IOError as e:
            logger.error("send command error %s", e)

    def go_from(self, fen, depth=7):
        self.send_command(f'position fen {fen}')
        self.last_fen = fen
        self.send_command(f'go depth {depth}')
        time.sleep(0.3)

    def stop_thinking(self):
        self.send_command("stop")
        while True:
            try:
                output = self.outlines.get_nowait()
            except queue.Empty:
                continue
            items = output.split()
            action = items[0]
            if action in ['bestmove', 'nobestmove']:
                return

    def close(self):
        self.send_command("quit")
        self.pipe.kill()


class Game(Chess):

    ORIGIN = {
        (0, 0): Chess.BLACK * Chess.ROOK,
        (1, 0): Chess.BLACK * Chess.KNIGHT,
        (2, 0): Chess.BLACK * Chess.BISHOP,
        (3, 0): Chess.BLACK * Chess.ADVISOR,
        (4, 0): Chess.BLACK * Chess.KING,
        (5, 0): Chess.BLACK * Chess.ADVISOR,
        (6, 0): Chess.BLACK * Chess.BISHOP,
        (7, 0): Chess.BLACK * Chess.KNIGHT,
        (8, 0): Chess.BLACK * Chess.ROOK,

        (1, 2): Chess.BLACK * Chess.CANNON,
        (7, 2): Chess.BLACK * Chess.CANNON,

        (0, 3): Chess.BLACK * Chess.PAWN,
        (2, 3): Chess.BLACK * Chess.PAWN,
        (4, 3): Chess.BLACK * Chess.PAWN,
        (6, 3): Chess.BLACK * Chess.PAWN,
        (8, 3): Chess.BLACK * Chess.PAWN,

        (0, 9): Chess.RED * Chess.ROOK,
        (1, 9): Chess.RED * Chess.KNIGHT,
        (2, 9): Chess.RED * Chess.BISHOP,
        (3, 9): Chess.RED * Chess.ADVISOR,
        (4, 9): Chess.RED * Chess.KING,
        (5, 9): Chess.RED * Chess.ADVISOR,
        (6, 9): Chess.RED * Chess.BISHOP,
        (7, 9): Chess.RED * Chess.KNIGHT,
        (8, 9): Chess.RED * Chess.ROOK,

        (1, 7): Chess.RED * Chess.CANNON,
        (7, 7): Chess.RED * Chess.CANNON,

        (0, 6): Chess.RED * Chess.PAWN,
        (2, 6): Chess.RED * Chess.PAWN,
        (4, 6): Chess.RED * Chess.PAWN,
        (6, 6): Chess.RED * Chess.PAWN,
        (8, 6): Chess.RED * Chess.PAWN,
    }

    FEN = {
        Chess.ROOK: 'R',
        Chess.KNIGHT: 'N',
        Chess.BISHOP: 'B',
        Chess.ADVISOR: 'A',
        Chess.KING: 'K',
        Chess.CANNON: 'C',
        Chess.PAWN: 'P',
    }

    def __init__(self):
        self.board = mat(zeros((Chess.W, Chess.H)), dtype=int)
        self.turn = Chess.RED
        self.bout = 1
        self.draw = 0  # 没有吃子的回合数

        for pos, chess in self.ORIGIN.items():
            self.board[pos] = chess

        self.engine = Engine()

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

    def validate_knight(self, fpos, tpos, chess, color, offset):
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

    def validate_advisor(self, fpos, tpos, chess, color, offset):
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
        elif chess == Chess.KNIGHT:
            return self.validate_knight(fpos, tpos, chess, color, offset)
        elif chess == Chess.BISHOP:
            return self.validate_bishop(fpos, tpos, chess, color, offset)
        elif chess == Chess.ADVISOR:
            return self.validate_advisor(fpos, tpos, chess, color, offset)
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

        if self.board[tpos]:
            self.draw += 1
        else:
            self.draw = 0

        self.board[tpos] = self.board[fpos]
        self.board[fpos] = Chess.NONE
        self.turn *= -1
        if self.turn == Chess.RED:
            self.bout += 1

        return True

    def get_fen(self):
        lines = []
        for y in range(Chess.H):
            blank = 0
            slot = []
            for x in range(Chess.W):
                pos = (x, y)
                chess = self.board[pos]
                if not chess:
                    blank += 1
                    continue
                if blank:
                    slot.append(str(blank))
                    blank = 0
                ctype = self.FEN[abs(chess)]
                color = np.sign(chess)
                if color < 0:
                    ctype = ctype.lower()
                slot.append(ctype)
            if blank:
                slot.append(str(blank))
                blank = 0

            line = ''.join(slot)
            lines.append(line)

        items = ['/'.join(lines)]
        if self.turn == Chess.RED:
            items.append('w')
        else:
            items.append('b')

        items.extend(['-', '-', str(self.draw), str(self.bout)])

        result = ' '.join(items)

        return result

    def set_fen(self):
        pass


class Board(QLabel):

    flags = QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint

    BOARD = os.path.join(dirname, u"images/board.png")
    MARK = os.path.join(dirname, 'images/mark.png')
    ROOK1 = os.path.join(dirname, 'images/black_rook.png')

    IMAGES = {
        Chess.RED: {
            Chess.ROOK: os.path.join(dirname, 'images/red_rook.png'),
            Chess.KNIGHT: os.path.join(dirname, 'images/red_horse.png'),
            Chess.BISHOP: os.path.join(dirname, 'images/red_bishop.png'),
            Chess.ADVISOR: os.path.join(dirname, 'images/red_knight.png'),
            Chess.KING: os.path.join(dirname, 'images/red_king.png'),
            Chess.CANNON: os.path.join(dirname, 'images/red_cannon.png'),
            Chess.PAWN: os.path.join(dirname, 'images/red_pawn.png'),
        },
        Chess.BLACK: {
            Chess.ROOK: os.path.join(dirname, 'images/black_rook.png'),
            Chess.KNIGHT: os.path.join(dirname, 'images/black_horse.png'),
            Chess.BISHOP: os.path.join(dirname, 'images/black_bishop.png'),
            Chess.ADVISOR: os.path.join(dirname, 'images/black_knight.png'),
            Chess.KING: os.path.join(dirname, 'images/black_king.png'),
            Chess.CANNON: os.path.join(dirname, 'images/black_cannon.png'),
            Chess.PAWN: os.path.join(dirname, 'images/black_pawn.png'),
        }
    }

    AUDIO_MOVE = os.path.join(dirname, 'audios/move.wav')
    AUDIO_CAPTURE = os.path.join(dirname, 'audios/capture.wav')
    AUDIO_CHECK = os.path.join(dirname, 'audios/check.wav')

    def __init__(self, parent):
        super().__init__(parent)
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

        pygame.mixer.init()

        self.choice = None

    def setBoardImage(self):
        self.setPixmap(QtGui.QPixmap(self.BOARD))

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

        # self.play(self.AUDIO_MOVE)
        self.choice = pos
        self.mark1.setGeometry(self.getChessGeometry(pos))
        self.mark1.setVisible(True)
        self.mark2.setVisible(False)

    def play(self, audio):
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()

    def closeEvent(self, event):
        self.game.engine.close()
        return super().closeEvent(event)

    def mousePressEvent(self, event):
        pos = self.getPosition(event)
        if not pos:
            return
        logger.debug("click %s", pos)
        self.clickPosition(pos)

    def clickPosition(self, pos):
        chess = self.game.board[pos]

        if not self.choice and not chess:
            return

        if not self.choice:
            self.setChoice(pos)
            return

        tchess = self.game.board[pos]

        if self.game.move(self.choice, pos):
            self.mark2.setGeometry(self.getChessGeometry(pos))
            self.mark2.setVisible(True)
            self.refresh()
            self.choice = None
            if not tchess:
                self.play(self.AUDIO_MOVE)
            else:
                self.play(self.AUDIO_CAPTURE)

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

    def hint(self):
        fen = self.game.get_fen()
        logger.debug(fen)
        self.game.engine.go_from(fen)
        while True:
            move = self.game.engine.moves.get()
            logger.debug(move)
            if move.action in ['bestmove', 'nobestmove']:
                break

        if move.action == 'bestmove':
            fpos = move.move[0]
            tpos = move.move[1]
            self.clickPosition(fpos)
            time.sleep(0.1)
            self.clickPosition(tpos)


class MainWindow(QtWidgets.QMainWindow):

    FAVICON = os.path.join(dirname, 'images/favicon.ico')

    def __init__(self):
        super().__init__()
        from ui import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.FAVICON))
        self.setWindowTitle(u"Chinese Chess")
        self.ui.board.setBoardImage()
        # self.resize(810, 900)

        self.ui.hint.clicked.connect(self.ui.board.hint)

    def resizeEvent(self, event):
        self.ui.board.resizeEvent(event)

    def closeEvent(self, event):
        self.ui.board.closeEvent(event)
        return super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
    # game = Game()
    # game.engine.close()


if __name__ == '__main__':
    main()
