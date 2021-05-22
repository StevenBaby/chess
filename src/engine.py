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

from attrdict import attrdict
from logger import logger
from chess import dirpath
from chess import Chess
from situation import Situation


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

    def __init__(self, filename: Path):
        super().__init__(daemon=True)

        self.filename = Path(filename)
        self.dirname = str(filename.parent)
        self.pipe = None
        self.state = self.ENGINE_BOOT

        self.sit = Situation()
        self.stack = [self.sit]

        self.parser_thread = threading.Thread(target=self.parser, daemon=True)

        self.outlines = Queue()
        self.running = False
        self.checkmate = False

        self.index = 0

        self.setup()

    def close(self):
        if self.pipe:
            self.pipe.terminate()

    def move(self, fpos, tpos):
        logger.debug('start move stack %s index %s', self.stack, self.index)
        nidx = self.index + 1
        if nidx < len(self.stack) and (self.stack[nidx].fpos, self.stack[nidx].tpos) == (fpos, tpos):
            logger.debug("forward hint %s", self.sit.format_move(fpos, tpos))
            self.sit = self.stack[nidx]
            self.index = nidx
            result = self.sit.result
            if result == Chess.CHECKMATE:
                self.checkmate = True
            return self.sit.result
        else:
            self.stack = self.stack[:self.index + 1]

        sit = copy.deepcopy(self.sit)

        result = sit.move(fpos, tpos)
        sit.result = result

        if not result:
            return result

        if result != Chess.INVALID:
            self.stack.append(sit)
            self.sit = sit
            self.index += 1
        else:
            self.sit.check = sit.check

        if result == Chess.CHECKMATE:
            self.checkmate = True

        logger.debug('finish move stack %s index %s', self.stack, self.index)

        return result

    def undo(self):
        logger.debug('start undo stack %s index %s', self.stack, self.index)
        if self.index == 0:
            return False

        self.checkmate = False
        self.index -= 1

        self.sit = self.stack[self.index]

        logger.debug(self.sit)
        logger.debug('finish undo stack %s index %s', self.stack, self.index)

        return True

    def redo(self):
        nidx = self.index + 1
        if nidx >= len(self.stack):
            return False

        self.index += 1
        self.sit = self.stack[self.index]
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
            logger.info("COMMAND: %s", command)
            line = f'{command}\n'.encode('gbk')
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
                logger.info("OUTPUT: %s", line)
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

    def __init__(self, filename, callback=None):
        self.ids = attrdict()
        self.options = attrdict()
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

    def close(self):
        self.send_command('quit')
        return super().close()

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

    def position(self):
        fen = self.sit.format_fen()

        mark = 'fen '
        if fen.startswith('startpos'):
            mark = ''

        command = f'position {mark}{fen}'

        self.send_command(command)

    def move(self, fpos, tpos):
        result = super().move(fpos, tpos)
        if not result:
            return result

        self.position()
        return result

    def undo(self):
        if super().undo():
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

        move_type = None
        fpos = None
        tpos = None

        if instruct == 'bestmove':
            moves = items[1].split()
            move_type = Chess.MOVE
            fpos, tpos = self.sit.parse_move(moves[0])

            if len(items) > 2:
                if items[2] == 'draw':
                    move_type = Chess.DRAW
                if items[2] == 'resign':
                    move_type = Chess.RESIGN

        elif instruct == 'nobestmove':
            self.running = False
            if self.sit.idle > 100:
                move_type = Chess.DRAW
            else:
                move_type = Chess.CHECKMATE
                # self.checkmate = True
        else:
            logger.warning(instruct)
            return

        if callable(self.callback):
            self.callback(move_type, fpos, tpos)


def main():
    filename = dirpath / 'engines/eleeye/eleeye.exe'
    engine = UCCIEngine(filename)
    engine.start()

    from PySide6 import QtCore, QtWidgets, QtGui
    from board import BoardFrame
    app = QtWidgets.QApplication(sys.argv)
    ui = BoardFrame()

    def callback(move_type, fpos, tpos):
        if move_type in (Chess.MOVE, ):
            engine.move(fpos, tpos)
            ui.board.setBoard(engine.sit.board, engine.sit.fpos, engine.sit.tpos)

            time.sleep(1)

            if engine.sit.turn == Chess.RED:
                engine.go(depth=2)
            else:
                engine.go(depth=3)

        elif move_type == Chess.CHECKMATE:
            return
            while engine.undo():
                ui.board.setBoard(engine.board, engine.fpos, engine.tpos)
                time.sleep(0.01)

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
