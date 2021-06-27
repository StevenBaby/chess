# coding=utf-8

import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtCore import Qt

from version import VERSION
from attrdict import attrdict
from logger import logger

from engine import Engine
from chess import Chess

from ui import settings
from ui import method

import system

UPDATE_URL = 'https://github.com/StevenBaby/chess/releases'


class Signal(QtCore.QObject):

    refresh = QtCore.Signal(None)


class Settings(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = settings.Ui_Dialog()
        self.ui.setupUi(self)

        self.ok = self.ui.ok
        self.transprancy = self.ui.transprancy
        self.reverse = self.ui.reverse
        self.redside = self.ui.redside
        self.blackside = self.ui.blackside
        self.version = self.ui.version
        self.checkupdate = self.ui.checkupdate
        self.audio = self.ui.audio
        self.delay = self.ui.delay
        self.red_depth = self.ui.red_depth
        self.black_depth = self.ui.black_depth

        self.version.setText(f"v{VERSION}")
        self.checkupdate.clicked.connect(self.check_update)

        # 去掉标题栏问号
        flags = QtCore.Qt.Dialog
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)

        # 设置标题
        self.setWindowTitle("设置")

        self.setStyleSheet("font-family: dengxian;")

        self.ui.ok.clicked.connect(self.save)

        self.ui.ok.clicked.connect(self.close)
        self.ui.cancel.clicked.connect(self.close)
        self.ui.cancel.clicked.connect(lambda: self.set_settings(self.backup))

    def show(self):
        self.backup = self.get_current()
        super().show()

    def get_filename(self):
        return os.path.join(system.get_execpath(), 'settings.json')

    def get_default(self):
        data = attrdict()
        data.version = VERSION
        data.transprancy = 0
        data.reverse = False
        data.audio = True
        data.redside = 0
        data.blackside = 0
        data.delay = 300
        data.red_depth = 7
        data.black_depth = 1
        return data

    def get_current(self):
        data = self.get_default()
        data.version = VERSION
        data.transprancy = self.transprancy.value()
        data.reverse = self.reverse.isChecked()
        data.audio = self.audio.isChecked()
        data.redside = self.redside.currentIndex()
        data.blackside = self.blackside.currentIndex()
        data.delay = self.delay.value()
        data.red_depth = self.red_depth.value()
        data.black_depth = self.black_depth.value()
        return data

    def set_settings(self, settings):
        if self.transprancy.value() != settings.transprancy:
            logger.info("set transprancy %s", settings.transprancy)
            self.transprancy.setValue(settings.transprancy)

        if self.reverse.isChecked() != settings.reverse:
            logger.info("set reverse %s", settings.reverse)
            self.reverse.setChecked(settings.reverse)

        if self.audio.isChecked() != settings.audio:
            logger.info("set audio %s", settings.audio)
            self.audio.setChecked(settings.audio)

        if self.redside.currentIndex() != settings.redside:
            logger.info("set redside %s", settings.redside)
            self.redside.setCurrentIndex(settings.redside)

        if self.blackside.currentIndex() != settings.blackside:
            logger.info("set blackside %s", settings.blackside)
            self.blackside.setCurrentIndex(settings.blackside)

        if self.delay.value() != settings.delay:
            logger.info("set delay %s", settings.delay)
            self.delay.setValue(settings.delay)

        if self.red_depth.value() != settings.red_depth:
            logger.info("set red_depth %s", settings.red_depth)
            self.red_depth.setValue(settings.red_depth)

        if self.black_depth.value() != settings.black_depth:
            logger.info("set black_depth %s", settings.black_depth)
            self.black_depth.setValue(settings.black_depth)

    def loads(self):
        import json
        filename = self.get_filename()
        settings = self.get_default()

        if not os.path.exists(filename):
            return

        with open(filename, encoding='utf8') as file:
            source = file.read()

        try:
            data = json.loads(source)
            data = attrdict.loads(data)
            settings.update(data)
        except Exception:
            return

        self.set_settings(settings)

    @QtCore.Slot(None)
    def save(self):
        import json

        data = self.get_current()

        logger.info("save settings %s", data)

        content = json.dumps(data, ensure_ascii=False, indent=4)
        with open(self.get_filename(), 'w', encoding='utf8') as file:
            file.write(content)

    def check_update(self):
        import webbrowser
        webbrowser.open(UPDATE_URL)

    def _test_signal(self):
        pass


class Method(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = method.Ui_Dialog()
        self.ui.setupUi(self)
        self.list = self.ui.listwidget

        # 去掉标题栏问号
        flags = QtCore.Qt.Dialog
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)

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
        engine = self.engine
        var = 0
        for index, sit in enumerate(engine.stack):
            if sit.moves:
                comment = sit.get_comment(engine.stack[index - 1].board, sit.fpos, sit.tpos)
                comment = f'{index:03} {comment}'
            else:
                comment = "棋局开始"

            # logger.debug(comment)
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

            item.setText(comment)
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


def main():
    app = QtWidgets.QApplication()
    window = Method()
    # window = Settings()
    # window._test_signal()
    # window.loads()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
