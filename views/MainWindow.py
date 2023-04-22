import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPlainTextEdit, QTreeView, QMenu, QAction, QPushButton, QFileDialog
from PyQt5.QtGui import QContextMenuEvent, QCursor
from bson import ObjectId
from bson.json_util import dumps
from views.widgets.AddCollectionWidget import AddCollectionWidget
from models.StandardItem import StandardItem, TypeOfStandardItem
from models.TreeModel import TreeModel
from logger.logger import Logger
from models.model import Model
import logging

from views.widgets.AddFieldValueWidget import AddFieldValueWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, model: Model):
        """Set Objects to none before loading from ui to make developing easier.
        Load models, widgets.
        Init menus, logger, QTreeView and TreeModel.
        Connect signal of button to add_collection_widget_show slot"""
        super(MainWindow, self).__init__()
        # All objects will be loaded from ui
        self._loggerTextEdit: QPlainTextEdit | None = None
        self._treeView: QTreeView | None = None
        self._treeModel: TreeModel | None = None
        self._newCollectionButton: QPushButton | None = None
        self._saveToJSONButton: QPushButton | None = None

        self._model_db = model

        self._collection_widget: AddCollectionWidget = AddCollectionWidget()
        self._field_value_widget: AddFieldValueWidget = AddFieldValueWidget()

        self._menu1 = QMenu(self)
        self._menu2 = QMenu(self)

        uic.loadUi('views/MainWindow.ui', self)

        self._newCollectionButton.clicked.connect(self.add_collection_widget_show)
        self._saveToJSONButton.clicked.connect(self.save_to_JSON)

        self.logger_init()
        self.tree_init()

        self.fill_menus()

    def add_collection_widget_show(self):
        self._collection_widget.show()
        self._collection_widget.pushButton.clicked.connect(self.add_collection)

    def add_collection(self):
        collection_name = self._collection_widget.lineEdit.text()
        if not self._model_db.add_new_collection(collection_name):
            logging.warning(f"Collection {collection_name} already exists")
            return
        root_node = self._treeModel.invisibleRootItem()
        root_node.appendRow(StandardItem(collection_name, type_of_item=TypeOfStandardItem.COLLECTION))
        self._collection_widget.close()
        logging.info(f"Collection {collection_name} added")

    def add_field_value_widget_show(self, parent_document: StandardItem):
        self._field_value_widget.show()
        # Check if signal connected to slot. If not -> connect()
        if not self._field_value_widget.pushButton.receivers(self._field_value_widget.pushButton.clicked) > 0:
            self._field_value_widget.pushButton.clicked.connect(lambda: self.add_field_value(parent_document))

    def add_field_value(self, parent_document: StandardItem):
        field = self._field_value_widget.lineEditField.text()
        value = self._field_value_widget.lineEditValue.text()
        key_item = StandardItem(field, type_of_item=TypeOfStandardItem.OBJECT_KEY)
        parent_document.appendRow(key_item)
        value_item = StandardItem(value, type_of_item=TypeOfStandardItem.OBJECT_VALUE)
        key_item.appendRow(value_item)
        parent_collection = parent_document.parent()
        self._field_value_widget.close()
        self._model_db.update_entry(parent_document.getId(), {field: value}, parent_collection.text())
        logging.info(f"Field {field} and value {value} added")

    def append_item(self):
        selection_model = self._treeView.selectionModel()
        indexes = selection_model.selectedIndexes()
        for index in indexes:
            item = self._treeModel.itemFromIndex(index)
            match item.getTypeOfItem():
                case TypeOfStandardItem.COLLECTION:
                    _id = self._model_db.insert_entry({}, item.text())
                    document_item = StandardItem(f"Document with id: {_id}", type_of_item=TypeOfStandardItem.DOCUMENT,
                                                 item_id=_id, collection_name=item.text())
                    item.appendRow(document_item)
                    logging.info(f"New document with id: {_id} appended to collection: {item.text()}")
                case TypeOfStandardItem.DOCUMENT:
                    self.add_field_value_widget_show(item)

    def delete_item(self):
        selection_model = self._treeView.selectionModel()
        indexes = selection_model.selectedIndexes()
        for index in indexes:
            item = self._treeModel.itemFromIndex(index)
            match item.getTypeOfItem():
                case TypeOfStandardItem.COLLECTION:
                    self._model_db.delete_collection(item.text())
                case TypeOfStandardItem.DOCUMENT:
                    if self._model_db.delete_entry(item.getId(), item.parent().text()) != 1:
                        logging.warning(f"No document with given id: {item.getId()}")
                    else:
                        logging.info(f"Deleted document with id: {item.getId()} from collection: {item.parent().text()}")
                case TypeOfStandardItem.OBJECT_KEY:
                    document = item.parent()
                    if self._model_db.delete_entry(document.getId(), document.parent().text()) != 1:
                        logging.warning(f"No document with given id: {document.getId()}")
                    logging.info(f"Deleted entry with value: {item.text()} from document: {item.parent().getId()}")
            self._treeModel.removeRow(index.row(), index.parent())

    def fill_menus(self):
        """Add actions to menus"""
        append_action = QAction('Append', self)
        delete_action = QAction('Delete', self)
        append_action.triggered.connect(self.append_item)
        delete_action.triggered.connect(self.delete_item)
        self._menu1.addAction(append_action)
        self._menu1.addAction(delete_action)
        self._menu2.addAction(delete_action)

    def logger_init(self):
        """Load Logger and give widget to work with. Add handler, set level and formatter """
        _logger = Logger(self._loggerTextEdit)
        _logger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(_logger)
        logging.getLogger().setLevel(logging.INFO)

    def tree_init(self):
        """Create TreeModel(that extends QTreeItemModel) and fill it with data using fill_update()"""
        self._treeModel = TreeModel(self._model_db)
        self.fill_tree()

    def fill_tree(self):
        """Fill TreeModel with data and connect TreeModel to QTreeView"""
        root_node = StandardItem("Collections", type_of_item=TypeOfStandardItem.ROOT)  # Create root node to append collections to it
        self._treeModel.appendRow(root_node)
        for collection_name, collection_entry in self._model_db.get_document_of_collections().items():
            # Append collections to root node
            collection_item = StandardItem(collection_name, type_of_item=TypeOfStandardItem.COLLECTION)
            root_node.appendRow(collection_item)
            for document in collection_entry:
                # Append documents to collections
                document_id = document.get('_id', 'NULL')
                document_object_id = ObjectId(document_id)
                document_item = StandardItem(f"Document with id: {document.get('_id', 'NULL')}",
                                             type_of_item=TypeOfStandardItem.DOCUMENT, item_id=document_object_id)
                if "_id" in document:
                    document.pop('_id')
                collection_item.appendRow(document_item)
                for field, value in document.items():
                    # Append documents with fields and values
                    field_item = StandardItem(str(field), type_of_item=TypeOfStandardItem.OBJECT_KEY)
                    value_item = StandardItem(str(value), type_of_item=TypeOfStandardItem.OBJECT_VALUE)
                    document_item.appendRow(field_item)
                    field_item.appendRow(value_item)
        self._treeView.setModel(self._treeModel)
        self._treeView.expandAll()

    def save_to_JSON(self):
        """Save JSON to file with QFileDialog"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        save_files = "All Files (*);;Text Files (*.txt);;JSON Files (*.json)"
        caption = "Save to JSON"
        full_path, _ = QFileDialog.getSaveFileName(self, caption, "", save_files, options=options)
        if not os.path.exists(full_path):
            return
        with open(full_path, 'w') as f:
            dump = dumps(self._model_db.get_document_of_collections())
            f.write(dump)
        filename = os.path.basename(full_path)
        logging.info(f"JSON stored in {filename}")

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Rewrite base class method to show right click menus"""
        index = self._treeView.indexAt(event.pos())  # Buggy interaction with QMenuBar, so use QPushButtons instead
        if not index.isValid():
            return
        item = self._treeView.model().itemFromIndex(index)
        # Do not show right click menu for StandardItem that has field dropEnabled = false
        if not item or not item.isDropEnabled():
            return
        # Show right click menu based on field appendEnabled of StandardItem
        if item.isAppendEnabled():
            self._menu1.popup(QCursor.pos())
        else:
            self._menu2.popup(QCursor.pos())
