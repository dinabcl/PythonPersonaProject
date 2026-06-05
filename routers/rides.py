from fastapi import APIRouter
from database import get_db_connection
from models.ride import RideCreate

router = APIRouter(prefix="/rides", tags=["Rides"])


@router.get("/")
def get_rides():

    conn = get_db_connection()

    rides = conn.execute(
        "SELECT * FROM rides"
    ).fetchall()

    conn.close()

    return [dict(ride) for ride in rides]


@router.get("/{ride_id}")
def get_ride(ride_id: int):

    conn = get_db_connection()

    ride = conn.execute(
        "SELECT * FROM rides WHERE id = ?",
        (ride_id,)
    ).fetchone()

    conn.close()

    if ride:
        return dict(ride)

    return {"message": "Ride not found"}


@router.post("/")
def create_ride(ride: RideCreate):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO rides
        (
            customer_name,
            pickup_location,
            destination,
            status,
            driver_id,
            fare
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ride.customer_name,
            ride.pickup_location,
            ride.destination,
            ride.status,
            ride.driver_id,
            ride.fare
        )
    )

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    return {"message": "Ride created", "id": new_id}


@router.delete("/{ride_id}")
def delete_ride(ride_id: int):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM rides WHERE id = ?",
        (ride_id,)
    )

    conn.commit()
    conn.close()

    return {"message": "Ride deleted"}

@router.put("/{ride_id}/status")
def update_ride_status(ride_id: int, status: str):
    conn = get_db_connection()

    conn.execute(
        "UPDATE rides SET status = ? WHERE id = ?",
        (status, ride_id)
    )

    conn.commit()
    conn.close()

    return {"message": "Ride status updated"}