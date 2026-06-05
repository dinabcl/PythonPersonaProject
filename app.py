import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import time
import re
from streamlit_autorefresh import st_autorefresh

API_URL = "http://127.0.0.1:8000"
SIMULATED_MINUTE_SECONDS = 2

st.set_page_config(page_title="Taksi Kosova", layout="wide")
st.title("🚕 Taksi Kosova")

if "active_rides" not in st.session_state:
    st.session_state.active_rides = []

should_refresh = False

for ride in st.session_state.active_rides:
    if ride["last_status"] not in ["Completed", "Cancelled"]:
        should_refresh = True
        break

if should_refresh:
    st_autorefresh(interval=3000, key="refresh")


location_data = {
    "Prishtina Center": {"lat": 42.6629, "lon": 21.1655},
    "Mother Teresa Boulevard": {"lat": 42.6611, "lon": 21.1622},
    "Prishtina Bus Station": {"lat": 42.6515, "lon": 21.1533},
    "University of Prishtina": {"lat": 42.6488, "lon": 21.1663},
    "Rruga B": {"lat": 42.6487, "lon": 21.1740},
    "Albi Mall": {"lat": 42.6236, "lon": 21.1484},
    "Germia Park": {"lat": 42.6786, "lon": 21.2011},
    "Prishtina Airport": {"lat": 42.5728, "lon": 21.0358},
    "Fushe Kosove": {"lat": 42.6394, "lon": 21.0961},
    "Lipjan": {"lat": 42.5217, "lon": 21.1258},
    "Ferizaj": {"lat": 42.3706, "lon": 21.1553},
    "Mitrovica": {"lat": 42.8914, "lon": 20.8656},
    "Peja": {"lat": 42.6591, "lon": 20.2883},
    "Prizren": {"lat": 42.2139, "lon": 20.7397},
    "Gjakova": {"lat": 42.3803, "lon": 20.4308},
    "Gjilan": {"lat": 42.4635, "lon": 21.4699}
}


def get_drivers():
    response = requests.get(f"{API_URL}/drivers/")
    return response.json() if response.status_code == 200 else []


def get_rides():
    response = requests.get(f"{API_URL}/rides/")
    return response.json() if response.status_code == 200 else []


def update_driver_availability(driver_id, available):
    requests.put(
        f"{API_URL}/drivers/{driver_id}/availability",
        params={"available": available}
    )


def update_ride_status(ride_id, status):
    requests.put(
        f"{API_URL}/rides/{ride_id}/status",
        params={"status": status}
    )


def is_valid_name(name):
    name = name.strip()
    return len(name) >= 3 and all(char.isalpha() or char.isspace() for char in name)


def is_valid_car_model(car_model):
    car_model = car_model.strip()
    return len(car_model) >= 3 and any(char.isalpha() for char in car_model)


def is_valid_plate(plate):
    plate = plate.strip().upper()
    pattern = r"^\d{2}-\d{3}-[A-Z]{2}$"
    return re.match(pattern, plate) is not None


def status_badge(status):
    if status == "Accepted":
        return "🟢 Driver Coming"
    elif status == "Transporting":
        return "🟣 Transporting Customer"
    elif status == "Completed":
        return "🔵 Completed"
    elif status == "Cancelled":
        return "🔴 Cancelled"
    return f"⚪ {status}"


def calculate_distance(start, end):
    p1 = location_data[start]
    p2 = location_data[end]

    lat_diff = p1["lat"] - p2["lat"]
    lon_diff = p1["lon"] - p2["lon"]

    return round(((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111, 2)


def calculate_driver_to_pickup_distance(driver, pickup_location):
    pickup = location_data[pickup_location]

    lat_diff = driver["latitude"] - pickup["lat"]
    lon_diff = driver["longitude"] - pickup["lon"]

    return round(((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111, 2)


def generate_eta(distance):
    return max(4, int(distance * 3))


def generate_pickup_eta(distance):
    return max(3, int(distance * 6))


def generate_fare(distance):
    base_fare = 1.50
    price_per_km = 0.60
    return round(base_fare + distance * price_per_km, 2)


def interpolate(start_lat, start_lon, end_lat, end_lon, progress):
    progress = min(max(progress, 0), 1)
    current_lat = start_lat + (end_lat - start_lat) * progress
    current_lon = start_lon + (end_lon - start_lon) * progress
    return current_lat, current_lon


def get_moving_driver(ride):
    driver = ride["driver"]
    elapsed = time.time() - ride["created_at"]

    pickup = location_data[ride["pickup_location"]]
    destination = location_data[ride["destination"]]

    pickup_seconds = ride["pickup_eta"] * SIMULATED_MINUTE_SECONDS
    trip_seconds = ride["trip_eta"] * SIMULATED_MINUTE_SECONDS

    if elapsed < pickup_seconds:
        progress = elapsed / pickup_seconds

        current_lat, current_lon = interpolate(
            driver["latitude"],
            driver["longitude"],
            pickup["lat"],
            pickup["lon"],
            progress
        )

        phase = "Accepted"
        remaining = int((pickup_seconds - elapsed) / SIMULATED_MINUTE_SECONDS) + 1

    elif elapsed < pickup_seconds + trip_seconds:
        progress = (elapsed - pickup_seconds) / trip_seconds

        current_lat, current_lon = interpolate(
            pickup["lat"],
            pickup["lon"],
            destination["lat"],
            destination["lon"],
            progress
        )

        phase = "Transporting"
        remaining = int(
            (pickup_seconds + trip_seconds - elapsed) / SIMULATED_MINUTE_SECONDS
        ) + 1

    else:
        current_lat = destination["lat"]
        current_lon = destination["lon"]
        phase = "Completed"
        remaining = 0

    moving_driver = driver.copy()
    moving_driver["latitude"] = current_lat
    moving_driver["longitude"] = current_lon
    moving_driver["available"] = 0 if phase != "Completed" else 1

    return moving_driver, phase, remaining


def show_driver_map(drivers):
    if not drivers:
        st.warning("No drivers found.")
        return

    df = pd.DataFrame(drivers)

    map_df = df.rename(columns={
        "latitude": "lat",
        "longitude": "lon"
    })

    map_df["color"] = map_df["available"].apply(
        lambda x: [0, 200, 0, 180] if x == 1 else [255, 0, 0, 180]
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius=120,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=map_df["lat"].mean(),
        longitude=map_df["lon"].mean(),
        zoom=12,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=view_state,
            layers=[layer],
            tooltip={
                "text": "{name}\n{car_model}\nPlate: {license_plate}"
            }
        )
    )


drivers = get_drivers()
rides = get_rides()

admin_tab, customer_tab = st.tabs([
    "📊 Admin Dashboard",
    "🚕 Customer App"
])


with admin_tab:
    st.header("Admin Dashboard")

    total_revenue = round(
        sum(ride["fare"] for ride in rides if ride["status"] != "Cancelled"),
        2
    )

    available_count = len([driver for driver in drivers if driver["available"] == 1])
    busy_count = len([driver for driver in drivers if driver["available"] == 0])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Drivers", len(drivers))
    col2.metric("Available", available_count)
    col3.metric("Busy", busy_count)
    col4.metric("Revenue €", total_revenue)

    st.subheader("Add Driver")

    with st.form("add_driver_form"):
        name = st.text_input("Driver Name")
        car_model = st.text_input("Car Model")
        license_plate = st.text_input("License Plate", placeholder="01-123-AA")

        driver_location = st.selectbox(
            "Driver Starting Location",
            list(location_data.keys())
        )

        add_driver = st.form_submit_button("Add Driver")

        if add_driver:
            name = name.strip()
            car_model = car_model.strip()
            license_plate = license_plate.strip().upper()

            if not is_valid_name(name):
                st.error("Driver name must be at least 3 letters and contain only letters/spaces.")

            elif not is_valid_car_model(car_model):
                st.error("Car model must be at least 3 characters and contain letters.")

            elif not is_valid_plate(license_plate):
                st.error("License plate must be in this format: 01-123-AA")

            else:
                payload = {
                    "name": name,
                    "car_model": car_model,
                    "license_plate": license_plate,
                    "available": True,
                    "latitude": location_data[driver_location]["lat"],
                    "longitude": location_data[driver_location]["lon"]
                }

                response = requests.post(f"{API_URL}/drivers/", json=payload)

                if response.status_code == 200:
                    st.success("Driver added!")
                    st.rerun()
                else:
                    st.error("Could not add driver.")

    st.subheader("Drivers")

    if drivers:
        driver_df = pd.DataFrame(drivers)
        driver_df["status"] = driver_df["available"].apply(
            lambda x: "🟢 Available" if x == 1 else "🔴 Busy"
        )
        st.dataframe(driver_df, use_container_width=True)
    else:
        st.warning("No drivers found.")

    st.subheader("Rides")

    if rides:
        ride_df = pd.DataFrame(rides)
        ride_df["status_display"] = ride_df["status"].apply(status_badge)
        st.dataframe(ride_df, use_container_width=True)
    else:
        st.warning("No rides found.")

    st.subheader("Live Driver Map")

    admin_map_drivers = []
    moving_driver_ids = []

    for active_ride in st.session_state.active_rides:
        moving_driver, current_phase, remaining_eta = get_moving_driver(active_ride)

        if current_phase != active_ride["last_status"]:
            active_ride["status"] = current_phase
            active_ride["last_status"] = current_phase
            update_ride_status(active_ride["ride_id"], current_phase)

            if current_phase == "Completed":
                update_driver_availability(active_ride["driver"]["id"], True)

        if current_phase != "Completed":
            admin_map_drivers.append(moving_driver)
            moving_driver_ids.append(active_ride["driver"]["id"])

    for driver in drivers:
        if driver["id"] not in moving_driver_ids:
            admin_map_drivers.append(driver)

    show_driver_map(admin_map_drivers)


with customer_tab:
    st.header("Customer App")

    locations = list(location_data.keys())

    with st.form("ride_form"):
        customer_name = st.text_input("Customer Name")

        pickup_location = st.selectbox("Pickup Location", locations)
        destination = st.selectbox("Destination", locations)

        driver_options = []

        for driver in drivers:
            status = "🟢 Available" if driver["available"] == 1 else "🔴 Busy"
            driver_options.append(
                f"{driver['id']} - {driver['name']} {status}"
            )

        selected_driver = st.selectbox("Choose Driver", driver_options)

        submitted = st.form_submit_button("Request Taxi")

        if submitted:
            customer_name = customer_name.strip()

            if not is_valid_name(customer_name):
                st.error("Customer name must be at least 3 letters and contain only letters/spaces.")

            elif pickup_location == destination:
                st.error("Pickup and destination cannot be the same.")

            elif not selected_driver:
                st.error("No drivers found.")

            else:
                selected_driver_id = int(selected_driver.split(" - ")[0])

                assigned_driver = None

                for driver in drivers:
                    if driver["id"] == selected_driver_id:
                        assigned_driver = driver
                        break

                if assigned_driver["available"] != 1:
                    st.error(
                        f"{assigned_driver['name']} is currently busy. Please choose another driver."
                    )
                    st.stop()

                trip_distance = calculate_distance(pickup_location, destination)
                pickup_distance = calculate_driver_to_pickup_distance(
                    assigned_driver,
                    pickup_location
                )

                pickup_eta = generate_pickup_eta(pickup_distance)
                trip_eta = generate_eta(trip_distance)
                fare = generate_fare(trip_distance)

                payload = {
                    "customer_name": customer_name,
                    "pickup_location": pickup_location,
                    "destination": destination,
                    "status": "Accepted",
                    "driver_id": assigned_driver["id"],
                    "fare": fare
                }

                response = requests.post(f"{API_URL}/rides/", json=payload)

                if response.status_code == 200:
                    new_ride = response.json()

                    update_driver_availability(assigned_driver["id"], False)

                    st.session_state.active_rides.append({
                        "ride_id": new_ride["id"],
                        "driver": assigned_driver,
                        "pickup_location": pickup_location,
                        "destination": destination,
                        "status": "Accepted",
                        "pickup_eta": pickup_eta,
                        "trip_eta": trip_eta,
                        "fare": fare,
                        "distance": trip_distance,
                        "pickup_distance": pickup_distance,
                        "created_at": time.time(),
                        "last_status": "Accepted"
                    })

                    st.success(
                        f"Taxi requested! {assigned_driver['name']} is on the way."
                    )
                    st.rerun()
                else:
                    st.error("Could not create ride.")

    st.subheader("Active Rides")

    if st.session_state.active_rides:
        for index, ride in enumerate(st.session_state.active_rides):
            driver = ride["driver"]
            moving_driver, current_phase, remaining_eta = get_moving_driver(ride)

            if current_phase != ride["last_status"]:
                ride["status"] = current_phase
                ride["last_status"] = current_phase
                update_ride_status(ride["ride_id"], current_phase)

                if current_phase == "Completed":
                    update_driver_availability(driver["id"], True)

                st.session_state.active_rides[index] = ride
                st.rerun()

            with st.expander(
                f"Ride #{ride['ride_id']} — {driver['name']} — {status_badge(current_phase)}",
                expanded=True
            ):
                st.write(f"**Status:** {status_badge(current_phase)}")
                st.write(f"**Driver:** {driver['name']}")
                st.write(f"**Car:** {driver['car_model']}")
                st.write(f"**Plate:** {driver['license_plate']}")
                st.write(f"**Pickup:** {ride['pickup_location']}")
                st.write(f"**Destination:** {ride['destination']}")
                st.write(f"**Pickup Distance:** {ride['pickup_distance']} km")
                st.write(f"**Trip Distance:** {ride['distance']} km")
                st.write(f"**Fare:** {ride['fare']} €")

                if current_phase == "Accepted":
                    st.write(f"**Driver arrives in:** {remaining_eta} minutes")

                elif current_phase == "Transporting":
                    st.write(f"**Trip finishes in:** {remaining_eta} minutes")

                elif current_phase == "Completed":
                    st.success("🔵 Ride completed. You arrived at your destination.")
                    st.write("**ETA:** 0 minutes")

                if current_phase != "Completed":
                    if st.button("Cancel Ride", key=f"cancel_{ride['ride_id']}"):
                        update_ride_status(ride["ride_id"], "Cancelled")
                        update_driver_availability(driver["id"], True)
                        st.session_state.active_rides.pop(index)
                        st.success("Ride cancelled.")
                        st.rerun()

                st.subheader("Live Driver Location")
                show_driver_map([moving_driver])

    else:
        st.warning("No active rides yet.")