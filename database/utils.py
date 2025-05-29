import re

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

def normalize_weight_class(raw_weightclass):
    
    weightclasses = [
        "women's strawweight", "women's flyweight", "women's bantamweight", "women's featherweight",
        "flyweight", "bantamweight", "featherweight", "lightweight", "welterweight", "middleweight",
        "light heavyweight", "heavyweight", "open weight", "catch weight"
    ]

    def format_class(name):
        if name.startswith("women's "):
            return "Women's " + name[len("women's "):].capitalize()
        return name.title()

    cleaned = re.sub(r'\b(UFC|Title|Bout|Interim)\b', '', raw_weightclass, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()

    if "tournament" in cleaned or "superfight" in cleaned:
        return "Open Weight"
    
    for wc in weightclasses:
        if wc in cleaned:
            return format_class(wc)
    return None

def insert_fighters_weightclass(cursor, bout_info):
    wc_id = bout_info[0]
    fighter1_id = bout_info[1]
    fighter2_id = bout_info[2]

    cursor.execute('SELECT * FROM fighter_weight_class WHERE fighter_id = ? AND weight_class_id = ?', (fighter1_id, wc_id))
    fighter1_wc = cursor.fetchone()
    if not fighter1_wc:
        cursor.execute('INSERT INTO fighter_weight_class (fighter_id, weight_class_id) VALUES (?, ?)', (fighter1_id, wc_id))
    
    cursor.execute('SELECT * FROM fighter_weight_class WHERE fighter_id = ? AND weight_class_id = ?', (fighter2_id, wc_id))
    fighter2_wc = cursor.fetchone()
    if not fighter2_wc:
        cursor.execute('INSERT INTO fighter_weight_class (fighter_id, weight_class_id) VALUES (?, ?)', (fighter2_id, wc_id))
