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


class SettingsDialog(BaseDialog):

    ATTRIBUTES = {
        'ok',
        'cancel',

        'version',
        'checkupdate',
    }

    SETTINGS = {
        'transprancy': 0,
        'audio': True,
        'reverse': False,
        'delay': 300,
        'animate': True,
        'standard_method': False,

        'redside': 0,
        'blackside': 0,

        'red_engine': 0,
        'black_engine': 0,

        'mode': 0,

        'red_depth': 7,
        'black_depth': 1,

        'red_time': 1000,
        'black_time': 1000,
        'qqboard': [842, 230, 1196, 1330],
    }

    ATTRIBUTES.update(
        SETTINGS.keys()
    )

    MODE_DEPTH = 0
    MODE_TIME = 1

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        for name in self.ATTRIBUTES:
            if not hasattr(self.ui, name):
                setattr(self, name, self.SETTINGS[name])
                continue

            attr = getattr(self.ui, name)
            setattr(self, name, attr)
            logger.info("set settings attr %s object %s", name, attr)

        self.ui.version.setText(f"v{VERSION}")
        self.ui.checkupdate.clicked.connect(self.check_update)

        # 设置标题
        self.setWindowTitle("设置")

        self.setStyleSheet("font-family: dengxian;")

        self.ui.ok.clicked.connect(self.save)

        self.ui.ok.clicked.connect(self.close)
        self.ui.cancel.clicked.connect(self.close)
        self.ui.cancel.clicked.connect(lambda: self.set_settings(self.backup))
        self.setup_engines()

        self.mode.currentIndexChanged.connect(self.update_mode)

    @QtCore.Slot(int)
    def update_mode(self, mode):
        if mode == self.MODE_DEPTH:
            # 深度制
            self.red_depth.setEnabled(True)
            self.black_depth.setEnabled(True)
            self.red_time.setEnabled(False)
            self.black_time.setEnabled(False)
        elif mode == self.MODE_TIME:
            #  加时制
            self.red_depth.setEnabled(False)
            self.black_depth.setEnabled(False)
            self.red_time.setEnabled(True)
            self.black_time.setEnabled(True)

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
        data = attrdict.loads(self.SETTINGS)
        data.version = VERSION
        return data

    def get_current(self):
        data = self.get_default()

        for name in self.SETTINGS:
            attr = getattr(self, name)
            if isinstance(attr, (QtWidgets.QLabel, )):
                continue
            if isinstance(attr, (QtWidgets.QSlider, QtWidgets.QSpinBox)):
                value = attr.value()
            elif isinstance(attr, QtWidgets.QCheckBox):
                value = attr.isChecked()
            elif isinstance(attr, QtWidgets.QComboBox):
                value = attr.currentIndex()
            elif isinstance(attr, list):
                value = attr
            else:
                raise Exception(str(attr))
            data[name] = value

        return data

    def set_settings(self, settings: dict):
        for name, value in self.SETTINGS.items():
            attr = getattr(self, name)
            if name in settings:
                value = settings[name]
            if isinstance(attr, (QtWidgets.QLabel, )):
                continue
            if isinstance(attr, (QtWidgets.QSlider, QtWidgets.QSpinBox)):
                if attr.value() != value:
                    attr.setValue(value)
                    logger.info("set %s %s", name, value)
            elif isinstance(attr, QtWidgets.QCheckBox):
                if attr.isChecked() != value:
                    attr.setChecked(value)
                    logger.info("set %s %s", name, value)
            elif isinstance(attr, QtWidgets.QComboBox):
                if attr.currentIndex() != value:
                    attr.setCurrentIndex(value)
                    logger.info("set %s %s", name, value)
            elif isinstance(attr, list):
                logger.info("list name %s old %s new %s", name, attr, value)
                setattr(self, name, value)
            else:
                raise Exception(str(attr))

        self.update_mode(self.get_mode())

    def get_mode(self):
        return self.ui.mode.currentIndex()

    def get_params(self, turn):
        mode = self.get_mode()
        params = attrdict()
        if mode == self.MODE_DEPTH:
            # 深度制
            if turn == Chess.RED:
                params.depth = self.red_depth.value()
            else:
                params.depth = self.black_depth.value()
        elif mode == self.MODE_TIME:
            #  加时制
            if turn == Chess.RED:
                params.time = self.red_time.value()
                params.opptime = self.black_time.value()
            else:
                params.time = self.black_time.value()
                params.opptime = self.red_time.value()
        else:
            raise Exception("invalid engine mode")
        return params

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
    window.loads()
    app.exec_()
