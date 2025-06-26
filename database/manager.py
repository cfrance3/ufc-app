import sqlite3
import random

class DatabaseManager:
    def __init__(self, db_path="ufc_info.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_random_fight(self):
        cursor = self.conn.cursor()
        try:
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
                            f.fighter1_sig_strikes AS fighter1_sig_strikes,
                            f.fighter2_sig_strikes AS fighter2_sig_strikes,
                            f.fighter1_sig_strikes_att AS fighter1_sig_strikes_att,
                            f.fighter2_sig_strikes_att AS fighter2_sig_strikes_att,
                            f.fighter1_total_strikes AS fighter1_total_strikes,
                            f.fighter2_total_strikes AS fighter2_total_strikes,
                            f.fighter1_total_strikes_att AS fighter1_total_strikes_att,
                            f.fighter2_total_strikes_att AS fighter2_total_strikes_att,
                            f.fighter1_head_strikes AS fighter1_head_strikes,
                            f.fighter2_head_strikes AS fighter2_head_strikes,
                            f.fighter1_head_strikes_att AS fighter1_head_strikes_att,
                            f.fighter2_head_strikes_att AS fighter2_head_strikes_att,
                            f.fighter1_body_strikes AS fighter1_body_strikes,
                            f.fighter2_body_strikes AS fighter2_body_strikes,
                            f.fighter1_body_strikes_att AS fighter1_body_strikes_att,
                            f.fighter2_body_strikes_att AS fighter2_body_strikes_att,
                            f.fighter1_leg_strikes AS fighter1_leg_strikes,
                            f.fighter2_leg_strikes AS fighter2_leg_strikes,
                            f.fighter1_leg_strikes_att AS fighter1_leg_strikes_att,
                            f.fighter2_leg_strikes_att AS fighter2_leg_strikes_att,
                            f.fighter1_takedowns AS fighter1_takedowns,
                            f.fighter2_takedowns AS fighter2_takedowns,
                            f.fighter1_takedowns_att AS fighter1_takedowns_att,
                            f.fighter2_takedowns_att AS fighter2_takedowns_att,
                            f.fighter1_submissions_att AS fighter1_submissions_att,
                            f.fighter2_submissions_att AS fighter2_submissions_att,
                            f.fighter1_control_time AS fighter1_control_time,
                            f.fighter2_control_time AS fighter2_control_time,
                            f1.reach AS fighter1_reach,
                            f2.reach AS fighter2_reach,
                            wc.name AS weight_class,
                            winner.name AS winner,
                            f.method AS method,
                            e.name AS event_name,
                            e.date AS date,
                            f.title_fight AS title_fight
                       FROM fight as f
                       JOIN fighter AS f1 ON f.fighter1_id = f1.id
                       JOIN fighter AS f2 ON f.fighter2_id = f2.id
                       JOIN fighter AS winner ON f.winner_id = winner.id
                       JOIN event AS e ON f.event_id = e.id
                       JOIN weight_class as wc ON f.weight_class_id = wc.id
                       ''')
        except:
            return None
        fights = cursor.fetchall()
        
        return fights and dict(random.choice(fights)) or None
    
    def query(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def get_all_events(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM event ORDER BY date DESC")
        return [row["name"] for row in cursor.fetchall()]
    
    def search_events_by_name(self, name):
        cursor = self.conn.cursor()
        sql = "SELECT id, name, FROM event WHERE name LIKE ? ORDER BY name"
        cursor.execute(sql, (f"%{name}%",))
        return cursor.fetchall
    
    def close(self):
        self.conn.close()
        