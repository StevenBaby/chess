# coding=utf-8

import os
import sys
import pathlib

dirpath = pathlib.Path(__file__).parent
sys.path.insert(0, str(dirpath / 'src'))

from version import VERSION  # noqa

with open(dirpath / 'main.spec', 'r') as file:
    content = file.read()

result = content.format(VERSION=VERSION)

with open(dirpath / 'build.spec', 'w') as file:
    file.write(result)
