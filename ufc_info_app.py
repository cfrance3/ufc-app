import tkinter as tk
import sqlite3
import csv
import re
from datetime import datetime

def main():
    root = tk.Tk()
    root.title("UFC Fighter Database")
    root.geometry("800x600")

    label = tk.Label(root, text="Welcome to the UFC Fighter Database!", font=("Helvetica", 16))
    label.pack(pady=200)

    root.mainloop()

def parse_height(height_str):
    if not height_str or '--' in height_str:
        return None
    match = re.match(r"(\d+)'\s*(\d+)", height_str)
    if match:
        feet = match.group(1)
        inches = match.group(2)
        return f"{feet}' {inches}\""
    return None

def parse_weight(weight_str):
    if not weight_str or '--' in weight_str:
        return None
    return int(weight_str.replace(' lbs.', '').strip())

def parse_reach(reach_str):
    if not reach_str or '--' in reach_str:
        return None
    return int(reach_str.replace('"', '').strip())

def parse_dob(dob_str):
    try:
        return datetime.strptime(dob_str.strip(), "%b %d, %Y").date().isoformat()
    except:
        return None

def parse_event_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y").date().isoformat()
    except:
        return None

def parse_landed_of_attempted(landed_of_attempted_str):
    if not landed_of_attempted_str or 'of' not in landed_of_attempted_str:
        return (0,0)
    try:
        landed, attempted = landed_of_attempted_str.split('of')
        return (int(landed.strip()), int(attempted.strip()))
    except ValueError:
        return (0,0)

def parse_names_from_bout(bout_str):
    fighter1, fighter2 = bout_str.split('vs.')
    return (fighter1.strip(), fighter2.strip())

def add_times(time1, time2):
    def to_seconds(t):
        if not t or ':' not in t:
            return 0
        minutes, seconds = map(int, t.strip().split(':'))
        return minutes * 60 + seconds

    def to_m_ss(total_seconds):
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02}"

    total_seconds = to_seconds(time1) + to_seconds(time2)
    return to_m_ss(total_seconds)

def get_or_create_fighter_by_name(cursor, name):
    cursor.execute('SELECT id FROM fighter WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute('INSERT INTO fighter (name) VALUES (?)', (name,))
        return cursor.lastrowid

def normalize_weight_class(raw_bout):
    cleaned = re.sub(r'\b(UFC|Title|Bout)\b', '', raw_bout, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def create_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS fight")
    cursor.execute("DROP TABLE IF EXISTS fighter_weight_class")
    cursor.execute("DROP TABLE IF EXISTS fighter")
    cursor.execute("DROP TABLE IF EXISTS weight_class")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fighter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    height TEXT,
    weight INTEGER,
    reach REAL,
    stance TEXT,
    dob TEXT,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    no_contests INTEGER DEFAULT 0,
    takedowns INTEGER DEFAULT 0,
    takedowns_attempted INTEGER DEFAULT 0,
    sig_strikes INTEGER DEFAULT 0,
    sig_strikes_attempted INTEGER DEFAULT 0,
    total_strikes INTEGER DEFAULT 0,
    total_strikes_attempted INTEGER DEFAULT 0,
    knockdowns INTEGER DEFAULT 0,
    knockouts INTEGER DEFAULT 0,
    submissions INTEGER DEFAULT 0,
    submissions_attempted INTEGER DEFAULT 0,
    control_time TEXT               --mm:ss
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_class (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        weight INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fighter_weight_class (
        fighter_id INTEGER NOT NULL,
        weight_class_id INTEGER NOT NULL,
        FOREIGN KEY (fighter_id) REFERENCES fighter(id),
        FOREIGN KEY (weight_class_id) REFERENCES weight_class(id),
        PRIMARY KEY (fighter_id, weight_class_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        location TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fight (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        fighter1_id INTEGER NOT NULL,
        fighter2_id INTEGER NOT NULL,
        outcome TEXT NOT NULL,               --W if single winner, D if draw, NC if no contest
        winner_id INTEGER,
        weight_class_id INTEGER,
        title_fight BOOLEAN,
        method TEXT,
        round INTEGER,
        time TEXT,                         --"m:ss"
        referee TEXT,
        details TEXT,
        FOREIGN KEY (event_id) REFERENCES event(id),
        FOREIGN KEY (fighter1_id) REFERENCES fighter(id),
        FOREIGN KEY (fighter2_id) REFERENCES fighter(id),
        FOREIGN KEY (winner_id) REFERENCES fighter(id),
        FOREIGN KEY (weight_class_id) REFERENCES weight_class(id)
        )
    ''')

def populate_weight_classes(cursor):
    weight_classes = [
        (1, "Strawweight (W)", 115),
        (2, "Flyweight (W)", 125),
        (3, "Flyweight", 125),
        (4, "Bantamweight (W)", 135),
        (5, "Bantamweight", 135),
        (6, "Featherweight (W)", 145),
        (7, "Featherweight", 145),
        (8, "Lightweight", 155),
        (9, "Welterweight", 170),
        (10, "Middleweight", 185),
        (11, "Light Heavyweight", 205),
        (12, "Heavyweight", 265),
        (13, "Open Weight", 500),
        (14, "Catch Weight", 500)
    ]

    for id, name, weight in weight_classes:
        cursor.execute('''
            INSERT OR IGNORE INTO weight_class (id, name, weight)
            VALUES (?, ?, ?)
        ''', (id, name, weight))

def import_fighters_from_csv(cursor, csv_file_path, db_path="ufc_info.db"):

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['FIGHTER'].strip()
            height = parse_height(row['HEIGHT'])
            weight = parse_weight(row['WEIGHT'])
            reach = parse_reach(row['REACH'])
            stance = row['STANCE'].strip() if row['STANCE'] and row['STANCE'] != '--' else None
            dob = parse_dob(row['DOB'])

            cursor.execute("SELECT id FROM fighter WHERE name = ?", (name,))
            if cursor.fetchone():
                continue
            
            cursor.execute('''
                INSERT INTO fighter (name, height, weight, reach, stance, dob)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, height, weight, reach, stance, dob))

def import_fight_stats_from_csv(cursor, csv_file_path, db_path="ufc_info.db"):

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['FIGHTER'].strip()
            knockdowns = int(float(row['KD'].strip() or 0))
            sig_strikes, sig_strikes_attempted = parse_landed_of_attempted(row['SIG.STR.'])
            total_strikes, total_strikes_attempted = parse_landed_of_attempted(row['TOTAL STR.'])
            takedowns, takedowns_attempted = parse_landed_of_attempted(row['TD'])
            control_time = row['CTRL'].strip() or "0:00"
            submissions_attempted = int(float(row['SUB.ATT'].strip() or 0))

            fighter_id = get_or_create_fighter_by_name(cursor, name)

            cursor.execute('''
                SELECT knockdowns, sig_strikes, sig_strikes_attempted, total_strikes, total_strikes_attempted, takedowns, takedowns_attempted, control_time, submissions_attempted
                FROM fighter WHERE id = ?
            ''', (fighter_id,))

            fighter = cursor.fetchone()

            if fighter:
                curr_kds, curr_sig_strikes, curr_sig_strikes_att, curr_total_strikes, curr_total_strikes_att, curr_tds, curr_tds_att, curr_control_time, curr_submissions_att = fighter

                cursor.execute('''
                    UPDATE fighter
                    SET
                        knockdowns = ?,
                        sig_strikes = ?,
                        sig_strikes_attempted = ?,
                        total_strikes = ?,
                        total_strikes_attempted = ?,
                        takedowns = ?,
                        takedowns_attempted = ?,
                        submissions_attempted = ?,
                        control_time = ?
                    WHERE id = ?
                ''', (
                    curr_kds + knockdowns,
                    curr_sig_strikes + sig_strikes,
                    curr_sig_strikes_att + sig_strikes_attempted,
                    curr_total_strikes + total_strikes,
                    curr_total_strikes_att + total_strikes_attempted,
                    curr_tds + takedowns,
                    curr_tds_att + takedowns_attempted,
                    curr_submissions_att + submissions_attempted,
                    add_times(curr_control_time, control_time),
                    fighter_id
                ))

def import_events_from_csv(cursor, csv_file_path, db_path="ufc_info.db"):

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['EVENT'].strip()
            date = parse_event_date(row['DATE'])
            location = row['LOCATION']

            cursor.execute("SELECT id FROM event WHERE name = ?", (name,))
            if cursor.fetchone():
                continue
            
            cursor.execute('''
                INSERT INTO event (name, date, location)
                VALUES (?, ?, ?)
            ''', (name, date, location))

def import_fight_results_from_csv(cursor, csv_file_path, db_path="ufc_info.db"):
    
    weight_class_map = {
        "Women's Strawweight": 1,
        "Women's Flyweight": 2,
        "Flyweight": 3,
        "Women's Bantamweight": 4,
        "Bantamweight": 5,
        "Women's Featherweight": 6,
        "Featherweight": 7,
        "Lightweight": 8,
        "Welterweight": 9,
        "Middleweight": 10,
        "Light Heavyweight": 11,
        "Heavyweight": 12,
        "Open Weight": 13,
        "Catch Weight": 14
    }
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            event_id = cursor.execute("SELECT id FROM event WHERE name = ?", (row['EVENT'].strip(),)).fetchone()[0]
            fighter1_id = get_or_create_fighter_by_name(cursor, parse_names_from_bout(row['BOUT'])[0])
            fighter2_id = get_or_create_fighter_by_name(cursor, parse_names_from_bout(row['BOUT'])[1])
            
            outcome = row['OUTCOME'].strip()
            winner_id = None
            if outcome == 'W/L':
                outcome = 'W'
                winner_id = fighter1_id
            elif outcome == 'L/W':
                outcome = 'W'
                winner_id = fighter2_id
            elif outcome == 'D/D':
                outcome = 'D'
            else:
                outcome = 'NC'
            
            weight_class_id = weight_class_map.get(normalize_weight_class(row['BOUT']))
            title_fight = True if 'Title' in row['BOUT'] else False
            method = row['METHOD'].strip()
            round_num = row['ROUND'].strip()
            time = row['TIME'].strip()
            referee = row['REFEREE'].strip()
            details = row['DETAILS'].strip()

            cursor.execute('''
                INSERT INTO fight (event_id, fighter1_id, fighter2_id, outcome, winner_id, weight_class_id, title_fight, method, round, time, referee, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, fighter1_id, fighter2_id, outcome, winner_id, weight_class_id, title_fight, method, round_num, time, referee, details))
            
            
            


def create_database():
    conn = sqlite3.connect("ufc_info.db")
    cursor = conn.cursor()
    
    create_tables(cursor)
    populate_weight_classes(cursor)
    import_events_from_csv(cursor, "ufc-data-scraper/ufc_event_details.csv")
    import_fighters_from_csv(cursor, "ufc-data-scraper/ufc_fighter_tott.csv")
    import_fight_stats_from_csv(cursor, "ufc-data-scraper/ufc_fight_stats.csv")
    import_fight_results_from_csv(cursor, "ufc-data-scraper/ufc_fight_results.csv")

    conn.commit()
    conn.close()



if __name__ == "__main__":
    create_database()
    main()