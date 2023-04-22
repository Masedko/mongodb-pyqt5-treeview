from enum import Enum
from PyQt5.QtGui import QStandardItem, QFont
from bson import ObjectId


class TypeOfStandardItem(Enum):
    ROOT = 1
    COLLECTION = 2
    DOCUMENT = 3
    OBJECT_KEY = 4
    OBJECT_VALUE = 5


class StandardItem(QStandardItem):
    def __init__(self, text: str = '',
                 type_of_item: TypeOfStandardItem = TypeOfStandardItem.OBJECT_VALUE,
                 item_id: ObjectId = None, collection_name: str = None, font: str = 'MS Shell Dlg 2'):
        super(StandardItem, self).__init__()
        self._appendEnabled = None
        self._id = item_id
        self._collection_name = collection_name
        self._typeOfItem = type_of_item
        self.setText(text)
        match self._typeOfItem:
            case TypeOfStandardItem.ROOT:
                self.setEditable(False)
                self.setDropEnabled(False)
                self.setAppendEnabled(True)
            case TypeOfStandardItem.COLLECTION:
                self.setEditable(True)
                self.setDropEnabled(True)
                self.setAppendEnabled(True)
            case TypeOfStandardItem.DOCUMENT:
                self.setEditable(False)
                self.setDropEnabled(True)
                self.setAppendEnabled(True)
            case TypeOfStandardItem.OBJECT_KEY:
                self.setEditable(True)
                self.setDropEnabled(True)
                self.setAppendEnabled(False)
            case TypeOfStandardItem.OBJECT_VALUE:
                self.setEditable(True)
                self.setDropEnabled(False)
                self.setAppendEnabled(False)
        font_sizes = {
            TypeOfStandardItem.ROOT: 18,
            TypeOfStandardItem.COLLECTION: 16,
            TypeOfStandardItem.DOCUMENT: 14,
            TypeOfStandardItem.OBJECT_KEY: 12,
            TypeOfStandardItem.OBJECT_VALUE: 12
        }
        font = QFont(font, font_sizes[self._typeOfItem])
        self.setFont(font)
    # Not PEP8 because of PyQt5 style
    def setAppendEnabled(self, append_enabled: bool):
        self._appendEnabled = append_enabled

    def isAppendEnabled(self) -> bool:
        return self._appendEnabled

    def getTypeOfItem(self) -> TypeOfStandardItem:
        return self._typeOfItem

    def getCollectionName(self) -> str:
        return self._collection_name

    def getId(self) -> ObjectId:
        return self._id
