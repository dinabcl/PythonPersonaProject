from fastapi import FastAPI
from routers import drivers, rides
from database import create_database

app = FastAPI(title="Taxi Dispatch API")

create_database()

app.include_router(drivers.router)
app.include_router(rides.router)


@app.get("/")
def home():
    return {"message": "Taxi Dispatch API is running"}