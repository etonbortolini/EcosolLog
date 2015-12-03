# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EcosolLog_dialog_base.ui'
#
# Created: Tue Sep  8 20:22:06 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_EcosolLogDialogBase(object):
    def setupUi(self, EcosolLogDialogBase):
        EcosolLogDialogBase.setObjectName(_fromUtf8("EcosolLogDialogBase"))
        EcosolLogDialogBase.resize(400, 300)
        self.button_box = QtGui.QDialogButtonBox(EcosolLogDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))

        self.retranslateUi(EcosolLogDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), EcosolLogDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), EcosolLogDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(EcosolLogDialogBase)

    def retranslateUi(self, EcosolLogDialogBase):
        EcosolLogDialogBase.setWindowTitle(_translate("EcosolLogDialogBase", "EcosolLog", None))

