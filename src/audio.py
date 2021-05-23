# coding=utf-8

import pygame

from chess import Chess
from logger import logger

import system

dirpath = system.get_dirpath()

AUDIO_MOVE = str(dirpath / 'audios/move.wav')
AUDIO_CAPTURE = str(dirpath / 'audios/capture.wav')
AUDIO_CHECK = str(dirpath / 'audios/check.wav')
AUDIO_INVALID = str(dirpath / 'audios/invalid.wav')
AUDIO_NEW_GAME = str(dirpath / 'audios/newgame.wav')


def init():
    pygame.mixer.init()


def play(audio_type):
    if audio_type == Chess.CAPTURE:
        audio = AUDIO_CAPTURE
    elif audio_type == Chess.MOVE:
        audio = AUDIO_MOVE
    elif audio_type == Chess.CHECK:
        audio = AUDIO_CHECK
    elif audio_type == Chess.INVALID:
        audio = AUDIO_INVALID
    elif audio_type == Chess.NEWGAME:
        audio = AUDIO_NEW_GAME
    else:
        return

    logger.info("play audio %s", audio)
    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
