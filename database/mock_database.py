import sqlite3
from sqlite3 import Error
import os
from database.mock_data_model import Player
MOCK_DATABASE_PATH = "mock.db"

class MockDatabase:
    
    def __init__(self):
        self.conn = MockDatabase.create_connection(MOCK_DATABASE_PATH)
        
    @staticmethod
    def create_connection(database_path):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(database_path)
        except Error as e:
            print(e)

        return conn
    
    def close_connection(self):
        """ Close database connection. Call at end of script"""
        self.conn.close()

if __name__ == '__main__':
    db = MockDatabase()
    Player.create_table(db.conn)