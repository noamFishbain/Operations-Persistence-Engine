# Import the specialized drivers
from .postgres_driver import PostgresDriver
from .mongo_driver import MongoDriver


class DBManager:
    def __init__(self):
        # Initialize the drivers
        self.postgres = PostgresDriver()
        self.mongo = MongoDriver()

    def save_operation(self, flavor, operation, result, arguments):
        """
        Orchestrates saving the operation to both databases.
        1. Gets the next ID from Postgres (Source of Truth).
        2. Saves to Postgres.
        3. Saves to Mongo.
        """
        # Step 1: Generate a unique ID
        new_id = self.postgres.get_next_id()

        # Step 2: Save to Postgres
        self.postgres.insert_operation(new_id, flavor, operation, result, arguments)

        # Step 3: Save to Mongo
        self.mongo.insert_operation(new_id, flavor, operation, result, arguments)

    def fetch_history(self, persistence_method):
        """
        Routes the fetch request to the correct driver based on user input.
        """
        if persistence_method == "POSTGRES":
            return self.postgres.get_all_operations()
        elif persistence_method == "MONGO":
            return self.mongo.get_all_operations()
        else:
            return []