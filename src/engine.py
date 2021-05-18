# coding=utf-8

import os
import sys
import subprocess
import threading
import time
import logging
import traceback
from pathlib import Path
import re
import queue
import copy

import numpy as np
from numpy import mat
from numpy import zeros

from attrdict import attrdict

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='[%(filename)s:%(lineno)d] %(levelname)s %(message)s',)
logger = logging.getLogger()

dirpath = Path(__file__).parent


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


class Queue(queue.Queue):

    mark = 'a3c63f6d-a880-4bde-a176-82af83bcf793'

    def __init__(self, maxsize=0):
        super().__init__(maxsize)
        self.condition = threading.Condition()

    def __enter__(self):
        self.condition.acquire()
        self.put(self.mark)
        self.condition.wait()

    def get(self, block=True, timeout=None):
        while True:
            line = super().get(block=block, timeout=timeout)
            if line != self.mark:
                return line
            with self.condition:
                self.condition.notify()
                self.condition.wait()
                continue

    def __exit__(self, exc_type, exc_value, traceback):
        self.condition.notify()
        self.condition.release()


class Engine(threading.Thread):

    ENGINE_BOOT = 0
    ENGINE_IDLE = 1
    ENGINE_BUSY = 2

    MOVE_BEST = 0  # 正常
    MOVE_DEAD = 1  # 将死
    MOVE_RESGIN = 2  # 认输
    MOVE_DRAW = 3  # 和棋

    MOVE_IDLE = 4
    MOVE_CAPTURE = 5

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

    def __init__(self, filename: Path):
        super().__init__(daemon=True)

        self.filename = Path(filename)
        self.dirname = str(filename.parent)
        self.pipe = None
        self.state = self.ENGINE_BOOT

        self.init_startpos()

        self.parser_thread = threading.Thread(target=self.parser, daemon=True)

        self.outlines = Queue()
        self.running = False
        self.setup()

    def init_startpos(self):
        self.board = mat(zeros((Chess.W, Chess.H)), dtype=int)
        self.fpos = None
        self.tpos = None

        self.turn = Chess.RED
        self.bout = 1  # 回合数
        self.idle = 0  # 没有吃子的半回合数
        self.steps = []

        for pos, chess in self.ORIGIN.items():
            self.board[pos] = chess

    def close(self):
        if self.pipe:
            self.pipe.terminate()

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

    def color(self, pos):
        return np.sign(self.board[pos])

    def move(self, fpos, tpos):
        if not self.validate(fpos, tpos):
            return False

        self.steps.append((copy.deepcopy(self.board), self.fpos, self.tpos, self.turn, self.idle, self.bout))

        self.fpos = fpos
        self.tpos = tpos

        if self.board[tpos]:
            self.idle = 0
        else:
            self.idle += 1

        if self.board[tpos]:
            result = self.MOVE_CAPTURE
        else:
            result = self.MOVE_IDLE

        self.board[tpos] = self.board[fpos]
        self.board[fpos] = Chess.NONE
        self.turn *= -1
        if self.turn == Chess.RED:
            self.bout += 1

        return result

    def unmove(self):
        if not self.steps:
            return
        self.board, self.fpos, self.tpos, self.turn, self.idle, self.bout = self.steps.pop()
        return True

    def parse_line(self, line: str):
        pass

    def run(self):
        self.running = True
        self.parser_thread.start()

        while self.running:
            line = self.readline()
            self.outlines.put(line)

    def parser(self):
        while True:
            line = self.outlines.get()
            try:
                self.parse_line(line)
            except Exception:
                logger.error(traceback.format_exc())

    def send_command(self, command):
        try:
            logger.info(command)
            line = f'{command}\n'.encode('utf8')
            self.stdin.write(line)
            self.stdin.flush()
        except IOError as e:
            logger.error("send command error %s", e)
            logger.error(traceback.format_exc())

    def readline(self):
        while True:
            try:
                line = self.stdout.readline().strip().decode('utf8')
                if not line:
                    continue
                logger.info(line)
                return line
            except Exception as e:
                logger.error(traceback.format_exc())
                continue

    def clear(self):
        with self.outlines:
            while True:
                try:
                    self.outlines.get_nowait()
                except queue.Empty:
                    return

    def setup(self):
        logger.info("open pipe %s", self.filename)

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.pipe = subprocess.Popen(
            [str(self.filename)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.dirname),
            startupinfo=startupinfo
        )
        self.stdin = self.pipe.stdin
        self.stdout = self.pipe.stdout
        self.stderr = self.pipe.stderr


class UCCIEngine(Engine):

    '''https://www.xqbase.com/protocol/cchess_ucci.htm'''

    FEN = {
        Chess.ROOK: 'R',
        Chess.KNIGHT: 'N',
        Chess.BISHOP: 'B',
        Chess.ADVISOR: 'A',
        Chess.KING: 'K',
        Chess.CANNON: 'C',
        Chess.PAWN: 'P',
    }

    FEN_CHESS = {value: key for key, value in FEN.items()}

    def __init__(self, filename, callback=None):
        self.ids = attrdict()
        self.options = attrdict()
        self.fen = 'startpos'
        self.moves = []
        self.callback = callback
        super().__init__(filename)

    def setup(self):
        super().setup()
        self.send_command('ucci')

        while True:
            line = self.readline()
            try:
                self.parse_line(line)
            except Exception:
                logger.error(traceback.format_exc())
            if self.state == self.ENGINE_IDLE:
                break

    def parse_option(self, message: str):
        message = re.sub(' +', ' ', message)
        items = message.split()
        option = attrdict()

        key = None
        for var in items:
            if var in {'type', 'min', 'max', 'var', 'default'}:
                key = var
                continue
            elif not key:
                continue
            elif key == 'var':
                option.setdefault('vars', [])
                option.vars.append(var)
                continue
            else:
                option[key] = var
            if key == 'default':
                option.value = var
            key = None
        return option

    def set_option(self, option, value):
        if option not in self.options:
            logger.warning("option %s not supported!!!", option)
            return
        self.options[option].value = value
        command = f'setoption {option} {value}'
        self.send_command(command)

    def position(self, fen=None, moves=None):
        if fen and not self.parse_fen(fen, moves):
            return

        if self.turn == Chess.RED:
            turn = 'w'
        else:
            turn = 'b'

        fen = ' '.join([self.fen, turn, '-', '-', str(self.idle), str(self.bout)])

        command = f'position {fen}'
        if self.moves:
            command += f' moves {" ".join(self.moves)}'

        self.send_command(command)

    def move(self, fpos, tpos):
        result = super().move(fpos, tpos)
        if not result:
            return result

        move = self.format_move(fpos, tpos)
        self.moves.append(move)
        self.position()
        return result

    def unmove(self):
        if super().unmove():
            self.moves.pop()
            self.position()
            return True

    def banmoves(self, moves: list):
        if not moves:
            return
        command = f'banmoves {" ".join(moves)}'
        self.send_command(command)

    def go(self, depth=3, nodes=None,
           time=None, increment=None,
           opptime=None, oppmovetogo=None, oppincrement=None,
           draw=None, ponder=None):
        command = "go"
        if draw:
            command += ' draw'
        elif ponder:
            command += ' ponder'

        if depth:
            command += f' depth {depth}'
        elif nodes:
            command += f' nodes {depth}'
        elif time:
            command += f' time {time}'
            if increment:
                command += f'increment {increment}'
            elif opptime:
                command += f'opptime {opptime}'
            elif oppmovetogo:
                command += f'oppmovetogo {oppmovetogo}'
            elif oppincrement:
                command += f'oppincrement {oppincrement}'

        self.send_command(command)
        self.state = self.ENGINE_BUSY

    def ponderhit(self, draw=False):
        var = ''
        if draw:
            var = 'draw'
        command = f"ponderhint {var}"
        self.send_command(command)

    def probe(self, fen, moves=None):
        if not moves:
            moves = []
        command = f'probe {fen} moves {" ".join(moves)}'
        self.send_command(command)

    def pophash(self, line):
        pass

    def stop(self):
        self.send_command('stop')

    def isready(self):
        self.clear()
        self.send_command("isready")
        with self.outlines:
            line = self.outlines.get()
            if line == 'readyok':
                return True
            return False

    def parse_pos(self, move):
        fpos = (ord(move[0]) - ord('a'), 9 - int(move[1]))
        tpos = (ord(move[2]) - ord('a'), 9 - int(move[3]))
        return [fpos, tpos]

    def format_move(self, fpos, tpos):
        v1 = chr(fpos[0] + ord('a'))
        v2 = 9 - fpos[1]
        v3 = chr(tpos[0] + ord('a'))
        v4 = 9 - tpos[1]
        return ''.join([v1, str(v2), v3, str(v4)])

    def parse_line(self, line: str):
        items = line.split(maxsplit=1)
        instruct = items[0]
        if instruct == 'bye':
            self.running = False

        if instruct in ['readyok', 'bye']:
            return

        if instruct == 'ucciok':
            self.state = self.ENGINE_IDLE
            return

        if instruct in {'id', 'option', 'info', 'pophash', 'bestmove'}:
            tup = items[1].split(maxsplit=1)
            if instruct == 'id':
                self.ids[tup[0]] = tup[1]
                return
            if instruct == 'option':
                self.options[tup[0]] = self.parse_option(tup[1])
                return

            if instruct == 'info':
                # TODO info
                return
            if instruct == 'pophash':
                # TODO pophash
                return

        self.state = self.ENGINE_IDLE

        move = attrdict()

        if instruct == 'bestmove':
            move.type = self.MOVE_BEST
            moves = items[1].split()
            move.fpos, move.tpos = self.parse_pos(moves[0])
            if len(items) > 2:
                if items[2] == 'draw':
                    move.type = self.MOVE_DRAW
                if items[2] == 'resign':
                    move.type = self.MOVE_RESGIN
        elif instruct == 'nobestmove':
            self.running = False
            move.type = self.MOVE_DEAD
        else:
            logger.warning(instruct)
            return

        if callable(self.callback):
            self.callback(move)

    def parse_fen(self, fen, moves=None):
        if fen == 'startpos':
            self.fen = fen
            self.init_startpos()
            return

        match = re.match(r'(?P<board>.+/{9}.+) (?P<turn>[w|b]) - - (?P<idle>\d+) (?P<bout>\d+)', fen)

        if not match:
            logger.warning('invalid fen %s', fen)
            return

        self.fen = match.group('board')
        if not moves:
            moves = []

        if match.group('turn') == 'w':
            self.turn = Chess.RED
        else:
            self.turn = Chess.BLACK

        self.idle = int(match.group('idle'))
        self.bout = int(match.group('bout'))

        self.board = mat(zeros((Chess.W, Chess.H)), dtype=int)

        index = 0
        for ch in match.group('board'):
            if ch == '/':
                continue
            if ch > '0' and ch <= '9':
                index += int(ch)
                continue
            chess = self.FEN_CHESS[ch.upper()]
            if ch > 'Z':
                chess *= -1

            pos = divmod(index, Chess.WIDTH)[::-1]

            index += 1
            self.board[pos] = chess
        return True

    def format_fen(self):
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

        items.extend(['-', '-', str(self.idle), str(self.bout)])

        result = ' '.join(items)

        return result

    def close(self):
        self.send_command('quit')
        return super().close()


def main():
    filename = dirpath / 'engines/eleeye/eleeye.exe'
    engine = UCCIEngine(filename)
    engine.start()

    from PySide6 import QtCore, QtWidgets, QtGui
    from board import BoardFrame
    app = QtWidgets.QApplication(sys.argv)
    ui = BoardFrame()

    def callback(move):
        if move.type == Engine.MOVE_BEST:
            engine.move(move.fpos, move.tpos)
            ui.board.setBoard(engine.board, move.fpos, move.tpos)

            time.sleep(1)
            if engine.turn == Chess.RED:
                engine.go(depth=7)
            else:
                engine.go(depth=3)
        elif move.type == Engine.MOVE_DEAD:
            return
            while engine.unmove():
                ui.board.setBoard(engine.board, engine.fpos, engine.tpos)
                time.sleep(0.01)
            # engine.unmove()

    engine.callback = callback
    engine.clear()
    logger.debug(engine.isready())
    engine.position()
    engine.go()

    ui.show()
    app.exec_()
    # thread.join()
    engine.close()


if __name__ == '__main__':
    main()
