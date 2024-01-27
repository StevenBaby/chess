import os

from engine import UCCIEngine

filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eleeye.exe')


class EleeyeEngine(UCCIEngine):

    NAME = '象眼引擎'

    def __init__(self, callback):
        super().__init__(filename, callback=callback)
