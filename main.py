from fastapi import FastAPI
from routers import drivers, rides, locations, auth
from database import create_database

app = FastAPI(title="Infinity Taxi API")

create_database()

app.include_router(drivers.router)
app.include_router(rides.router)
app.include_router(locations.router)
app.include_router(auth.router)


@app.get("/")
def home():
    return {"message": "Infinity Taxi API is running"}