'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-22
用于局面 以及 走法生成 的数据结构
'''

# coding=utf-8

import copy
import re
import itertools

import numpy as np

from chess import Chess
from logger import logger
from method import Method


class Generator(object):

    '''走法生成器'''

    def filter_valid(self, wheres):

        return [var for var in wheres if (-1 < var[0] < Chess.W) and (-1 < var[1] < Chess.H)]

    def generate_rook(self, board, where, turn):
        alter = [
            [(var, where[1]) for var in range(where[0] - 1, -1, -1)],
            [(var, where[1]) for var in range(where[0] + 1, Chess.W, 1)],
            [(where[0], var) for var in range(where[1] - 1, -1, -1)],
            [(where[0], var) for var in range(where[1] + 1, Chess.H, 1)],
        ]
        result = []
        for wheres in alter:
            for pos in wheres:
                if not board[pos]:
                    result.append(pos)
                    continue
                elif board[pos] & turn == 0:
                    result.append(pos)
                    break
                else:
                    break
        return result

    def generate_knight(self, board, where, turn):
        # offsets = [var for var in itertools.product([1, -1, 2, -2], repeat=2) if abs(var[0] * var[1]) == 2]
        offsets = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        where = np.array(where)
        alter = self.filter_valid([where + np.array(var) for var in offsets])

        result = []
        for pos in alter:
            if (board[tuple(pos)] & turn) != 0:  # 不能吃自己的棋子
                continue

            offset = pos - where
            # 可能蹩马腿的棋子位置
            barrier = where + (np.abs(offset) // 2) * np.sign(offset)
            if board[tuple(barrier)]:
                continue
            result.append(tuple(pos))
        return result

    def generate_bishop(self, board, where, turn):
        # offsets = [var for var in itertools.product([2, -2], repeat=2)]
        offsets = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        where = np.array(where)
        alter = self.filter_valid([where + np.array(var) for var in offsets])

        result = []
        for pos in alter:
            if (board[tuple(pos)] & turn) != 0:  # 不能吃自己的棋子
                continue

            offset = pos - where
            # 可能卡象眼的棋子位置
            barrier = where + (offset // 2)
            if board[tuple(barrier)]:
                continue
            result.append(tuple(pos))

        return result

    def generate_advisor(self, board, where, turn):
        # offsets = [var for var in itertools.product([1, -1], repeat=2)]
        offsets = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        where = np.array(where)
        alter = self.filter_valid([where + np.array(var) for var in offsets])
        result = []

        for pos in alter:
            if (board[tuple(pos)] & turn) != 0:  # 不能吃自己的棋子
                continue
            if pos[0] < 3 or pos[0] > 5:  # 不能出宫
                continue
            if turn == Chess.RED and pos[1] < 7:  # 不能出宫
                continue
            if turn == Chess.BLACK and pos[1] > 2:  # 不能出宫
                continue
            result.append(tuple(pos))

        return result

    def generate_king(self, board, where, turn):
        offsets = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        where = np.array(where)
        alter = self.filter_valid([where + np.array(var) for var in offsets])
        result = []
        for pos in alter:
            if (board[tuple(pos)] & turn) != 0:  # 不能吃自己的棋子
                continue

            if pos[0] < 3 or pos[0] > 5:  # 不能出宫
                continue
            if turn == Chess.RED and pos[1] < 7:  # 不能出宫
                continue
            if turn == Chess.BLACK and pos[1] > 2:  # 不能出宫
                continue
            result.append(tuple(pos))

        # 单独判断老将见面
        king = list(np.argwhere(board == Chess.invert((Chess.KING | turn))))
        if not king:  # 没找到对方老将，可能局面不合法
            return result
        king = king[0]
        if where[0] != king[0]:  # 不在同一列，一定不见面
            return result

        start = min(where[1], king[1]) + 1
        stop = max(where[1], king[1])

        for var in range(start, stop):
            pos = (where[0], var)
            if board[pos]:  # 有遮挡，一定不见面
                return result
        # 无遮挡
        result.append(tuple(king))
        return result

    def generate_cannon(self, board, where, turn):
        alter = [
            [(var, where[1]) for var in range(where[0] - 1, -1, -1)],
            [(var, where[1]) for var in range(where[0] + 1, Chess.W, 1)],
            [(where[0], var) for var in range(where[1] - 1, -1, -1)],
            [(where[0], var) for var in range(where[1] + 1, Chess.H, 1)],
        ]

        result = []

        for wheres in alter:
            barrier = 0
            for pos in wheres:
                if barrier == 0:  # 没有炮架子
                    if not board[pos]:  # 没有架子可以直接移动
                        result.append(pos)
                    else:
                        barrier = 1
                    continue
                # 有炮架子
                if not board[pos]:
                    continue
                if board[pos] & Chess.invert(turn) != 0:
                    result.append(pos)
                    break
                if board[pos]:
                    break
        return result

    def generate_pawn(self, board, where, turn):
        # turn - 16 red 32 black

        offsets = [(0, np.sign(turn - 20))]

        # 过河卒
        if where[1] > 4 and turn == Chess.BLACK:
            offsets.extend([(-1, 0), (1, 0)])
        if where[1] < 5 and turn == Chess.RED:
            offsets.extend([(-1, 0), (1, 0)])

        where = np.array(where)
        alter = self.filter_valid([where + np.array(var) for var in offsets])
        result = []
        for pos in alter:
            if (board[tuple(pos)] & turn) != 0:  # 不能吃自己的棋子
                continue
            result.append(tuple(pos))
        return result

    def generate(self, board, where, turn):
        if not board[where]:
            return []

        chess = board[where] & Chess.CMASK
        if chess == Chess.ROOK:
            return self.generate_rook(board, where, turn)
        if chess == Chess.KNIGHT:
            return self.generate_knight(board, where, turn)
        if chess == Chess.BISHOP:
            return self.generate_bishop(board, where, turn)
        if chess == Chess.ADVISOR:
            return self.generate_advisor(board, where, turn)
        if chess == Chess.KING:
            return self.generate_king(board, where, turn)
        if chess == Chess.CANNON:
            return self.generate_cannon(board, where, turn)
        if chess == Chess.PAWN:
            return self.generate_pawn(board, where, turn)

        return []

    def get_check(self, board, turn):
        king = turn | Chess.KING
        king = list(np.argwhere(board == (Chess.KING | turn)))
        if not king:
            return None
        king = tuple(king[0])

        chesses = np.argwhere((board & Chess.invert(turn)) != 0)

        for chess in chesses:
            steps = self.generate(board, tuple(chess), Chess.invert(turn))
            valid = [var for var in steps if var == king]
            if valid:
                return tuple(chess)
        return None

    def is_checkmate(self, board, turn):
        chesses = np.argwhere((board & turn) != 0)
        for var in chesses:
            fpos = tuple(var)
            steps = self.generate(board, fpos, turn)
            for tpos in steps:
                tboard = copy.deepcopy(board)
                tboard[tpos] = board[fpos]
                tboard[fpos] = 0

                check = self.get_check(tboard, turn)
                if not check:
                    return False
        return True


class Situation(Generator, Method):

    def __init__(self, board: np.array = None, turn=Chess.RED, moves=None, bout=1, idle=0):
        if board is None:
            self.board = copy.deepcopy(Chess.ORIGIN)
        else:
            self.board = board

        self.turn = turn
        self.moves = moves
        if not moves:
            self.moves = []
        self.bout = bout
        self.idle = idle
        self.result = False
        self.check = None
        self.fen = self.format_current_fen()

    @property
    def fpos(self):
        if not self.moves:
            return None
        return self.moves[-1][0]

    @property
    def tpos(self):
        if not self.moves:
            return None
        return self.moves[-1][1]

    def print(self):
        print(self.board.T)

    def show(self, csize=20):
        # import threading
        from PySide2 import QtWidgets
        from board import BoardFrame

        hasapp = QtWidgets.QApplication.instance()
        if hasapp is None:
            import sys
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = hasapp
        ui = BoardFrame()
        ui.board.csize = csize
        ui.resize(ui.board.csize * Chess.W, ui.board.csize * Chess.H)
        ui.board.setBoard(self.board, self.fpos, self.tpos)
        ui.show()

        if not hasapp:
            app.exec_()

    @staticmethod
    def parse_move(move):
        fpos = (ord(move[0]) - ord('a'), 9 - int(move[1]))
        tpos = (ord(move[2]) - ord('a'), 9 - int(move[3]))
        return (fpos, tpos)

    @staticmethod
    def format_move(fpos, tpos):
        var1 = chr(ord('a') + fpos[0])
        var2 = str(9 - fpos[1])
        var3 = chr(ord('a') + tpos[0])
        var4 = str(9 - tpos[1])
        return ''.join([var1, var2, var3, var4])

    def parse_fen(self, fen, load=False):
        if fen == 'startpos':
            self.__init__()
            return True

        pattern = r'((?:[RNBAKCP1-9]+/){9}[RNBAKCP1-9]+) ([wb]) - - (\d+) (\d+)(?: moves((?: [a-i]\d[a-i]\d)+))?'
        match = re.match(pattern, fen, re.IGNORECASE)
        if not match:
            logger.warning('invalid fen %s', fen)
            return None

        self.board = np.mat(np.zeros((Chess.W, Chess.H)), dtype=int)

        self.fen = f"{match.group(1)} {match.group(2)} - - {match.group(3)} {match.group(4)}"

        if match.group(2) == 'w':
            self.turn = Chess.RED
        else:
            self.turn = Chess.BLACK

        self.idle = int(match.group(3))
        self.bout = int(match.group(4))

        index = 0
        values = dict(zip(Chess.NAMES.values(), Chess.NAMES.keys()))

        for ch in match.group(1):
            if ch == '/':
                continue
            if ch > '0' and ch <= '9':
                index += int(ch)
                continue

            pos = divmod(index, Chess.WIDTH)[::-1]

            index += 1
            self.board[pos] = values[ch]

        if not match.group(5):
            return True

        self.moves = []

        moves = match.group(5).strip().split()
        for move in moves:
            fpos, tpos = self.parse_move(move)
            self.moves.append((fpos, tpos))
            if not load:
                self.board[tpos] = self.board[fpos]
                self.board[fpos] = 0
                self.turn = Chess.invert(self.turn)

        logger.debug('parse turn %d idle %d bout %d', self.turn, self.idle, self.bout)

        return True

    def format_current_fen(self):
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
                slot.append(Chess.NAMES[chess])
            if blank:
                slot.append(str(blank))
                blank = 0

            line = ''.join(slot)
            lines.append(line)

        result = '/'.join(lines)

        items = [result]
        if self.turn == Chess.RED:
            items.append('w')
        else:
            items.append('b')

        items.extend(['-', '-', str(self.idle), str(self.bout)])

        result = ' '.join(items)

        return result

    def format_fen(self):
        if not self.moves:
            return self.fen
        moves = [
            self.format_move(fpos, tpos)
            for fpos, tpos in self.moves
        ]
        moves = ' '.join(moves)

        return f'{self.fen} moves {moves}'

    def where_turn(self, where):
        return self.board[where] & Chess.TMASK

    def validate_move(self, board, fpos, tpos):
        if fpos == tpos:
            return False
        return tpos in self.generate(board, fpos, self.turn)

    def move(self, fpos, tpos):
        if not self.validate_move(self.board, fpos, tpos):
            return False

        logger.info("get comment %s", self.get_comment(self.board, fpos, tpos))

        board = copy.deepcopy(self.board)
        board[tpos] = board[fpos]
        board[fpos] = Chess.NONE

        check = self.get_check(board, self.turn)
        if check:
            self.check = check
            return Chess.INVALID

        self.check = None

        if self.board[tpos]:
            self.idle = 0
        else:
            self.idle += 1

        if self.board[tpos]:
            result = Chess.CAPTURE
        else:
            result = Chess.MOVE

        self.turn = Chess.invert(self.turn)
        if self.turn == Chess.RED:
            self.bout += 1

        self.board[tpos] = self.board[fpos]
        self.board[fpos] = Chess.NONE
        self.moves.append((fpos, tpos))

        if self.is_checkmate(self.board, self.turn):
            logger.warning("Checkmate ......")
            return Chess.CHECKMATE

        check = self.get_check(self.board, self.turn)
        if check:
            self.check = check
            return Chess.CHECK

        return result

    def __repr__(self):
        if not self.fpos:
            return 'startpos'
        return self.format_move(self.fpos, self.tpos)


def main():
    sit = Situation()
    fen = sit.format_fen()
    logger.debug(fen)

    # fen = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1'
    # fen = 'rnbakabnr/9/1c5c1/9/9/9/9/1C5C1/9/RNBAKABNR w - - 0 1'
    # fen = 'rnbakabnr/9/1c5c1/P1P1P1P1P/9/9/9/1C5C1/9/RNBAKABNR w - - 0 1'
    fen = '9/9/3k5/9/9/9/4R4/3A5/4K4/8r b - - 0 1 moves i0i1 e1e0 i1i0 e0e1 i0i1 e1e0 i1i0 e0e1 i0i1 e1e0'
    fen = '9/9/3k5/9/9/9/4R4/3AB4/4K4/7rr b - - 0 1 moves i0i1 e1e0 i1i0 e0e1 i0i1 e1e0 i1i0 e0e1 i0i1'

    sit.parse_fen(fen)

    logger.debug(sit.turn)
    logger.debug(sit.fen)
    # logger.debug(sit.moves)
    # sit.print()
    logger.debug(sit.get_check(sit.board, Chess.RED))
    logger.debug(sit.is_checkmate(sit.board, Chess.RED))
    # logger.debug(sit.generate(sit.board, (0, 0), Chess.BLACK))
    # logger.debug(sit.generate(sit.board, (1, 0), Chess.BLACK))
    # logger.debug(sit.generate(sit.board, (2, 0), Chess.BLACK))
    # logger.debug(sit.generate(sit.board, (3, 0), Chess.BLACK))
    # logger.debug(sit.generate(sit.board, (4, 0), Chess.BLACK))
    # logger.debug(sit.generate(sit.board, (4, 3), Chess.RED))
    # logger.debug(sit.generate(sit.board, (1, 2), Chess.BLACK))
    # logger.debug(sit.generate(sit.board, (4, 6), sit.turn))
    # sit.show(50)


if __name__ == '__main__':
    main()
