# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'method.ui'
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
        Dialog.resize(240, 609)
        Dialog.setMinimumSize(QSize(240, 0))
        Dialog.setMaximumSize(QSize(240, 16777215))
        Dialog.setSizeIncrement(QSize(0, 0))
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listwidget = QListWidget(Dialog)
        brush = QBrush(QColor(255, 0, 0, 255))
        brush.setStyle(Qt.NoBrush)
        brush1 = QBrush(QColor(255, 0, 0, 255))
        brush1.setStyle(Qt.NoBrush)
        __qlistwidgetitem = QListWidgetItem(self.listwidget)
        __qlistwidgetitem.setText(u"New Item");
        __qlistwidgetitem.setBackground(brush1);
        __qlistwidgetitem.setForeground(brush);
        self.listwidget.setObjectName(u"listwidget")
        font = QFont()
        font.setFamily(u"DengXian")
        font.setPointSize(14)
        self.listwidget.setFont(font)
        self.listwidget.setProperty("showDropIndicator", False)
        self.listwidget.setSpacing(5)
        self.listwidget.setViewMode(QListView.ListMode)

        self.verticalLayout.addWidget(self.listwidget)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u7740\u6cd5", None))

        __sortingEnabled = self.listwidget.isSortingEnabled()
        self.listwidget.setSortingEnabled(False)
        self.listwidget.setSortingEnabled(__sortingEnabled)

    # retranslateUi

