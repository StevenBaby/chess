'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-26
'''
from functools import partial

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

from logger import logger


class BaseContextMenu(QtWidgets.QMenu):

    items = [
        # 名称, 快捷键, 执行的函数, 是否可屏蔽
        ['测试', 'Ctrl+A', lambda self: print(self), True],
        'separator',
    ]

    def __init__(self, parent=None, signal: QtCore.QObject = None):
        super().__init__(parent)
        self.signal = signal
        self.font_families = QtGui.QFont()
        self.font_families.setFamilies([u"DengXian"])
        self.font_families.setPointSize(12)
        self.all_shortcuts = []
        self.disabled_shortcuts = []

        self.disabled_actions = []
        self.all_actions = []

        self.setTitle('菜单')
        self.createShortCut()
        self.createContextMenu()

    def setAllShortcutEnabled(self, enable: bool):
        for shortcut in self.disabled_shortcuts:
            shortcut.setEnabled(enable)

    def setAllMenuEnabled(self, enable: bool):
        for action in self.disabled_actions:
            action.setEnabled(enable)

    def createShortCut(self):
        for item in self.items:
            if len(item) == 4:
                name, key, slot, disabled = item
                if not key:
                    continue
                logger.info(f"add shortcut {name}")
                shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(key), self.parentWidget())
                shortcut.activated.connect(partial(slot, self))
                self.all_shortcuts.append(shortcut)
                if disabled:
                    self.disabled_actions.append(shortcut)

    def createContextMenu(self):
        for item in self.items:
            if len(item) == 4:
                name, key, slot, disabled = item
                action = QtWidgets.QAction(name, self)
                action.setFont(self.font_families)
                action.setShortcut(key)
                action.triggered.connect(partial(slot, self))
                self.addAction(action)
                self.all_actions.append(action)
                if disabled:
                    self.disabled_actions.append(action)
                logger.info(f"add action {len(self.actions())} {name}")
                continue
            if item == "separator":
                self.addSeparator()
                continue


class BaseContextMenuWidget(QtWidgets.QWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.menu = BaseContextMenu(self)
        self.setupContextMenu()

    def setupContextMenu(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, point):
        self.menu.exec_(self.mapToGlobal(point))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = BaseContextMenuWidget()
    window.show()
    sys.exit(app.exec_())
