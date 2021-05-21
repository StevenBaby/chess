# coding=utf-8

import pygame

from engine import dirpath
from chess import Chess

AUDIO_MOVE = str(dirpath / 'audios/move.wav')
AUDIO_CAPTURE = str(dirpath / 'audios/capture.wav')
AUDIO_CHECK = str(dirpath / 'audios/check.wav')


def init():
    pygame.mixer.init()


def play(audio_type):
    if audio_type == Chess.CAPTURE:
        audio = AUDIO_CAPTURE
    elif audio_type == Chess.MOVE:
        audio = AUDIO_MOVE
    elif audio_type in (Chess.CHECK, Chess.CHECKMATE, Chess.CHECKWARN):
        audio = AUDIO_CHECK
    else:
        return

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
