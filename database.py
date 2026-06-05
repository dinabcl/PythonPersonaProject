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
        ("Arben Krasniqi", "Toyota Prius", "01-124-AA", 1, 42.6629, 21.1655),
        ("Drita Berisha", "VW Golf", "01-552-BB", 1, 42.6515, 21.1533),
        ("Besnik Gashi", "Skoda Octavia", "01-883-CC", 1, 42.6236, 21.1484),
        ("Elira Hoxha", "Mercedes C200", "01-772-DD", 1, 42.6786, 21.2011),
        ("Valon Shala", "Audi A4", "01-339-EE", 0, 42.6487, 21.1740),
    ]

    rides = [
        ("Arta", "Prishtina Center", "Albi Mall", "Completed", 1, 12.50),
        ("Luan", "Mother Teresa Boulevard", "University of Prishtina", "Completed", 2, 8.00),
        ("Blerta", "Prishtina Airport", "Prishtina Center", "Accepted", 3, 18.90),
        ("Dren", "Rruga B", "Germia Park", "Waiting", None, 7.50),
        ("Valbona", "Prishtina Bus Station", "Fushe Kosove", "Completed", 4, 9.50),
        ("Ardit", "Prizren", "Prishtina Center", "Completed", 2, 28.00),
        ("Besa", "Peja", "Prishtina Airport", "Completed", 1, 35.00),
        ("Gent", "Gjilan", "Ferizaj", "Completed", 3, 14.00),
        ("Shqipe", "Mitrovica", "Prishtina Center", "Accepted", 4, 22.50),
        ("Fisnik", "Lipjan", "Prishtina Center", "Waiting", None, 10.00)
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