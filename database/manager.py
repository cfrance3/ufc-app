import sqlite3
import random

class DatabaseManager:
    def __init__(self, db_path="../ufc_info.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_random_fight(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM fights")
        fights = cursor.fetchall()
        return fights and dict(random.choice(fights)) or None
    
    def query(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()
        