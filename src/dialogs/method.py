'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-30
'''

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6.QtCore import Qt

if __name__ == '__main__':
    import base

from logger import logger
from engine import Engine
from chess import Chess
from ui.method import Ui_Dialog
from dialogs.base import Signal
from dialogs.base import BaseDialog


class MethodDialog(BaseDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.engine = None
        self.standard = False

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.list = self.ui.listwidget

        # 设置标题
        self.setWindowTitle("着法")

        self.font = QtGui.QFont()
        self.font.setFamilies([u"DengXian"])
        self.font.setPointSize(14)

        self.red_style = QtGui.QBrush(QtGui.QColor(255, 0, 0, 255))
        self.black_style = QtGui.QBrush(QtGui.QColor(0, 0, 0, 255))

        self.signal = Signal(self)
        self.signal.refresh.connect(self.update)

    def event(self, e):
        if e.type() != QtCore.QEvent.NonClientAreaMouseButtonDblClick:
            return super().event(e)
        if not self.parentWidget():
            return super().event(e)
        parent = self.parentWidget()

        geometry = QtCore.QRect(
            self.geometry().x(),
            parent.geometry().y(),
            self.geometry().width(),
            parent.geometry().height()
        )

        self.setGeometry(geometry)

        return super().event(e)

    def update(self):
        super().update()

        if not self.engine:
            return

        engine = self.engine
        var = 0
        for index, sit in enumerate(engine.stack):
            if sit.moves:
                method = sit.get_method(engine.stack[index - 1].board, sit.fpos, sit.tpos, self.standard)
                method = f'{index:03} {method}'
            else:
                method = "棋局开始"

            item = self.list.item(var)

            if not item:
                item = QtWidgets.QListWidgetItem(self.list)

            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(self.font)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            if sit.turn == Chess.BLACK:
                item.setForeground(self.red_style)
            else:
                item.setForeground(self.black_style)

            item.setText(method)
            var += 1

        current = self.list.item(self.engine.index)
        self.list.setCurrentItem(current)

        while True:
            item = self.list.takeItem(var)
            if not item:
                break

    def refresh(self, engine: Engine):
        self.engine = engine
        self.signal.refresh.emit()

    def set_standard(self, standard: bool):
        logger.debug('standard changed %s', standard)
        self.standard = bool(standard)
        self.signal.refresh.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    window = MethodDialog()
    window.show()
    app.exec()
