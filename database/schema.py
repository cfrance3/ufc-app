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
    control_time TEXT DEFAULT '0:00'               --mm:ss
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
        fighter1_kd INTEGER DEFAULT 0,
        fighter2_kd INTEGER DEFAULT 0,
        fighter1_sig_strikes INTEGER DEFAULT 0,
        fighter2_sig_strikes INTEGER DEFAULT 0,
        fighter1_sig_strikes_att INTEGER DEFAULT 0,
        fighter2_sig_strikes_att INTEGER DEFAULT 0,
        fighter1_total_strikes INTEGER DEFAULT 0,
        fighter2_total_strikes INTEGER DEFAULT 0,
        fighter1_total_strikes_att INTEGER DEFAULT 0,
        fighter2_total_strikes_att INTEGER DEFAULT 0,   
        fighter1_takedowns INTEGER DEFAULT 0,
        fighter2_takedowns INTEGER DEFAULT 0,
        fighter1_takedowns_att INTEGER DEFAULT 0,
        fighter2_takedowns_att INTEGER DEFAULT 0,
        fighter1_submissions_att INTEGER DEFAULT 0,
        fighter2_submissions_att INTEGER DEFAULT 0,
        fighter1_control_time TEXT DEFAULT '0:00',
        fighter2_control_time TEXT DEFAULT '0:00',
        outcome TEXT NOT NULL,               --W if single winner, D if draw, NC if no contest
        winner_id INTEGER,
        weight_class_id INTEGER NOT NULL,
        title_fight BOOLEAN NOT NULL,
        method TEXT NOT NULL,
        round INTEGER NOT NULL,
        time TEXT NOT NULL,                         --"m:ss"
        referee TEXT NOT NULL,
        details TEXT NOT NULL,
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