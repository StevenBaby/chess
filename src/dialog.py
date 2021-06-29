# coding=utf-8

import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtCore import Qt

from version import VERSION
from attrdict import attrdict
from logger import logger

from chess import Chess
from engine import Engine
from chess import Chess
from engines import UCCI_ENGINES

from ui import settings
from ui import method

import system

UPDATE_URL = 'https://github.com/StevenBaby/chess/releases'


class Signal(QtCore.QObject):

    refresh = QtCore.Signal(None)


class Settings(QtWidgets.QDialog):

    ATTRIBUTES = {
        'ok',
        'cancel',

        'version',
        'checkupdate',

        'transprancy',
        'audio',
        'reverse',
        'delay',
        'standard_method',

        'redside',
        'blackside',

        'red_engine',
        'black_engine',

        'mode',

        'red_depth',
        'black_depth',

        'red_time',
        'black_time',

        'red_steps',
        'black_steps',

        'red_increment',
        'black_increment',
    }

    SETTINGS = {
        'transprancy': 0,
        'audio': True,
        'reverse': False,
        'delay': 300,
        'standard_method': False,

        'redside': 0,
        'blackside': 0,

        'red_engine': 0,
        'black_engine': 0,

        'mode': 0,

        'red_depth': 7,
        'black_depth': 1,

        'red_time': 5000,
        'black_time': 5000,

        'red_steps': 200,
        'black_steps': 200,

        'red_increment': 3000,
        'black_increment': 3000,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = settings.Ui_Dialog()
        self.ui.setupUi(self)

        # 去掉标题栏问号
        flags = QtCore.Qt.Dialog
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)

        # 设置标题
        self.setWindowTitle("设置")

        self.setStyleSheet("font-family: dengxian;")

        for name in self.ATTRIBUTES:
            attr = getattr(self.ui, name)
            setattr(self, name, attr)
            logger.info("set settings attr %s object %s", name, attr)

        self.version.setText(f"v{VERSION}")
        self.checkupdate.clicked.connect(self.check_update)

        self.ok.clicked.connect(self.save)

        self.ok.clicked.connect(self.close)
        self.cancel.clicked.connect(self.close)
        self.cancel.clicked.connect(lambda: self.set_settings(self.backup))
        self.mode.currentIndexChanged.connect(self.update_mode)
        self.update_mode(0)

        self.setup_engines()

    @QtCore.Slot(int)
    def update_mode(self, idx):
        if idx == 0:
            # 深度制
            self.red_depth.setEnabled(True)
            self.black_depth.setEnabled(True)
            self.red_time.setEnabled(False)
            self.black_time.setEnabled(False)
            self.red_steps.setEnabled(False)
            self.black_steps.setEnabled(False)
            self.red_increment.setEnabled(False)
            self.black_increment.setEnabled(False)
        elif idx == 1:
            #  加时制
            self.red_depth.setEnabled(False)
            self.black_depth.setEnabled(False)
            self.red_time.setEnabled(True)
            self.black_time.setEnabled(True)
            self.red_steps.setEnabled(False)
            self.black_steps.setEnabled(False)
            self.red_increment.setEnabled(True)
            self.black_increment.setEnabled(True)
            pass
        elif idx == 2:
            # 时段制
            self.red_depth.setEnabled(False)
            self.black_depth.setEnabled(False)
            self.red_time.setEnabled(True)
            self.black_time.setEnabled(True)
            self.red_steps.setEnabled(True)
            self.black_steps.setEnabled(True)
            self.red_increment.setEnabled(False)
            self.black_increment.setEnabled(False)

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
            else:
                raise Exception(str(attr))

    def go_params(self, turn):
        idx = self.mode.currentIndex()
        params = attrdict()
        if idx == 0:
            # 深度制
            if turn == Chess.RED:
                params.depth = self.red_depth.value()
            else:
                params.depth = self.black_depth.value()
        elif idx == 1:
            #  加时制
            if turn == Chess.RED:
                params.time = self.red_time.value()
                params.increment = self.red_increment.value()
                params.opptime = self.black_time.value()
                params.oppincrement = self.black_increment.value()
            else:
                params.time = self.black_time.value()
                params.increment = self.black_increment.value()
                params.opptime = self.red_time.value()
                params.oppincrement = self.red_increment.value()
        elif idx == 2:
            # 时段制
            if turn == Chess.RED:
                params.time = self.red_time.value()
                params.movestogo = self.red_steps.value()
                params.opptime = self.black_time.value()
                params.oppmovestogo = self.black_steps.value()
            else:
                params.time = self.black_time.value()
                params.movestogo = self.black_steps.value()
                params.opptime = self.red_time.value()
                params.oppmovestogo = self.red_steps.value()
        else:
            raise Exception("invalid engine mode")
        return params

    def loads(self):
        import json
        filename = self.get_filename()
        settings = self.get_default()

        if os.path.exists(filename):
            with open(filename, encoding='utf8') as file:
                source = file.read()

            try:
                data = json.loads(source)
                data = attrdict.loads(data)
                settings.update(data)
            except Exception:
                pass

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

        self.engine = None
        self.standard = False

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


def main():
    app = QtWidgets.QApplication()
    # window = Method()
    window = Settings()
    # window._test_signal()
    window.loads()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
