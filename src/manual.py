# coding=utf-8

import re
import numpy as np

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

        ctype = chess & Chess.CMASK
        logger.debug("chess %s pos %s", chess, pos)
        wheres = np.argwhere(board == chess)
        if len(wheres) == 1:
            return tuple(wheres[0])

        wheres = sorted(wheres, key=lambda e: (e[0], e[1]))

        if type == 1:
            result = []
            for where in wheres:
                if where[0] != pos:
                    continue
                result.append(tuple(where))
            if len(result) == 1:
                return result[0]
            if ctype in (Chess.ADVISOR, Chess.BISHOP):
                if move[2] == BACKWARD:
                    return result[-1]
                else:
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
    from PySide6 import QtWidgets
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
    1. 相三进五 马２进３
 2. 兵三进一 卒３进１
 3. 马二进三 马３进４
 4. 马八进九 炮８平５
 5. 车九进一 炮２平４
 6. 车九平四 车１平２
 7. 仕四进五 马８进７
 8. 马三进二 炮５进４
 9. 车一平三 车２进５
10. 马二进三 车９平８
11. 车三进三 士６进５
12. 兵九进一 车２平１
13. 兵三进一 炮５退１
14. 车四进四 车１平４
15. 帅五平四 象７进５
16. 炮八平六 炮５退１
17. 兵三平二 车８平６
18. 车四进四 士５退６
19. 帅四平五 士４进５
20. 兵二进一 炮５平７
21. 炮六进三 车４退１
22. 兵二进一 炮４进１
23. 马三进五 象３进５
24. 兵二平三 炮７平８
25. 马九进八 车４平７
26. 车三进二 象５进７
27. 马八退六 炮４平３
28. 马六进七 炮３进３
29. 马七进五 象７退５
30. 马五退四 炮８退３
31. 马四进六 炮３退５
32. 马六进五 士５进４
33. 马五退六 士６进５
34. 马六进四 炮３进１
35. 兵三进一 炮８平９
36. 马四退三 炮３退１
37. 炮二平一 炮９进１
38. 炮一进四 炮３平７
39. 马三进二 炮７平６
40. 炮一平九 炮９平５
41. 炮九平五 将５平４
42. 兵一进一 炮５平６
43. 兵一进一 前炮进４
44. 兵一平二 前炮平２
45. 兵二平三 炮２退５
46. 马二退四 炮２平４
47. 马四退五 炮６退１
48. 马五进七 士５进６
49. 兵三进一 士６退５
50. 兵三平四 炮６平８
51. 炮五退三 炮８平５
52. 炮五平三 炮５平７
53. 马七进五 炮７平８
54. 马五进七 炮８进１
55. 炮三平五 士５退６
56. 相七进九 炮８平９
57. 马七退九 炮９进１
58. 马九退八 士６进５
59. 马八进七 炮９平５
60. 相九进七 炮４平３
61. 帅五平四 炮３平４
62. 马七进九 炮４平３
63. 马九进八 炮５平８
64. 仕五进六 炮８退１
65. 马八退九 炮８进１
66. 兵四平五 士５进６
67. 帅四平五 炮８平９
68. 兵五平六 士４退５
69. 仕六进五 炮９平８
70. 仕五进四 士５退６
71. 兵六平五 炮８平９
72. 兵五平四 士６退５
73. 马九进八 炮９平５
74. 帅五平四 炮５平８
75. 相五进三 炮８退１
76. 帅四平五 士５进４
77. 马八退九 士６进５
78. 炮五退二 炮８进２
79. 马九退七 炮８进３
80. 相三退五 炮３平４
81. 兵四平五 炮８平３
82. 相七退九 炮３平６
83. 兵五进一 炮４平３
84. 兵五平六 士５进４
85. 马七进六 炮６退４
    '''

    manual = Manual()
    manual.callback = callback
    thread = threading.Thread(target=manual.parse, args=(content, ))
    thread.start()

    app.exec()
    # thread.join()
    engine.close()
