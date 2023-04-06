
import os

from database.mock_database import MOCK_DATABASE_PATH, MockDatabase
from database.mongo_database import MongoDBClient



def get_number_of_rows(table, c):
    c.execute(f"SELECT count(*) from {table}")
    num_rows = c.fetchone()
    return num_rows[0]

def get_mockdb_size():
    return os.path.getsize(MOCK_DATABASE_PATH)

def summarize_database(conn):
    c = conn.cursor()
    c.execute("SELECT name from sqlite_schema where type='table' order by name")
    tables = c.fetchall()
    for table, in tables:
        num_rows = get_number_of_rows(table, c)
        print(f"{table}: {num_rows} rows")
    print(f"Database size: {get_mockdb_size()} bytes")

def summarize_mongo(mongodb_client: MongoDBClient):
    matches_stats = mongodb_client.db.command("collstats", "matches")
    print(f"Uncompressed size: {matches_stats['size']}")
    print(f"Uncompressed size: {matches_stats['storageSize']}")
if __name__ == '__main__':
    database = MockDatabase()
    mongodb_client = MongoDBClient()
    summarize_database(database.conn)
    summarize_mongo(mongodb_client)
    