'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-30
'''

import os
import sys

from PySide6 import QtWidgets
from PySide6 import QtCore

dirname = os.path.dirname(os.path.abspath(__file__))
project = os.path.dirname(dirname)

if project not in sys.path:
    sys.path.insert(0, project)


class Signal(QtCore.QObject):

    refresh = QtCore.Signal(None)


class BaseDialog(QtWidgets.QDialog):

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        # 去掉标题栏问号
        flags = QtCore.Qt.Dialog
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
