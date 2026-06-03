from pydantic import BaseModel


class DriverBase(BaseModel):
    name: str
    car_model: str
    license_plate: str
    available: bool
    latitude: float
    longitude: float


class DriverCreate(DriverBase):
    pass


class DriverResponse(DriverBase):
    id: int


class Driver(DriverBase):
    id: int