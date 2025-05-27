import re
from datetime import datetime

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