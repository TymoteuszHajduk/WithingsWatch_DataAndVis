import sqlite3
from config import read_queries_config
import pandas as pd
class FileDialog:
    def __init__(self):
        self.connection = sqlite3.connect('withings_database.db')
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
    def write_to_db(self, table, data):
        try:
            self.cursor.executemany(f"INSERT OR IGNORE INTO {table} (timestamp, value) VALUES (?, ?)", data)
            self.connection.commit()
        except sqlite3.OperationalError as error:
            print(f"error writing to db, error: {error}")

    def write_sleep_summary_to_db(self, data):
        query = """INSERT OR IGNORE INTO sleep_summaries(date, start, end, total_sleep_time, lightsleepduration, remsleepduration, deepsleepduration, sleep_score, waso) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(query, data)
        self.connection.commit()
    def read_from_db(self,meas_type, start, end):
        """START AND END ARE UNIX TIMESTAMPS"""
        params = {

            'start': start,
            'end': end,
        }
        df = pd.read_sql_query(read_queries_config[meas_type], self.connection, params=params)
        return df

