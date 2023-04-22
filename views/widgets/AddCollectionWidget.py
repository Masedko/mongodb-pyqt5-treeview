from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QLineEdit


class AddCollectionWidget(QtWidgets.QWidget):
    def __init__(self):
        super(AddCollectionWidget, self).__init__()
        self.lineEdit: QLineEdit | None = None
        self.pushButton: QPushButton | None = None
        uic.loadUi('views/widgets/AddCollection.ui', self)
