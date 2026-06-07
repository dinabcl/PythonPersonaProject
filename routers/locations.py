from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("/")
def get_locations():
    conn = get_db_connection()

    locations = conn.execute(
        "SELECT * FROM locations"
    ).fetchall()

    conn.close()

    return [dict(location) for location in locations]