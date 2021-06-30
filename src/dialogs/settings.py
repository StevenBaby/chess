'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-30
'''
import os

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtCore import Qt

if __name__ == '__main__':
    import base

from logger import logger
from engine import Engine
from chess import Chess
from ui.settings import Ui_Dialog
from dialogs.base import Signal
from dialogs.base import BaseDialog
from attrdict import attrdict
from version import VERSION
from engines import UCCI_ENGINES
import system


UPDATE_URL = 'https://github.com/StevenBaby/chess/releases'


class SettingsDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Dialog()
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
        self.red_engine = self.ui.red_engine
        self.black_engine = self.ui.black_engine
        self.standard_method = self.ui.standard_method

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
        self.setup_engines()

    def get_engine_box(self, turn) -> QtWidgets.QComboBox:
        if turn == Chess.RED:
            return self.red_engine
        else:
            return self.black_engine

    def setup_engines(self):
        for engine in UCCI_ENGINES:
            self.red_engine.addItem(engine.NAME)
            self.black_engine.addItem(engine.NAME)

    def show(self):
        self.backup = self.get_current()
        super().show()

    def get_filename(self):
        return os.path.join(system.get_execpath(), 'settings.json')

    def get_default(self):
        data = attrdict()
        data.version = VERSION
        data.transprancy = False
        data.reverse = False
        data.audio = True
        data.redside = 0
        data.blackside = 0
        data.delay = 300
        data.red_depth = 7
        data.black_depth = 1
        data.standard_method = False
        data.red_engine = 0
        data.black_engine = 0

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
        data.standard_method = self.standard_method.isChecked()

        data.red_engine = self.red_engine.currentIndex()
        data.black_engine = self.black_engine.currentIndex()

        return data

    def set_settings(self, settings):
        if self.standard_method.isChecked() != settings.standard_method:
            logger.info("set standard_method %s", settings.standard_method)
            self.standard_method.setChecked(settings.standard_method)

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

        if self.red_engine.currentIndex() != settings.red_engine:
            logger.info("set red_engine %s", settings.red_engine)
            self.red_engine.setCurrentIndex(settings.red_engine)

        if self.black_engine.currentIndex() != settings.black_engine:
            logger.info("set black_engine %s", settings.black_engine)
            self.black_engine.setCurrentIndex(settings.black_engine)

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


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    window = SettingsDialog()
    window.show()
    app.exec_()
