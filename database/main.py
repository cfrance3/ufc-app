import sqlite3
from database.schema import *
from database.importers import *

def create_database(callback):
    conn = sqlite3.connect("ufc_info.db")
    cursor = conn.cursor()
    
    create_tables(cursor)
    populate_weight_classes(cursor)

    import_events_from_csv(cursor, "ufc-data-scraper/ufc_event_details.csv")
    import_fighters_from_csv(cursor, "ufc-data-scraper/ufc_fighter_tott.csv")
    import_fight_results_from_csv(cursor, "ufc-data-scraper/ufc_fight_results.csv")
    conn.commit()
    import_fight_stats_from_csv(cursor, "ufc-data-scraper/ufc_fight_stats.csv")

    conn.commit()
    conn.close()
    callback()