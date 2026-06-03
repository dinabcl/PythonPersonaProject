from pydantic import BaseModel
from typing import Optional

class RideBase(BaseModel):
    customer_name: str
    pickup_location: str
    destination: str
    status: str
    driver_id: Optional[int] = None
    fare: float

class RideCreate(RideBase):
    pass

class RideResponse(RideBase):
    id: int

class Ride(RideBase):
    id: int