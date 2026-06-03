import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.title("🚕 Taxi Dispatch Dashboard")

tab1, tab2 = st.tabs(["Drivers", "Rides"])

with tab1:

    st.header("Drivers")

    response = requests.get(f"{API_URL}/drivers/")

    if response.status_code == 200:

        drivers = response.json()

        df = pd.DataFrame(drivers)

        st.dataframe(df)

with tab2:

    st.header("Rides")

    response = requests.get(f"{API_URL}/rides/")

    if response.status_code == 200:

        rides = response.json()

        df = pd.DataFrame(rides)

        st.dataframe(df)

st.header("Request Ride")

with st.form("ride_form"):

    customer_name = st.text_input("Customer Name")
    pickup_location = st.text_input("Pickup Location")
    destination = st.text_input("Destination")

    submitted = st.form_submit_button("Request Taxi")

    if submitted:

        payload = {
            "customer_name": customer_name,
            "pickup_location": pickup_location,
            "destination": destination,
            "status": "Waiting",
            "driver_id": None,
            "fare": 25.0
        }

        response = requests.post(
            f"{API_URL}/rides/",
            json=payload
        )

        st.success("Ride created!")

tab1, tab2, tab3 = st.tabs(["Drivers", "Rides", "Map"])

with tab3:

    st.header("Driver Locations")

    drivers = requests.get(
        f"{API_URL}/drivers/"
    ).json()

    import pandas as pd

    df = pd.DataFrame({
        "lat": [47.3769, 47.3771, 47.3775, 47.3765, 47.3780],
        "lon": [8.5417, 8.5420, 8.5410, 8.5430, 8.5405]
    })

    st.map(df)

with tab3:
    st.header("Driver Locations")

    response = requests.get(f"{API_URL}/drivers/")

    if response.status_code == 200:
        drivers = response.json()
        df = pd.DataFrame(drivers)

        map_df = df.rename(columns={
            "latitude": "lat",
            "longitude": "lon"
        })

        st.map(map_df[["lat", "lon"]])