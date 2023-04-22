import sys
from PyQt5.QtWidgets import QApplication
from views.MainWindow import MainWindow
from models.model import Model
from config import config_mongo_db


def main():
    app = QApplication(sys.argv)
    model = Model(config_mongo_db)
    widget = MainWindow(model)
    widget.show()
    app.exec_()


if __name__ == "__main__":
    main()
