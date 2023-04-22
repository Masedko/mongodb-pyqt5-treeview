import logging
from typing import Any

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pymongo.errors import OperationFailure

from models.model import Model
from logger.logger import error_message_box
from models.StandardItem import StandardItem, TypeOfStandardItem


class TreeModel(QStandardItemModel):
    def __init__(self, model_db: Model):
        super().__init__()
        self._model_db = model_db

    def itemFromIndex(self, index: QModelIndex) -> QStandardItem | StandardItem | None:
        item = super().itemFromIndex(index)
        if item is not None:
            return item
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole:
            return super().setData(index, value, role)
        if not index.isValid():
            return super().setData(index, value, role)

        item = self.itemFromIndex(index)
        if item.text() == value:
            return super().setData(index, self.itemFromIndex(index).text(), role)

        try:
            match item.getTypeOfItem():
                case TypeOfStandardItem.COLLECTION:
                    if self._model_db.rename_collection(self.itemFromIndex(index).text(), value):
                        logging.info(f"Rename collection from {item.text()} to {value} completed")
                    else:
                        logging.warning(f"Rename collection from {item.text()} to {value} went wrong")
                case TypeOfStandardItem.OBJECT_KEY:
                    document: QStandardItem = item.parent()
                    collection: QStandardItem = document.parent()
                    self._model_db.rename_field(document.getId(), collection.text(), item.text(), value)
                    logging.info(f"Rename field from {item.text()} to {value} completed")
                case TypeOfStandardItem.OBJECT_VALUE:
                    key: QStandardItem = item.parent()
                    document: QStandardItem = key.parent()
                    collection: QStandardItem = document.parent()
                    self._model_db.update_entry(document.getId(), {key.text(): value}, collection.text())
                    logging.info(f"Value update from {item.text()} to {value} completed")
        except OperationFailure:
            error_message_box("Operation Failure")
            logging.warning("Operation Failure")
            return super().setData(index, self.itemFromIndex(index).text(), role)

        return super().setData(index, value, role)
