from pydantic import BaseModel
from typing import Optional, List

class RideBase(BaseModel):
    id: int
    customer_id: int
    pickup_location: str
    destination: str
    status: str
    driver_id: int

class RideCreate(RideBase):
    pass

class RideResponse(RideBase):
    id: int

class Ride(RideBase):
    id: int