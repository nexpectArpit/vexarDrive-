import streamlit as st
import pickle
import requests
from src.config import PROCESSED_DATA_PATH
from src.ui.common import inject_styles_and_scripts, render_sidebar_logo
from src.ui.driver_page import render_driver_page
from src.ui.vehicle_page import render_vehicle_page

st.set_page_config(
    page_title="VexarDrive Fleet Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_styles_and_scripts()

@st.cache_data
def load_data():
    with open(PROCESSED_DATA_PATH, 'rb') as f:
        return pickle.load(f)

@st.cache_data
def get_road_route(start_lat, start_lon, end_lat, end_lon):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if 'routes' in data and len(data['routes']) > 0:
                coords = data['routes'][0]['geometry']['coordinates']
                return [[c[1], c[0]] for c in coords]
    except Exception:
        pass
    return [[start_lat, start_lon], [end_lat, end_lon]]

try:
    data = load_data()
    drivers = data['drivers']
    vehicles = data['vehicles']
    trips = data['trips']
    telemetry = data['telemetry']
except FileNotFoundError:
    st.error("Preprocessed data file not found! Please run 'python3 -m src.data.preprocessor' first.")
    st.stop()

page = render_sidebar_logo()

if page == "Driver Behaviour Dashboard":
    render_driver_page(drivers, trips, telemetry, get_road_route)
else:
    render_vehicle_page(vehicles)
