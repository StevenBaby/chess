import os

from engine import UCCIEngine

filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pikafish-bmi2.exe')


class PiKaFishEngine(UCCIEngine):

    NAME = '皮卡鱼'

    def __init__(self, callback):
        super().__init__(filename, callback=callback)
