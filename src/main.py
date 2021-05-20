# coding=utf-8

import sys
import time

import pygame

from PySide6 import QtCore, QtWidgets, QtGui

from engine import dirpath
from engine import logger
from engine import UCCIEngine
from engine import Engine
from engine import Chess


class MainWindow(QtWidgets.QMainWindow):

    enginefile = dirpath / 'engines/eleeye/eleeye.exe'

    AUDIO_MOVE = str(dirpath / 'audios/move.wav')
    AUDIO_CAPTURE = str(dirpath / 'audios/capture.wav')
    AUDIO_CHECK = str(dirpath / 'audios/check.wav')

    def __init__(self):
        super().__init__()
        from ui import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.board = self.ui.board

        self.setWindowIcon(QtGui.QIcon(self.board.FAVICON))
        self.setWindowTitle(u"Chinese Chess")

        self.ui.reset.clicked.connect(self.reset)
        self.ui.hint.clicked.connect(self.hint)
        self.ui.undo.clicked.connect(self.undo)

        self.board.callback = self.board_callback

        self.engine = UCCIEngine(self.enginefile, callback=self.engine_callback)
        self.engine2 = UCCIEngine(self.enginefile, callback=self.engine_callback)

        self.reset()

        pygame.mixer.init()

    def play(self, audio_type):
        if audio_type == Engine.MOVE_CAPTURE:
            audio = self.AUDIO_CAPTURE
        elif audio_type == Engine.MOVE_IDLE:
            audio = self.AUDIO_MOVE
        else:
            return

        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()

    def reset(self):
        if self.engine:
            self.engine.close()
        if self.engine2:
            self.engine2.close()

        self.fpos = None

        self.engine = UCCIEngine(self.enginefile, callback=self.engine_callback)
        self.engine.start()

        self.engine2 = UCCIEngine(self.enginefile, callback=self.engine_callback)
        self.engine2.start()

        self.updateBoard()

        self.versus = True
        self.depth_red = 3
        self.depth_black = 3
        self.engine_delay = 0.1

    def hint(self):
        self.ui.hint.setEnabled(False)
        if self.versus:
            self.engine2.go(depth=self.depth_red)
        else:
            self.engine.go(depth=self.depth_red)

    def undo(self):
        for _ in range(2):
            if self.engine.steps:
                self.engine.unmove()
            if self.engine2.steps:
                self.engine2.unmove()
        self.updateBoard()

    def updateBoard(self):
        self.board.setBoard(self.engine.board, self.engine.fpos, self.engine.tpos)

    def engine_callback(self, move):
        time.sleep(self.engine_delay)
        if move.type == Engine.MOVE_DEAD:
            pass
        if move.type != Engine.MOVE_BEST:
            return
        result = self.engine.move(move.fpos, move.tpos)

        self.updateBoard()
        self.ui.hint.setEnabled(True)
        self.play(result)

        self.engine2.move(move.fpos, move.tpos)

        if self.engine.turn == Chess.BLACK:
            self.engine.go(depth=self.depth_black)
        elif self.versus:
            self.engine2.go(depth=self.depth_red)

    def board_callback(self, pos):
        if self.engine.color(pos) == self.engine.turn:
            self.fpos = pos
            self.board.setBoard(self.engine.board, self.fpos)
            return

        if not self.fpos:
            return

        result = self.engine.move(self.fpos, pos)
        if not result:
            return

        self.engine2.move(self.fpos, pos)

        self.updateBoard()
        self.engine.go(depth=self.depth_black)
        self.play(result)

    def resizeEvent(self, event):
        self.ui.board.resizeEvent(event)

    def closeEvent(self, event):
        self.engine.close()
        return super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
    # game = Game()
    # game.engine.close()


if __name__ == '__main__':
    main()
