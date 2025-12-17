import os
from pymongo import MongoClient
import json

class MongoDriver:
    def __init__(self):
        # Configuration for Mongo connection
        self.host = os.environ.get('MONGO_HOST', 'localhost')
        self.port = 27017
        self.db_name = "calculator"
        self.collection_name = "calculator"

    def get_collection(self):
        """Establishes a connection and returns the Mongo collection."""
        client = MongoClient(f"mongodb://{self.host}:{self.port}/")
        db = client[self.db_name]
        return db[self.collection_name]

    def insert_operation(self, raw_id, flavor, operation, result, arguments):
        """Inserts a new document into the collection."""
        args_str = json.dumps(arguments)
        try:
            collection = self.get_collection()
            document = {
                "rawid": raw_id,
                "flavor": flavor,
                "operation": operation,
                "result": result,
                "arguments": args_str
            }
            collection.insert_one(document)
        except Exception as e:
            print(f"Error saving to Mongo: {e}")

    def get_all_operations(self):
        """Fetches all documents from the collection."""
        history = []
        try:
            collection = self.get_collection()
            cursor = collection.find({}, {"_id": 0})
            for doc in cursor:
                doc["id"] = doc.pop("rawid")
                doc["arguments"] = json.loads(doc["arguments"])
                history.append(doc)
        except Exception as e:
            print(f"Error fetching from Mongo: {e}")
        return history