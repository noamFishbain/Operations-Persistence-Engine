import os
import psycopg2
from pymongo import MongoClient
import json


# DBClient handles all interactions with Postgres and MongoDB
class DBClient:
    def __init__(self):
        # We use environment variables for host names so it works both locally and in Docker.
        # Defaults to 'localhost' for your local testing.
        self.postgres_host = os.environ.get('POSTGRES_HOST', 'localhost')
        self.mongo_host = os.environ.get('MONGO_HOST', 'localhost')

        # Postgres Config
        self.pg_user = "postgres"
        self.pg_pass = "docker"
        self.pg_db = "operations"
        self.pg_table = "operations"
        self.pg_port = 5432

        # Mongo Config
        self.mongo_port = 27017
        self.mongo_db_name = "calculator"
        self.mongo_col_name = "calculator"

    def get_postgres_connection(self):
        return psycopg2.connect(
            host=self.postgres_host,
            port=self.pg_port,
            database=self.pg_db,
            user=self.pg_user,
            password=self.pg_pass
        )

    def get_mongo_collection(self):
        client = MongoClient(f"mongodb://{self.mongo_host}:{self.mongo_port}/")
        db = client[self.mongo_db_name]
        return db[self.mongo_col_name]

    def get_next_id(self):
        """
        Calculates the next rawid to ensure sequential numbering starting from 1.
        We check Postgres MAX(rawid) as the source of truth.

        """
        try:
            conn = self.get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(rawid) FROM operations")
            max_id = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return 1 if max_id is None else max_id + 1
        except Exception as e:
            print(f"Error generating ID: {e}")
            return 1

    def save_operation(self, flavor, operation, result, arguments):
        """
        Saves the operation to BOTH Postgres and Mongo.

        """
        new_id = self.get_next_id()
        # Convert list arguments to JSON string string as required by the PDF schema
        args_str = json.dumps(arguments)

        # 1. Save to Postgres
        try:
            conn = self.get_postgres_connection()
            cursor = conn.cursor()
            query = "INSERT INTO operations (rawid, flavor, operation, result, arguments) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (new_id, flavor, operation, result, args_str))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error saving to Postgres: {e}")

        # 2. Save to Mongo
        try:
            collection = self.get_mongo_collection()
            # Note: We store rawid, but later retrieve it as 'id'
            document = {
                "rawid": new_id,
                "flavor": flavor,
                "operation": operation,
                "result": result,
                "arguments": args_str
            }
            collection.insert_one(document)
        except Exception as e:
            print(f"Error saving to Mongo: {e}")

    def fetch_history(self, persistence_method):
        """
        Fetches history from the specific DB requested by the user.

        """
        history = []

        # Helper function to parse arguments string back to list if needed,
        # though the client might expect the string representation.
        # Based on PDF examples, we usually return what we stored.

        if persistence_method == "POSTGRES":
            try:
                conn = self.get_postgres_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT rawid, flavor, operation, result, arguments FROM operations")
                rows = cursor.fetchall()
                for row in rows:
                    history.append({
                        "id": row[0],
                        "flavor": row[1],
                        "operation": row[2],
                        "result": row[3],
                        "arguments": json.loads(row[4])  # Convert string back to list/json for the response
                    })
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error fetching from Postgres: {e}")

        elif persistence_method == "MONGO":
            try:
                collection = self.get_mongo_collection()
                # Exclude internal _id
                cursor = collection.find({}, {"_id": 0})
                for doc in cursor:
                    # Rename rawid to id for the response
                    doc["id"] = doc.pop("rawid")
                    doc["arguments"] = json.loads(doc["arguments"])  # Convert string back to list
                    history.append(doc)
            except Exception as e:
                print(f"Error fetching from Mongo: {e}")

        return history