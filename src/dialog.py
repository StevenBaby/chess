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
from ui import comments

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
        self.hint_depth = self.ui.hint_depth
        self.engine_depth = self.ui.engine_depth

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

        self.ui.ok.clicked.connect(self.hide)
        self.ui.cancel.clicked.connect(self.hide)

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
        data.hint_depth = 7
        data.engine_depth = 1
        return data

    def loads(self):
        import json
        filename = self.get_filename()
        result = self.get_default()

        if not os.path.exists(filename):
            return

        with open(filename, encoding='utf8') as file:
            source = file.read()

        try:
            data = json.loads(source)
            data = attrdict.loads(data)
            result.update(data)
        except Exception:
            return

        logger.info("set transprancy %s", result.transprancy)
        self.transprancy.setValue(result.transprancy)

        logger.info("set reverse %s", result.reverse)
        self.reverse.setChecked(result.reverse)

        logger.info("set audio %s", result.audio)
        self.audio.setChecked(result.audio)

        logger.info("set redside %s", result.redside)
        self.redside.setCurrentIndex(result.redside)

        logger.info("set blackside %s", result.blackside)
        self.blackside.setCurrentIndex(result.blackside)

        logger.info("set delay %s", result.delay)
        self.delay.setValue(result.delay)

        logger.info("set hint_depth %s", result.hint_depth)
        self.hint_depth.setValue(result.hint_depth)

        logger.info("set engine_depth %s", result.engine_depth)
        self.engine_depth.setValue(result.engine_depth)

    @QtCore.Slot(None)
    def save(self):
        import json

        data = self.get_default()
        data.version = VERSION
        data.transprancy = self.transprancy.value()
        data.reverse = self.reverse.isChecked()
        data.audio = self.audio.isChecked()
        data.redside = self.redside.currentIndex()
        data.blackside = self.blackside.currentIndex()
        data.delay = self.delay.value()
        data.hint_depth = self.hint_depth.value()
        data.engine_depth = self.engine_depth.value()

        logger.info("save settings %s", data)

        content = json.dumps(data, ensure_ascii=False, indent=4)
        with open(self.get_filename(), 'w', encoding='utf8') as file:
            file.write(content)

    def check_update(self):
        import webbrowser
        webbrowser.open(UPDATE_URL)

    def _test_signal(self):
        pass


class Comments(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = comments.Ui_Dialog()
        self.ui.setupUi(self)

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
            else:
                comment = "开始"

            # logger.debug(comment)
            item = self.ui.comments.item(var)

            if not item:
                item = QtWidgets.QListWidgetItem(self.ui.comments)

            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(self.font)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            if sit.turn == Chess.BLACK:
                item.setForeground(self.red_style)
            else:
                item.setForeground(self.black_style)

            item.setText(comment)
            var += 1

        current = self.ui.comments.item(self.engine.index)
        self.ui.comments.setCurrentItem(current)

        while True:
            # item = self.ui.comments.item(var)
            item = self.ui.comments.takeItem(var)
            if not item:
                break

    def refresh(self, engine: Engine):
        self.engine = engine
        self.signal.refresh.emit()


def main():
    app = QtWidgets.QApplication()
    window = Comments()
    # window = Settings()
    # window._test_signal()
    # window.loads()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
