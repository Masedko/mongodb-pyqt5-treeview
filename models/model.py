from pymongo import MongoClient
from bson.objectid import ObjectId


def get_documents(collection) -> list:
    """Get all entries from collection"""
    return [x for x in collection.find()]


class Model:
    def __init__(self, mongo_db: dict):
        """Load MongoDB config if config is empty loading default values"""
        self._client = MongoClient(mongo_db.get('host', 'localhost'), mongo_db.get('port', 27017))
        self._db = self._client[mongo_db.get('db_name', 'mongo-db')]
        self._collections = [self._db[i] for i in self._db.list_collection_names()]

    def get_document_of_collections(self):
        """Get all documents from all collections"""
        return {collection.name: get_documents(collection) for collection in self._collections}

    def add_new_collection(self, collection_name: str) -> bool:
        """Add new collection by name"""
        if collection_name in self._db.list_collection_names():
            return False
        self._collections.append(self._db.create_collection(collection_name))
        return True

    def rename_collection(self, old_name: str, new_name: str) -> bool:
        """Rename collection"""
        self._db[old_name].rename(new_name)
        collection_names = self._db.list_collection_names()
        self._collections = [self._db[i] for i in self._db.list_collection_names()]
        if old_name not in collection_names and new_name in collection_names:
            return True
        else:
            return False

    def delete_collection(self, collection_name: str) -> bool:
        """Delete collection by name"""
        self._db[collection_name].drop()
        if collection_name in self._db.list_collection_names():
            return True
        else:
            return False

    def insert_entry(self, entry: dict, collection_name: str) -> ObjectId:
        """Insert entry into collection and get id of inserted entry"""
        return self._db[collection_name].insert_one(entry).inserted_id

    def delete_entry(self, object_id: ObjectId, collection_name: str) -> int:
        """Delete entry from collection and get deleted count to check if entry deleted"""
        id_filter = {'_id': object_id}
        return self._db[collection_name].delete_one(id_filter).deleted_count

    def update_entry(self, object_id: ObjectId, entry: dict, collection_name: str) -> ObjectId:
        """Update entry in collection using id and dictionary of new values and get id of inserted entry"""
        id_filter = {'_id': object_id}
        new_values = {'$set': entry}
        return self._db[collection_name].update_one(id_filter, new_values).upserted_id

    def rename_field(self, object_id: ObjectId, collection_name: str, old_name: str, new_name: str) -> ObjectId:
        """Rename field and get id of inserted entry"""
        id_filter = {'_id': object_id}
        rename_filter = {"$rename": {old_name: new_name}}
        return self._db[collection_name].update_one(id_filter, rename_filter).upserted_id
