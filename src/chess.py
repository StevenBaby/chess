# coding=utf-8
from pathlib import Path

import numpy as np

from logger import logger

dirpath = Path(__file__).parent


class Chess(object):

    NONE = 0
    RMASK = 16
    BMASK = 32
    RED = RMASK
    BLACK = BMASK
    TMASK = 0b110000
    CMASK = 0b111  # 7

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
