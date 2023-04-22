from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QLineEdit


class AddFieldValueWidget(QtWidgets.QWidget):
    def __init__(self):
        super(AddFieldValueWidget, self).__init__()
        self.lineEditField: QLineEdit | None = None
        self.lineEditValue: QLineEdit | None = None
        self.pushButton: QPushButton | None = None
        uic.loadUi('views/widgets/AddFieldValue.ui', self)
