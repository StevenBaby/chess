import os

from engine import UCCIEngine

filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'binghe.exe')


class BingHeEngine(UCCIEngine):

    NAME = '兵河五四'

    def __init__(self, callback):
        super().__init__(filename, callback=callback)
