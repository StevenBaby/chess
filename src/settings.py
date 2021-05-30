# coding=utf-8

from PySide2 import QtCore
from PySide2 import QtWidgets
from ui.settings import Ui_Dialog
from version import VERSION

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

    def check_update(self):
        import webbrowser
        webbrowser.open(UPDATE_URL)

    def _test_signal(self):
        self.ui.buttonBox.accepted.connect(lambda: print('accepted'))
        self.ui.buttonBox.rejected.connect(lambda: print('rejected'))
        self.ui.transprancy.valueChanged.connect(
            lambda e: (print(e), self.setWindowOpacity((100 - e) / 100)))
        self.reverse.stateChanged.connect(
            lambda e: print(e)
        )


def main():
    app = QtWidgets.QApplication()
    window = Settings()
    window._test_signal()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
