import sqlite3

def get_db_connection():
    conn = sqlite3.connect("taxi.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    conn = sqlite3.connect("taxi.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS taxi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        taxi TEXT,
        driver_id INTEGER,
        ride_id INTEGER,
        costumer_id INTEGER,
        pickup_location TEXT,
        destination TEXT,
        status TEXT,
        FOREIGN KEY(driver_id) REFERENCES drivers(id)
    )''')