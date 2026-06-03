from fastapi import APIRouter
from database import get_db_connection
from models.driver import DriverCreate

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("/")
def get_drivers():
    conn = get_db_connection()
    drivers = conn.execute("SELECT * FROM drivers").fetchall()
    conn.close()
    return [dict(driver) for driver in drivers]


@router.get("/{driver_id}")
def get_driver(driver_id: int):
    conn = get_db_connection()
    driver = conn.execute(
        "SELECT * FROM drivers WHERE id = ?",
        (driver_id,)
    ).fetchone()
    conn.close()

    if driver:
        return dict(driver)

    return {"message": "Driver not found"}


@router.post("/")
def create_driver(driver: DriverCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO drivers 
        (name, car_model, license_plate, available, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        driver.name,
        driver.car_model,
        driver.license_plate,
        int(driver.available),
        driver.latitude,
        driver.longitude
    ))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"message": "Driver created", "id": new_id}


@router.delete("/{driver_id}")
def delete_driver(driver_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
    conn.commit()
    conn.close()

    return {"message": "Driver deleted"}