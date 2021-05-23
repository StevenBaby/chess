# coding=utf-8

from version import VERSION
import system

dirpath = system.get_dirpath()

with open(dirpath / 'main.spec', 'r') as file:
    content = file.read()

result = content.format(VERSION=VERSION)

with open(dirpath / 'build.spec', 'w') as file:
    file.write(result)
