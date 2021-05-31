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

    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    ADVISOR = 5
    CANNON = 6
    KING = 7

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

    @staticmethod
    def invert(chess):
        # 转换棋子颜色
        return (chess & 7) | ((~chess) & 0b110000)

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
