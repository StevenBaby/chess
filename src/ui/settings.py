# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(440, 224)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(20)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamily(u"DengXian")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 2, 3, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.redside = QComboBox(Dialog)
        self.redside.addItem("")
        self.redside.addItem("")
        self.redside.setObjectName(u"redside")
        self.redside.setFont(font)

        self.gridLayout.addWidget(self.redside, 2, 2, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setFont(font)
        self.buttonBox.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 4, 3, 1, 2)

        self.transprancy = QSlider(Dialog)
        self.transprancy.setObjectName(u"transprancy")
        font1 = QFont()
        font1.setFamily(u"DengXian")
        font1.setPointSize(12)
        self.transprancy.setFont(font1)
        self.transprancy.setMinimum(0)
        self.transprancy.setMaximum(75)
        self.transprancy.setOrientation(Qt.Horizontal)
        self.transprancy.setTickPosition(QSlider.NoTicks)
        self.transprancy.setTickInterval(0)

        self.gridLayout.addWidget(self.transprancy, 0, 2, 1, 2)

        self.blackside = QComboBox(Dialog)
        self.blackside.addItem("")
        self.blackside.addItem("")
        self.blackside.setObjectName(u"blackside")
        self.blackside.setFont(font)

        self.gridLayout.addWidget(self.blackside, 2, 4, 1, 1)

        self.reverse = QCheckBox(Dialog)
        self.reverse.setObjectName(u"reverse")

        self.gridLayout.addWidget(self.reverse, 1, 2, 1, 2)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.version = QLabel(Dialog)
        self.version.setObjectName(u"version")
        self.version.setFont(font)
        self.version.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.version, 3, 2, 1, 2)

        self.checkupdate = QPushButton(Dialog)
        self.checkupdate.setObjectName(u"checkupdate")
        self.checkupdate.setFont(font)

        self.gridLayout.addWidget(self.checkupdate, 3, 4, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u900f\u660e\u5ea6", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u7ea2\u65b9", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u9ed1\u65b9", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u53cd\u8f6c\u68cb\u76d8", None))
        self.redside.setItemText(0, QCoreApplication.translate("Dialog", u"\u68cb\u624b", None))
        self.redside.setItemText(1, QCoreApplication.translate("Dialog", u"\u7535\u8111", None))

        self.blackside.setItemText(0, QCoreApplication.translate("Dialog", u"\u7535\u8111", None))
        self.blackside.setItemText(1, QCoreApplication.translate("Dialog", u"\u68cb\u624b", None))

        self.reverse.setText("")
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u7248\u672c\u53f7", None))
        self.version.setText(QCoreApplication.translate("Dialog", u"1.1.0", None))
        self.checkupdate.setText(QCoreApplication.translate("Dialog", u"\u68c0\u67e5\u66f4\u65b0", None))
    # retranslateUi

