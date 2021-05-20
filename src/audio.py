# coding=utf-8

import pygame

from engine import dirpath
from engine import Engine

AUDIO_MOVE = str(dirpath / 'audios/move.wav')
AUDIO_CAPTURE = str(dirpath / 'audios/capture.wav')
AUDIO_CHECK = str(dirpath / 'audios/check.wav')


def init():
    pygame.mixer.init()


def play(audio_type):
    if audio_type == Engine.MOVE_CAPTURE:
        audio = AUDIO_CAPTURE
    elif audio_type == Engine.MOVE_IDLE:
        audio = AUDIO_MOVE
    elif audio_type == Engine.MOVE_CHECK:
        audio = AUDIO_CHECK
    else:
        return

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
