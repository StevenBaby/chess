'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-21
用于生成 走法的中文描述，如 炮二平五，马八进七
'''

# coding=utf-8
import numpy as np

from chess import Chess


class Method(object):

    NAMES = {
        Chess.P: '兵',
        Chess.R: '俥',
        Chess.N: '傌',
        Chess.B: '相',
        Chess.A: '仕',
        Chess.C: '炮',
        Chess.K: '帥',
        Chess.p: '卒',
        Chess.r: '車',
        Chess.n: '馬',
        Chess.b: '象',
        Chess.a: '士',
        Chess.c: '砲',
        Chess.k: '將',
    }

    STANDARD_NAME = {
        Chess.P: '兵',
        Chess.R: '车',
        Chess.N: '马',
        Chess.B: '相',
        Chess.A: '仕',
        Chess.C: '炮',
        Chess.K: '帅',
        Chess.p: '卒',
        Chess.r: '车',
        Chess.n: '马',
        Chess.b: '象',
        Chess.a: '士',
        Chess.c: '炮',
        Chess.k: '将',
    }

    CNUMS = [
        '零',
        '一',
        '二',
        '三',
        '四',
        '五',
        '六',
        '七',
        '八',
        '九'
    ]

    ANUMS = [chr(ord('０') + var) for var in range(0, 10)]

    def get_name(self, chess, standard=False):
        if not chess:
            return None
        if standard:
            return self.STANDARD_NAME[chess]
        return self.NAMES[chess]

    def get_pos(self, chess, pos, standard=False):
        if Chess.is_black(chess):
            num = pos[0] + 1
        else:
            num = 9 - pos[0]
        if standard and Chess.is_black(chess):
            return self.ANUMS[num]
        return self.CNUMS[num]

    def get_action(self, chess, fpos, tpos, standard=False):
        delta = (tpos[0] - fpos[0], tpos[1] - fpos[1])
        if Chess.is_red(chess):
            delta = (-delta[0], -delta[1])

        posx = self.get_pos(chess, tpos, standard)

        if Chess.chess(chess) in {Chess.ROOK, Chess.CANNON, Chess.PAWN, Chess.KING}:
            posy = self.CNUMS[abs(delta[1])]
            if Chess.is_black(chess) and standard:
                posy = self.ANUMS[abs(delta[1])]
        else:
            posy = posx

        if delta[1] > 0:
            action = '进'
            pos = posy
        elif delta[1] < 0:
            action = '退'
            pos = posy
        else:
            action = f'平'
            pos = posx

        return f'{action}{pos}'

    def get_column_chess(self, board, fpos):
        chess = board[fpos]
        result = []
        for var in range(0, 10):
            pos = (fpos[0], var)
            if board[pos] == chess:
                result.append(pos)
        return result

    def get_pawns(self, board, chess):
        wheres = np.argwhere(board == chess)
        return wheres

    def get_method(self, board, fpos, tpos, standard=False):
        chess = board[fpos]

        name = self.get_name(chess, standard)
        pos = self.get_pos(chess, fpos, standard)
        action = self.get_action(chess, fpos, tpos, standard)

        method = f'{name}{pos}{action}'

        if Chess.chess(chess) not in {Chess.ROOK, Chess.KNIGHT, Chess.CANNON, Chess.PAWN}:
            return method

        chesses = self.get_column_chess(board, fpos)
        if len(chesses) == 1:
            return method

        # 同一列棋子多于一个
        if Chess.is_black(chess):
            chesses.reverse()

        if fpos == chesses[0]:
            pos = '前'
        else:
            pos = '后'

        method = f'{pos}{name}{action}'

        if Chess.chess(chess) in {Chess.ROOK, Chess.KNIGHT, Chess.CANNON}:
            return method

        # 以下为卒的情况

        wheres = np.argwhere(board == chess)

        columns = {}

        for where in wheres:
            columns.setdefault(where[0], 0)
            columns[where[0]] += 1

        for var in list(columns.keys()):
            if columns[var] == 1:
                del columns[var]

        if len(columns) == 1:

            idx = 1
            for where in chesses:
                if fpos == where:
                    break
                idx += 1

            if idx == 1:
                pos = '前'
            elif idx == 2 and len(chesses) == 3:
                pos = '中'
            else:
                pos = '后'

            return f'{pos}{name}{action}'

        # 两列的情况
        rangex = list(range(9))
        if Chess.is_red(chess):
            rangex.reverse()

        rangey = list(range(10))
        if Chess.is_black(chess):
            rangey.reverse()

        index = 0
        for x in rangex:
            if x not in columns:
                continue
            for y in rangey:
                pos = (x, y)
                if board[pos] != chess:
                    continue
                index += 1
                if fpos != pos:
                    continue
                pos = self.CNUMS[index]
                return f'{pos}{name}{action}'

        # 理论上不可能到这里
        raise Exception('格式化着法失败')


if __name__ == '__main__':
    print([chr(ord('０') + var) for var in range(0, 10)])
