import streamlit as st
import folium
from streamlit_folium import folium_static
import datetime
import requests
from geopy.geocoders import Nominatim


def get_coordinates(address):
    geolocator = Nominatim(user_agent="app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def create_map(pickup_latitude=None, pickup_longitude=None, dropoff_latitude=None, dropoff_longitude=None):

    if pickup_latitude is None or dropoff_latitude is None:
        map_center = [40.7580, -73.9855]
        m = folium.Map(location=map_center, zoom_start=12)

    else:
        map_center = [(pickup_latitude + dropoff_latitude) / 2, (pickup_longitude + dropoff_longitude) / 2]
        m = folium.Map(location=map_center, zoom_start=12)

        folium.Marker(
            [pickup_latitude, pickup_longitude],
            popup="Pickup location",
            icon=folium.Icon(color="blue", icon="cloud")
        )

        folium.Marker(
            [dropoff_latitude, dropoff_longitude],
            popup="Dropoff location",
            icon=folium.Icon(color="red", icon="cloud")
        )

    return m

st.markdown('''
            # TaxiFare - *NYC baby!*
''')

'''
## Tell us more about your plan:
'''
d = st.date_input(
    "When?",
    datetime.date.today())
st.write('You need a ride on',d)

t = st.time_input('What time?', datetime.time(12, 00))
st.write('At', t)

pickup_address = st.text_input("Enter pickup address", "Time Square, NYC")
dropoff_address = st.text_input("Enter dropoff address", "Central Park, NYC")

pickup_longitude, pickup_latitude = get_coordinates(pickup_address)
dropoff_longitude, dropoff_latitude = get_coordinates(dropoff_address)

map_obj = create_map(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)
folium_static(map_obj)

passenger_count = st.number_input('How many passenger(s)?', value=0.0)
st.write(passenger_count, ' people will take a ride')

if pickup_latitude and dropoff_latitude:
    st.write(f"📍 Pickup Location: {pickup_latitude}, {pickup_longitude}")
    st.write(f"📍 Dropoff Location: {dropoff_latitude}, {dropoff_longitude}")
    params = {
        "pickup_datetime": f"{d} {t}",
        "pickup_longitude": float(pickup_longitude),
        "pickup_latitude": float(pickup_latitude),
        "dropoff_longitude": float(dropoff_longitude),
        "dropoff_latitude": float(dropoff_latitude),
        "passenger_count": int(passenger_count)
    }

    if st.button('Get your fare 🚕'):
        api_url = 'https://taxifare.lewagon.ai/predict'

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            prediction = response.json()
            fare = prediction.get("fare", "Unknown")
            st.success(f"💵 Estimated fare: ${fare:.2f}")
        else:
            st.error(f"Error {response.status_code}. Please check your inputs.")
else:
    st.warning("🤔 Please enter valid addresses!")
