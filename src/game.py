# coding=utf-8

import sys

from PySide6 import QtWidgets

from board import BoardFrame
from engine import Engine
from engine import UCCIEngine


class Game(BoardFrame):
    pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Game()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
