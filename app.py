import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
import datetime

'''
# TaxiFareModel
'''

st.markdown('''
## Welcome to the Taxi Fare Prediction app!

Please fill in the following details to get the estimated fare for your ride.
''')

geolocator = Nominatim(user_agent="taxifare_app")

# Function to get address suggestions from Nominatim
def get_address_suggestions(query):
    if query:
        url = f'https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=5'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return [place['display_name'] for place in data]
    return []

# Collecting input from the user
pickup_date = st.date_input("Pickup Date", value=datetime.date.today())
pickup_time = st.time_input("Pickup Time", value=datetime.datetime.now().time())

# Autofill addresses
pickup_address_query = st.text_input("Enter Pickup Address")
pickup_suggestions = get_address_suggestions(pickup_address_query)
pickup_address = st.selectbox("Pickup Address Suggestions", pickup_suggestions)

dropoff_address_query = st.text_input("Enter Dropoff Address")
dropoff_suggestions = get_address_suggestions(dropoff_address_query)
dropoff_address = st.selectbox("Dropoff Address Suggestions", dropoff_suggestions)

# Convert addresses to coordinates using geopy
def geocode(address):
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        st.warning(f"Could not geocode address: {address}")
        return None, None

pickup_coords = geocode(pickup_address) if pickup_address else (None, None)
dropoff_coords = geocode(dropoff_address) if dropoff_address else (None, None)

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
# Add markers if coordinates are available
if pickup_coords != (None, None):
    folium.Marker(pickup_coords, tooltip="Pickup Location", icon=folium.Icon(color="green")).add_to(m)
if dropoff_coords != (None, None):
    folium.Marker(dropoff_coords, tooltip="Dropoff Location", icon=folium.Icon(color="red")).add_to(m)


# Embed the Folium map in Streamlit
st_folium(m, width=700, height=500)
# Collecting input for passenger count
passenger_count = st.number_input("Passenger Count", min_value=1, max_value=6, step=1)

# Collect pickup and dropoff coordinates or ask for manual input
if pickup_coords == (None, None):
    st.warning("No pickup coordinates available from address. Please enter manually.")
    pickup_longitude = st.number_input("Pickup Longitude", format="%.6f")
    pickup_latitude = st.number_input("Pickup Latitude", format="%.6f")
else:
    pickup_latitude, pickup_longitude = pickup_coords

if dropoff_coords == (None, None):
    st.warning("No dropoff coordinates available from address. Please enter manually.")
    dropoff_longitude = st.number_input("Dropoff Longitude", format="%.6f")
    dropoff_latitude = st.number_input("Dropoff Latitude", format="%.6f")
else:
    dropoff_latitude, dropoff_longitude = dropoff_coords

# Combine date and time into a single datetime object
pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time)

# Prepare parameters for the API call
params = {
    "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}

url = 'https://taxifare.lewagon.ai/predict'

# Button to get the fare prediction
if st.button("Get Fare Prediction"):
    # API call
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the prediction
        prediction = response.json().get("fare", "N/A")

        # Display the prediction
        st.success(f"Estimated Fare: ${prediction:.2f}")
    else:
        # Handle API error
        st.error(f"Failed to get the prediction. Status code: {response.status_code}")
