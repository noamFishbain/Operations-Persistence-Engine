import os
import psycopg2
import json

class PostgresDriver:
    def __init__(self):
        # Configuration for Postgres connection
        self.host = os.environ.get('POSTGRES_HOST', 'localhost')
        self.port = 5432
        self.user = "postgres"
        self.password = "docker"
        self.db_name = "operations"
        self.table_name = "operations"

    def get_connection(self):
        """Establishes a connection to the Postgres database."""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.db_name,
            user=self.user,
            password=self.password
        )

    def get_next_id(self):
        """Calculates the next unique ID based on the maximum existing ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT MAX(rawid) FROM {self.table_name}")
            max_id = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return 1 if max_id is None else max_id + 1
        except Exception as e:
            print(f"Error generating ID in Postgres: {e}")
            return 1

    def insert_operation(self, raw_id, flavor, operation, result, arguments):
        """Inserts a new operation record into the table."""
        args_str = json.dumps(arguments)
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = f"INSERT INTO {self.table_name} (rawid, flavor, operation, result, arguments) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (raw_id, flavor, operation, result, args_str))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error saving to Postgres: {e}")

    def get_all_operations(self):
        """Fetches all operation records."""
        history = []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT rawid, flavor, operation, result, arguments FROM {self.table_name}")
            rows = cursor.fetchall()
            for row in rows:
                history.append({
                    "id": row[0],
                    "flavor": row[1],
                    "operation": row[2],
                    "result": row[3],
                    "arguments": json.loads(row[4])
                })
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching from Postgres: {e}")
        return history