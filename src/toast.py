'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-06-22
'''

import threading

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

from logger import logger


class ToastSignal(QtCore.QObject):

    close = QtCore.Signal(None)


class Toast(QtWidgets.QWidget):
    BACKGROUND_COLOR = QtGui.QColor("#22000000")
    FOREGROUND_COLOR = QtGui.QColor("#db2828")

    font = QtGui.QFont('dengxian', 18, QtGui.QFont.Bold)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.painter = None
        self.timeout = 2
        self.text = ''
        self.pen = QtGui.QPen(QtGui.QColor(self.FOREGROUND_COLOR))
        self.signal = ToastSignal(self)
        self.signal.close.connect(self.close)

    def resize(self):
        size = self.font.pointSizeF()
        border = size

        height = size + border * 2
        width = size * len(self.text) * 2 + border * 2

        if not self.parentWidget():
            screen = QtGui.QGuiApplication.primaryScreen()
            geo = screen.geometry()
        else:
            geo = self.parentWidget().geometry()

        x = (geo.width() - width) // 2
        y = (geo.height() - height) // 2
        if self.parentWidget():
            x += geo.x()
            y += geo.y()

        self.setGeometry(QtCore.QRect(x, y, width, height))

    def paintEvent(self, event):
        radius = int(self.font.pointSizeF() / 2)

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        painter.setPen(self.pen)
        painter.setFont(self.font)

        rectpath = QtGui.QPainterPath()

        rect = QtCore.QRectF(0, 0, self.width(), self.height())
        rectpath.addRoundedRect(rect, radius, radius, QtCore.Qt.AbsoluteSize)

        painter.fillPath(rectpath, QtGui.QColor(self.BACKGROUND_COLOR))
        painter.drawText(QtCore.QRectF(0, 0, self.width(), self.height()), QtCore.Qt.AlignCenter, self.text)
        painter.end()

    def message(self, text, timeout=None):
        if not text:
            return
        if not timeout:
            timeout = self.timeout

        logger.info("toast message %s", text)

        self.text = text

        self.resize()
        self.repaint()
        self.show()

        timer = threading.Timer(timeout, lambda: self.signal.close.emit())
        timer.start()

    def close(self):
        # logger.info('toast close parent %s...', self.parentWidget())
        super().close()
        if self.parentWidget() is None:
            # logger.info("toast quit...")
            QtCore.QCoreApplication.quit()


if __name__ == '__main__':
    import sys
    # QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    toast = Toast()
    toast.message("Hello")

    sys.exit(app.exec())
