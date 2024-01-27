'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-29
'''

# coding=utf-8

import os
import sys
import re
import importlib
import glob
import typing

dirname = os.path.dirname(os.path.abspath(__file__))
project = os.path.dirname(dirname)
if project not in sys.path:
    sys.path.insert(0, project)

from engine import Engine, PipeEngine  # noqa
from engine import UCCIEngine  # noqa

IGNORED = [PipeEngine, UCCIEngine]


def get_ucci_engines() -> typing.List[UCCIEngine]:
    engines = glob.glob(os.path.join(dirname, '*/__init__.py'))
    result = []
    for name in engines:
        name = os.path.dirname(name)
        name = name.replace(project, '')
        name = re.sub(r'[/\\]', '.', name)
        name = name.strip('.')

        module = importlib.import_module(name)
        for attr in dir(module):
            if not attr.endswith("Engine"):
                continue
            engine = getattr(module, attr)
            if not isinstance(engine, type):
                continue
            if engine in IGNORED:
                continue
            if not issubclass(engine, UCCIEngine):
                continue
            result.append(engine)
    return result


UCCI_ENGINES = get_ucci_engines()
