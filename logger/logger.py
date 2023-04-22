import logging
import sys

from PyQt5.QtWidgets import QPlainTextEdit, QMessageBox
from logging import Handler, LogRecord


class Logger(Handler):
    def __init__(self, parent: QPlainTextEdit) -> None:
        super().__init__()
        self._text_edit = parent
        self._text_edit.setReadOnly(True)

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        self._text_edit.appendPlainText(msg)


def error_message_box(text, window_title="Error", should_abort=False):
    """Надрукувати текст в лог та зобразити Message Box про помилку"""
    message_box = QMessageBox()
    message_box.setText(text)
    message_box.setIcon(QMessageBox.Critical)
    message_box.setWindowTitle(window_title)
    message_box.exec_()
    logging.error(text)
    if should_abort:
        sys.exit(1)
