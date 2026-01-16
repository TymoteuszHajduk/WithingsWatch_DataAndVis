import sqlite3
def db_init():
    conn = sqlite3.connect('withings_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE heart_rate (
                timestamp INTEGER PRIMARY KEY,
                value INTEGER);''')
    c.execute('''CREATE TABLE steps (
                timestamp INTEGER PRIMARY KEY,
                value INTEGER);''')
    c.execute('''CREATE TABLE sleep_summaries(
                date INTEGER,
                start INTEGER,
                end INTEGER PRIMARY KEY,
                total_sleep_time INTEGER,
                lightsleepduration INTEGER,
                remsleepduration INTEGER,
                deepsleepduration INTEGER,
                sleep_score INTEGER,
                waso INTEGER);''')
    conn.commit()
    conn.close()

