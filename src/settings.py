# coding=utf-8

import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from ui.settings import Ui_Dialog
from version import VERSION
from attrdict import attrdict
from logger import logger

import system

UPDATE_URL = 'https://github.com/StevenBaby/chess/releases'


class Settings(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.buttonBox = self.ui.buttonBox
        self.transprancy = self.ui.transprancy
        self.reverse = self.ui.reverse
        self.redside = self.ui.redside
        self.blackside = self.ui.blackside
        self.version = self.ui.version
        self.checkupdate = self.ui.checkupdate
        self.audio = self.ui.audio
        self.delay = self.ui.delay

        self.version.setText(f"v{VERSION}")
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText('确认')
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setText('取消')
        self.checkupdate.clicked.connect(self.check_update)

        # 去掉标题栏问号
        flags = QtCore.Qt.Dialog
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)

        # 设置标题
        self.setWindowTitle("设置")

        self.ui.buttonBox.accepted.connect(self.save)

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

        logger.info("save settings %s", data)

        content = json.dumps(data, ensure_ascii=False, indent=4)
        with open(self.get_filename(), 'w', encoding='utf8') as file:
            file.write(content)

    def check_update(self):
        import webbrowser
        webbrowser.open(UPDATE_URL)

    def _test_signal(self):
        self.ui.buttonBox.accepted.connect(lambda: print('accepted'))
        self.ui.buttonBox.accepted.connect(lambda: print('accepted'))
        self.ui.buttonBox.rejected.connect(lambda: print('rejected'))
        self.ui.transprancy.valueChanged.connect(
            lambda e: (print(e), self.setWindowOpacity((100 - e) / 100)))
        self.reverse.stateChanged.connect(
            lambda e: print(e)
        )
        self.audio.stateChanged.connect(
            lambda e: print(e)
        )


def main():
    app = QtWidgets.QApplication()
    window = Settings()
    window._test_signal()
    window.loads()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
