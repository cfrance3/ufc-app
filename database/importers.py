from database.parsers import *
from database.utils import *
import csv

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

            if name == '':
                print(f"Empty name found: {row}")

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

            if name == '':
                continue
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
                loser_id = fighter2_id
            elif outcome == 'L/W':
                outcome = 'W'
                winner_id = fighter2_id
                loser_id = fighter1_id
            elif outcome == 'D/D':
                outcome = 'D'
            else:
                outcome = 'NC'

            raw_wc = row['WEIGHTCLASS']
            clean_wc = normalize_weight_class(raw_wc)
            weight_class_id = weight_class_map.get(clean_wc)
            if weight_class_id is None:
                print(f"Unmatched weight class: {raw_wc}")

            title_fight = True if 'Title' in row['WEIGHTCLASS'] else False
            method = row['METHOD'].strip()
            round_num = row['ROUND'].strip()
            time = row['TIME'].strip()
            referee = row['REFEREE'].strip()
            details = row['DETAILS'].strip()

            cursor.execute('''
                INSERT INTO fight (event_id, fighter1_id, fighter2_id, outcome, winner_id, weight_class_id, title_fight, method, round, time, referee, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, fighter1_id, fighter2_id, outcome, winner_id, weight_class_id, title_fight, method, round_num, time, referee, details))

            submissions = 0
            knockouts = 0
            if 'submission' in method.lower():
                submissions = 1
            elif 'ko' in method.lower():
                knockouts = 1

            if outcome == 'W':
                cursor.execute('SELECT wins, knockouts, submissions FROM fighter WHERE id = ?', (winner_id,))
                winner = cursor.fetchone()
                if winner:
                    curr_wins, curr_knockouts, curr_submissions = winner
                    cursor.execute('''
                        UPDATE fighter
                            SET
                            wins = ?,
                            knockouts = ?,
                            submissions = ?
                        WHERE id = ?
                    ''', 
                        (curr_wins + 1,
                        curr_knockouts + knockouts,
                        curr_submissions + submissions,
                        winner_id))
                    
                cursor.execute('SELECT losses FROM fighter WHERE id = ?', (loser_id,))
                loser = cursor.fetchone()
                if loser:
                    curr_losses = loser[0]
                    cursor.execute('UPDATE fighter SET losses = ? WHERE id = ?', (curr_losses + 1, loser_id))
            elif outcome == 'D':
                cursor.execute('SELECT draws FROM fighter WHERE id = ? OR id = ?', (fighter1_id, fighter2_id))
                fighter1 = cursor.fetchone()
                fighter2 = cursor.fetchone()

                if fighter1:
                    cursor.execute('UPDATE fighter SET draws = ? WHERE id = ?', (fighter1[0] + 1, fighter1_id))
                if fighter2:
                    cursor.execute('UPDATE fighter SET draws = ? WHERE id = ?', (fighter2[0] + 1, fighter2_id))
            else:
                cursor.execute('SELECT no_contests FROM fighter WHERE id = ? OR id = ?', (fighter1_id, fighter2_id))
                fighter1 = cursor.fetchone()
                fighter2 = cursor.fetchone()

                if fighter1:
                    cursor.execute('UPDATE fighter SET no_contests = ? WHERE id = ?', (fighter1[0] + 1, fighter1_id))
                if fighter2:
                    cursor.execute('UPDATE fighter SET no_contests = ? WHERE id = ?', (fighter2[0] + 1, fighter2_id))