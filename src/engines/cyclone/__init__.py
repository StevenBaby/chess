import os

from engine import UCCIEngine

filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cyclone.exe')


class CycloneEngine(UCCIEngine):

    NAME = '象棋旋风'

    def __init__(self, callback):
        super().__init__(filename, callback=callback)
