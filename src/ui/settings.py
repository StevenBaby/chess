# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGridLayout, QLabel, QPushButton, QSizePolicy,
    QSlider, QSpinBox, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(489, 379)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.red_engine = QComboBox(Dialog)
        self.red_engine.setObjectName(u"red_engine")
        font = QFont()
        font.setFamilies([u"DengXian"])
        font.setPointSize(14)
        self.red_engine.setFont(font)

        self.gridLayout.addWidget(self.red_engine, 5, 1, 1, 1)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 4, 2, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.cancel = QPushButton(Dialog)
        self.cancel.setObjectName(u"cancel")
        self.cancel.setFont(font)

        self.gridLayout.addWidget(self.cancel, 10, 3, 1, 1)

        self.animate = QCheckBox(Dialog)
        self.animate.setObjectName(u"animate")
        self.animate.setChecked(True)

        self.gridLayout.addWidget(self.animate, 3, 1, 1, 1)

        self.redside = QComboBox(Dialog)
        self.redside.addItem("")
        self.redside.addItem("")
        self.redside.setObjectName(u"redside")
        self.redside.setFont(font)

        self.gridLayout.addWidget(self.redside, 4, 1, 1, 1)

        self.label_20 = QLabel(Dialog)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setFont(font)
        self.label_20.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_20, 3, 0, 1, 1)

        self.label_7 = QLabel(Dialog)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_7, 6, 2, 1, 1)

        self.ok = QPushButton(Dialog)
        self.ok.setObjectName(u"ok")
        self.ok.setFont(font)

        self.gridLayout.addWidget(self.ok, 10, 2, 1, 1)

        self.blackside = QComboBox(Dialog)
        self.blackside.addItem("")
        self.blackside.addItem("")
        self.blackside.setObjectName(u"blackside")
        self.blackside.setFont(font)

        self.gridLayout.addWidget(self.blackside, 4, 3, 1, 1)

        self.black_depth = QSpinBox(Dialog)
        self.black_depth.setObjectName(u"black_depth")
        self.black_depth.setFont(font)
        self.black_depth.setMaximum(10)
        self.black_depth.setValue(1)

        self.gridLayout.addWidget(self.black_depth, 7, 3, 1, 1)

        self.label_8 = QLabel(Dialog)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font)
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_8, 7, 0, 1, 1)

        self.label_12 = QLabel(Dialog)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setFont(font)
        self.label_12.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_12, 5, 2, 1, 1)

        self.transprancy = QSlider(Dialog)
        self.transprancy.setObjectName(u"transprancy")
        font1 = QFont()
        font1.setFamilies([u"DengXian"])
        font1.setPointSize(12)
        self.transprancy.setFont(font1)
        self.transprancy.setMinimum(0)
        self.transprancy.setMaximum(75)
        self.transprancy.setOrientation(Qt.Horizontal)
        self.transprancy.setTickPosition(QSlider.NoTicks)
        self.transprancy.setTickInterval(0)

        self.gridLayout.addWidget(self.transprancy, 0, 1, 1, 3)

        self.delay = QSpinBox(Dialog)
        self.delay.setObjectName(u"delay")
        self.delay.setFont(font)
        self.delay.setMaximum(5000)
        self.delay.setValue(300)

        self.gridLayout.addWidget(self.delay, 6, 3, 1, 1)

        self.version = QLabel(Dialog)
        self.version.setObjectName(u"version")
        self.version.setFont(font)
        self.version.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.version, 9, 1, 1, 1)

        self.red_depth = QSpinBox(Dialog)
        self.red_depth.setObjectName(u"red_depth")
        self.red_depth.setFont(font)
        self.red_depth.setMaximum(10)
        self.red_depth.setValue(7)

        self.gridLayout.addWidget(self.red_depth, 7, 1, 1, 1)

        self.label_11 = QLabel(Dialog)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font)
        self.label_11.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_11, 5, 0, 1, 1)

        self.mode = QComboBox(Dialog)
        self.mode.addItem("")
        self.mode.addItem("")
        self.mode.setObjectName(u"mode")
        self.mode.setFont(font)

        self.gridLayout.addWidget(self.mode, 6, 1, 1, 1)

        self.label_13 = QLabel(Dialog)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font)
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_13, 6, 0, 1, 1)

        self.checkupdate = QPushButton(Dialog)
        self.checkupdate.setObjectName(u"checkupdate")
        self.checkupdate.setFont(font)

        self.gridLayout.addWidget(self.checkupdate, 9, 3, 1, 1)

        self.label_9 = QLabel(Dialog)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font)
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_9, 7, 2, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.black_engine = QComboBox(Dialog)
        self.black_engine.setObjectName(u"black_engine")
        self.black_engine.setFont(font)

        self.gridLayout.addWidget(self.black_engine, 5, 3, 1, 1)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 9, 0, 1, 1)

        self.red_time = QSpinBox(Dialog)
        self.red_time.setObjectName(u"red_time")
        self.red_time.setFont(font)
        self.red_time.setMaximum(100000)
        self.red_time.setValue(7)

        self.gridLayout.addWidget(self.red_time, 8, 1, 1, 1)

        self.reverse = QCheckBox(Dialog)
        self.reverse.setObjectName(u"reverse")

        self.gridLayout.addWidget(self.reverse, 2, 1, 1, 1)

        self.label_14 = QLabel(Dialog)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setFont(font)
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_14, 8, 0, 1, 1)

        self.standard_method = QCheckBox(Dialog)
        self.standard_method.setObjectName(u"standard_method")
        self.standard_method.setChecked(False)

        self.gridLayout.addWidget(self.standard_method, 2, 3, 1, 1)

        self.black_time = QSpinBox(Dialog)
        self.black_time.setObjectName(u"black_time")
        self.black_time.setFont(font)
        self.black_time.setMaximum(100000)
        self.black_time.setValue(1)

        self.gridLayout.addWidget(self.black_time, 8, 3, 1, 1)

        self.label_15 = QLabel(Dialog)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setFont(font)
        self.label_15.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_15, 8, 2, 1, 1)

        self.audio = QCheckBox(Dialog)
        self.audio.setObjectName(u"audio")
        self.audio.setChecked(True)

        self.gridLayout.addWidget(self.audio, 3, 3, 1, 1)

        self.label_10 = QLabel(Dialog)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font)
        self.label_10.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_10, 2, 2, 1, 1)

        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_6, 3, 2, 1, 1)

        self.label_16 = QLabel(Dialog)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setFont(font)
        self.label_16.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_16, 1, 0, 1, 1)

        self.ontop = QCheckBox(Dialog)
        self.ontop.setObjectName(u"ontop")

        self.gridLayout.addWidget(self.ontop, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u9ed1\u65b9", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u900f\u660e\u5ea6", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u53d6\u6d88", None))
        self.animate.setText("")
        self.redside.setItemText(0, QCoreApplication.translate("Dialog", u"\u68cb\u624b", None))
        self.redside.setItemText(1, QCoreApplication.translate("Dialog", u"\u7535\u8111", None))

        self.label_20.setText(QCoreApplication.translate("Dialog", u"\u542f\u7528\u52a8\u753b", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"\u5f15\u64ce\u5ef6\u8fdf", None))
        self.ok.setText(QCoreApplication.translate("Dialog", u"\u786e\u8ba4", None))
        self.blackside.setItemText(0, QCoreApplication.translate("Dialog", u"\u7535\u8111", None))
        self.blackside.setItemText(1, QCoreApplication.translate("Dialog", u"\u68cb\u624b", None))

        self.label_8.setText(QCoreApplication.translate("Dialog", u"\u7ea2\u65b9\u6df1\u5ea6", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"\u9ed1\u65b9\u5f15\u64ce", None))
        self.version.setText(QCoreApplication.translate("Dialog", u"1.1.0", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"\u7ea2\u65b9\u5f15\u64ce", None))
        self.mode.setItemText(0, QCoreApplication.translate("Dialog", u"\u6df1\u5ea6\u5236", None))
        self.mode.setItemText(1, QCoreApplication.translate("Dialog", u"\u9650\u65f6\u5236", None))

        self.label_13.setText(QCoreApplication.translate("Dialog", u"\u601d\u8003\u6a21\u5f0f", None))
        self.checkupdate.setText(QCoreApplication.translate("Dialog", u"\u68c0\u67e5\u66f4\u65b0", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"\u9ed1\u65b9\u6df1\u5ea6", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u53cd\u8f6c\u68cb\u76d8", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u7ea2\u65b9", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u7248\u672c\u53f7", None))
        self.reverse.setText("")
        self.label_14.setText(QCoreApplication.translate("Dialog", u"\u7ea2\u65b9\u65f6\u95f4", None))
        self.standard_method.setText("")
        self.label_15.setText(QCoreApplication.translate("Dialog", u"\u9ed1\u65b9\u65f6\u95f4", None))
        self.audio.setText("")
        self.label_10.setText(QCoreApplication.translate("Dialog", u"\u6807\u51c6\u7740\u6cd5", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"\u97f3\u6548", None))
        self.label_16.setText(QCoreApplication.translate("Dialog", u"\u603b\u662f\u5728\u4e0a", None))
        self.ontop.setText("")
    # retranslateUi

