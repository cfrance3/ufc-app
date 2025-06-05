import sqlite3
import random

class DatabaseManager:
    def __init__(self, db_path="ufc_info.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_random_fight(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT 
                            f.id AS fight_id,
                            f1.name AS fighter1_name,
                            f2.name AS fighter2_name,
                            f1.height AS fighter1_height,
                            f2.height AS fighter2_height,
                            f1.weight AS fighter1_weight,
                            f2.weight AS fighter2_weight,
                            f1.stance AS fighter1_stance,
                            f2.stance AS fighter2_stance,
                            winner.name AS winner,
                            e.name AS event_name,
                            e.date AS date
                       FROM fight as f
                       JOIN fighter AS f1 ON f.fighter1_id = f1.id
                       JOIN fighter AS f2 ON f.fighter2_id = f2.id
                       JOIN fighter AS winner ON f.winner_id = winner.id
                       JOIN event AS e ON f.event_id = e.id
                       ''')
        fights = cursor.fetchall()
        return fights and dict(random.choice(fights)) or None
    
    def query(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()
        