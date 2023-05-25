# database.py
import sqlite3

def create_database(dbname):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    # Check if table users already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone() is None:
        # If it doesn't exist, create it
        cursor.execute('''
            CREATE TABLE users
            (username TEXT PRIMARY KEY,
             password TEXT);
        ''')
        conn.commit()
    conn.close()
