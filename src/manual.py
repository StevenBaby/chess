# coding=utf-8

import re
import numpy as np
from numpy.lib.function_base import select

from chess import Chess
from logger import logger
from situation import Situation

CHESSES = {

    '俥': Chess.ROOK,
    '車': Chess.ROOK,
    '车': Chess.ROOK,

    '傌': Chess.KNIGHT,
    '馬': Chess.KNIGHT,
    '马': Chess.KNIGHT,

    '相': Chess.BISHOP,
    '象': Chess.BISHOP,

    '仕': Chess.ADVISOR,
    '士': Chess.ADVISOR,

    '帥': Chess.KING,
    '帅': Chess.KING,
    '將': Chess.KING,
    '将': Chess.KING,

    '兵': Chess.PAWN,
    '卒': Chess.PAWN,

    '炮': Chess.CANNON,
    '砲': Chess.CANNON,
}

NUMBERS = {
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,
    '前': 1,
    '中': 2,
    '后': 3,
}
NUMBERS.update(
    {
        chr(ord('０') + var): var
        for var in range(1, 10)
    }
)
NUMBERS.update(
    {
        chr(ord('0') + var): var
        for var in range(1, 10)
    }
)


CNAME = '俥車车傌馬马相象仕士帥帅將将兵卒炮砲'
PNAME = '一二三四五1-5１２３４５前中后'
XNAME = '一二三四五六七八九1-9１２３４５６７８９'
ANAME = '进退平'

PATTERN = re.compile(f'[{CNAME}{PNAME}][{XNAME}{CNAME}][{ANAME}][{XNAME}]')
PATTERN1 = re.compile(f'[{CNAME}][{XNAME}]')
PATTERN2 = re.compile(f'[{PNAME}][{CNAME}]')


FORWARD = '进'
BACKWARD = '退'
TOWARD = '平'


class Line(object):

    def __init__(self, nr, line) -> None:
        self.nr = nr
        self.line = line
        self.moves = PATTERN.findall(line)


class Manual(object):

    def __init__(self) -> None:
        self.callback = None
        self.sit = Situation()

    def parse(self, content: str):
        lines = content.splitlines()

        for nr, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                # 去掉空行
                continue
            if line.startswith('#'):
                # 去掉注释
                continue

            line = Line(nr, line)
            if not line.moves:
                continue
            for move in line.moves:
                fpos, tpos = self.parse_move(line, move)
                result = self.sit.move(fpos, tpos)
                if not result:
                    self.invalid_manual(line, move)
                if callable(self.callback):
                    self.callback(fpos, tpos)

    def parse_move(self, line: Line, move: str):
        logger.debug("parse move %s", move)
        board = self.sit.board
        if self.sit.turn == Chess.RED:
            board = np.rot90(board, k=2)

        fpos = self.get_fpos(board, line, move)
        tpos = self.get_tpos(board, fpos, move)

        if self.sit.turn == Chess.RED:
            fpos = (8 - fpos[0], 9 - fpos[1])
            tpos = (8 - tpos[0], 9 - tpos[1])

        return fpos, tpos

    def invalid_manual(self, line: Line, move: str):
        raise Exception(f'棋谱第 {line.nr} 行 {move} 不合法')

    def get_fpos(self, board, line, move):
        if PATTERN1.match(move[:2]):
            chess = CHESSES[move[0]] | self.sit.turn
            pos = NUMBERS[move[1]] - 1
            type = 1

        elif PATTERN2.match(move[:2]):
            chess = CHESSES[move[1]] | self.sit.turn
            pos = NUMBERS[move[0]]
            type = 2
        else:
            self.invalid_manual()

        logger.debug("chess %s pos %s", chess, pos)
        wheres = np.argwhere(board == chess)
        if len(wheres) == 1:
            return tuple(wheres[0])

        if type == 1:
            result = []
            for where in wheres:
                if where[0] != pos:
                    continue
                result.append(tuple(where))
            if len(result) == 1:
                return result[0]
            self.invalid_manual(line, move)
        else:
            columns = {}
            for where in wheres:
                columns.setdefault(where[0], [])
                columns[where[0]].append(where)
            for key in list(columns.keys()):
                if len(columns[key]) < 2:
                    del columns[key]
            columns = sorted(columns.items(), key=lambda e: e[0], reverse=True)
            if move[0] == '前':
                return tuple(columns[0][1][-1])
            elif move[0] == '中':
                return tuple(columns[0][1][-2])
            elif move[0] == '后':
                return tuple(columns[0][1][0])

            index = self.numbers[move[0]]
            counter = 1
            for idx, column in columns:
                column = list(column)
                column.reverse()
                for where in column:
                    if counter == index:
                        return tuple(where)
                    counter += 1

            self.invalid_manual(line, move)

    def get_tpos(self, board, fpos, move):
        pos = NUMBERS[move[3]]
        action = move[2]
        if action == '平':
            return (pos - 1, fpos[1])

        chess = board[fpos]
        ctype = chess & Chess.CMASK

        if ctype in (Chess.KING, Chess.ROOK, Chess.CANNON, Chess.PAWN):
            if move[2] == '进':
                return (fpos[0], fpos[1] + pos)
            else:
                return (fpos[0], fpos[1] - pos)

        if ctype == Chess.BISHOP:
            if pos in (1, 5, 9):
                return (pos - 1, 2)
            if action == '进':
                return (pos - 1, 4)
            else:
                return (pos - 1, 0)
        elif ctype == Chess.ADVISOR:
            if pos == 5:
                return (pos - 1, 1)
            if action == '进':
                return (pos - 1, 2)
            else:
                return (pos - 1, 0)
        else:
            # 马的情况
            offset0 = (pos - 1) - fpos[0]
            if abs(offset0) == 1:
                if action == '进':
                    offset1 = 2
                else:
                    offset1 = -2
            else:
                if action == '进':
                    offset1 = 1
                else:
                    offset1 = -1
            return (fpos[0] + offset0, fpos[1] + offset1)


if __name__ == '__main__':
    import pathlib
    dirname = pathlib.Path(__file__).parent

    import sys
    from PySide2 import QtWidgets
    from board import BoardFrame
    import threading
    from engine import Engine

    engine = Engine()

    app = QtWidgets.QApplication(sys.argv)
    ui = BoardFrame()
    ui.show()

    def callback(fpos, tpos):
        engine.move(fpos, tpos)
        ui.board.setBoard(engine.sit.board, engine.sit.fpos, engine.sit.tpos)

    content = '''
    # 沿河十八打
    1.炮二平五 炮2平5
    2.马二进三 马8进7
    3.车一平二 车9平8
    4.车二进六 炮8平9
    5.车二平三 车8进2
    6.车九进一 马2进3
    7.炮八进二 车1平2
    8.炮八平七 马3退5
    9.马八进九 炮9退1
    10.车九平四 炮9平7
    11.车三平四 炮5进4
    12.马三进五 马5进6
    13.马五进六 马6退5
    14.马六进四 车8退1
    15.车四平八 车2平1
    16.炮七平九 象3进1
    17.车八平二 车8平9
    18.炮九平一 象7进9
    19.车二进六 炮7进5
    20.车二平三 炮7平5
    21.炮五进四 马5进6
    22.车三平五 车9平5
    23.炮一进三 炮5退4
    24.相三进五 马6退7
    25.炮一平二 马7进9
    26.炮二平三 马9退7
    27.兵七进一 车1平2
    28.马九进七 车2进4
    29.马七进五 车2平5
    30.炮三平九 前车平2
    31.马五进六 车2退3
    32.炮九进二 车2退1
    33.马六进七
    '''

    manual = Manual()
    manual.callback = callback
    thread = threading.Thread(target=manual.parse, args=(content, ))
    thread.start()

    app.exec_()
    # thread.join()
    engine.close()
