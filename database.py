import sqlite3


def get_db_connection():
    conn = sqlite3.connect("taxi.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = sqlite3.connect("taxi.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            car_model TEXT NOT NULL,
            license_plate TEXT NOT NULL,
            available INTEGER NOT NULL,
            latitude REAL,
            longitude REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            pickup_location TEXT NOT NULL,
            destination TEXT NOT NULL,
            status TEXT NOT NULL,
            driver_id INTEGER,
            fare REAL,
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
    """)

    cursor.execute("DELETE FROM rides")
    cursor.execute("DELETE FROM drivers")

    drivers = [
        ("John Smith", "Toyota Prius", "ZH-124 882", 1, 47.3769, 8.5417),
        ("Sarah Jones", "VW Golf", "ZH-552 914", 1, 47.3771, 8.5420),
        ("Mike Brown", "Skoda Octavia", "ZH-883 120", 1, 47.3775, 8.5410),
        ("Emma Taylor", "Mercedes C200", "ZH-772 441", 1, 47.3765, 8.5430),
        ("David Wilson", "Audi A4", "ZH-339 665", 0, 47.3780, 8.5405),
    ]

    rides = [
        ("Alice", "Zurich HB", "Zurich Airport", "Completed", 1, 42.50),
        ("Ben", "Bahnhofstrasse", "ETH Zurich", "Completed", 2, 18.00),
        ("Mia", "Zurich Airport", "City Center", "Accepted", 3, 39.90),
        ("Noah", "Oerlikon", "Altstetten", "Waiting", None, 25.00),
        ("Lina", "University", "Main Station", "Completed", 4, 16.50),
    ]

    cursor.executemany("""
        INSERT INTO drivers 
        (name, car_model, license_plate, available, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
    """, drivers)

    cursor.executemany("""
        INSERT INTO rides 
        (customer_name, pickup_location, destination, status, driver_id, fare)
        VALUES (?, ?, ?, ?, ?, ?)
    """, rides)

    conn.commit()
    conn.close()

    print("taxi.db created successfully!")


if __name__ == "__main__":
    create_database()