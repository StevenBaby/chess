# coding=utf-8

import os
import pathlib
import sys
from logger import logger

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    RELEASE = True
    DEBUG = False
else:
    RELEASE = False
    DEBUG = True


def get_dirpath():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return pathlib.Path(sys._MEIPASS)
    else:
        return pathlib.Path(__file__).parent


def get_execpath():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(os.path.realpath(sys.executable))
    else:
        return pathlib.Path(__file__).parent
