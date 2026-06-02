from pydantic import BaseModel

class DriverBase(BaseModel):
    name: str

class DriverCreate(DriverBase):
    pass

class DriverResponse(BaseModel):
    id: int
    name: str

class Driver(DriverBase):
    id: int