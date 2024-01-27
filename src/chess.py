# coding=utf-8
import numpy as np

from logger import logger


class Chess(object):

    NONE = 0

    RMASK = 16  # 第五位表示红方 比如红車 0b01_0_001
    # 判断棋子是不是黑方只需要 按位与 0b0100000 就可以了

    BMASK = 32  # 第六位表示黑方 比如黑炮 0b10_0_110
    # 判断棋子是不是黑方只需要 按位与 0b100000 就可以了

    RED = RMASK
    BLACK = BMASK
    TMASK = 0b110000  # 棋子颜色掩码，可能的取值为 16 和 32
    CMASK = 0b111  # 棋子掩码

    # 棋子使用 1-7 来表示，二进制就是 0b001 - 0b111

    # INDEX = {
    #     '帥': (0, 0), '仕': (1, 0), '相': (2, 0), '傌': (3, 0), '俥': (4, 0), '炮': (5, 0), '兵': (6, 0),
    #     '將': (0, 1), '士': (1, 1), '象': (2, 1), '馬': (3, 1), '車': (4, 1), '砲': (5, 1), '卒': (6, 1),
    # }

    KING = 1
    ADVISOR = 2
    BISHOP = 3
    KNIGHT = 4
    ROOK = 5
    CANNON = 6
    PAWN = 7

    P = PAWN | RMASK
    R = ROOK | RMASK
    N = KNIGHT | RMASK
    B = BISHOP | RMASK
    A = ADVISOR | RMASK
    C = CANNON | RMASK
    K = KING | RMASK

    p = PAWN | BMASK
    r = ROOK | BMASK
    n = KNIGHT | BMASK
    b = BISHOP | BMASK
    a = ADVISOR | BMASK
    c = CANNON | BMASK
    k = KING | BMASK

    WIDTH = 9
    HEIGHT = 10
    W = WIDTH
    H = HEIGHT

    NAMES = {
        0: ' ',
        P: 'P',
        R: 'R',
        N: 'N',
        B: 'B',
        A: 'A',
        C: 'C',
        K: 'K',
        p: 'p',
        r: 'r',
        n: 'n',
        b: 'b',
        a: 'a',
        c: 'c',
        k: 'k',
    }

    CHESSES = {P, R, N, B, A, C, K, p, r, n, b, a, c, k, }

    @staticmethod
    def invert(chess):
        # 转换棋子颜色
        return (chess & 7) | ((~chess) & 0b110000)

    @staticmethod
    def is_red(chess):
        return chess & Chess.RED

    @staticmethod
    def is_black(chess):
        return chess & Chess.BLACK

    @staticmethod
    def chess(c):
        return c & Chess.CMASK

    ORIGIN = np.mat(
        np.array(
            [
                [r, 0, 0, p, 0, 0, P, 0, 0, R],
                [n, 0, c, 0, 0, 0, 0, C, 0, N],
                [b, 0, 0, p, 0, 0, P, 0, 0, B],
                [a, 0, 0, 0, 0, 0, 0, 0, 0, A],
                [k, 0, 0, p, 0, 0, P, 0, 0, K],
                [a, 0, 0, 0, 0, 0, 0, 0, 0, A],
                [b, 0, 0, p, 0, 0, P, 0, 0, B],
                [n, 0, c, 0, 0, 0, 0, C, 0, N],
                [r, 0, 0, p, 0, 0, P, 0, 0, R]
            ]
        )
    )

    MOVE = 1
    CAPTURE = 2
    DRAW = 3
    CHECK = 4
    INVALID = 5
    CHECKMATE = 6
    RESIGN = 7
    NEWGAME = 8

    # 以下为引擎专用
    INFO = 9
    POPHASH = 10
    NOBESTMOVE = 11
