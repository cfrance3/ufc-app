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
        return datetime.strptime(dob_str, "%b %d, %Y").date().isoformat()
    except:
        return None

def create_database():
    conn = sqlite3.connect("ufc_info.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS fight")
    cursor.execute("DROP TABLE IF EXISTS fighter_weight_class")
    cursor.execute("DROP TABLE IF EXISTS fighter")
    cursor.execute("DROP TABLE IF EXISTS weight_class")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fighter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dob TEXT,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    takedowns INTEGER DEFAULT 0,
    takedown_attempts INTEGER DEFAULT 0,
    sig_strikes INTEGER DEFAULT 0,
    total_strikes INTEGER DEFAULT 0,
    knockouts INTEGER DEFAULT 0,
    submissions INTEGER DEFAULT 0,
    height TEXT,
    reach REAL,
    weight INTEGER,
    stance TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_class (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    CREATE TABLE IF NOT EXISTS fight (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fighter1_id INTEGER NOT NULL,
        fighter2_id INTEGER NOT NULL,
        winner_id INTEGER,
        date TEXT,                          --"YYYY-MM-DD"
        weight_class_id INTEGER,
        title_fight BOOLEAN,
        method TEXT,
        round INTEGER,
        time TEXT,                          --"m:ss"
        FOREIGN KEY (fighter1_id) REFERENCES fighter(id),
        FOREIGN KEY (fighter2_id) REFERENCES fighter(id),
        FOREIGN KEY (winner_id) REFERENCES fighter(id),
        FOREIGN KEY (weight_class_id) REFERENCES weight_class(id)
        )
    ''')

    populate_weight_classes(cursor)
    import_fighters_from_csv(cursor, "../ufc-data-scraper/ufc_fighter_tott.csv")

    conn.commit()
    conn.close()

def populate_weight_classes(cursor):
    weight_classes = [
        ("Strawweight (W)", 115),
        ("Flyweight (W)", 125),
        ("Flyweight", 125),
        ("Bantamweight (W)", 135),
        ("Bantamweight", 135),
        ("Featherweight (W)", 145),
        ("Featherweight", 145),
        ("Lightweight", 155),
        ("Welterweight", 170),
        ("Middleweight", 185),
        ("Light Heavyweight", 205),
        ("Heavyweight", 265),
    ]

    for name, weight in weight_classes:
        cursor.execute('''
            INSERT OR IGNORE INTO weight_class (name, weight)
            VALUES (?, ?)
        ''', (name, weight))

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

if __name__ == "__main__":
    create_database()
    main()