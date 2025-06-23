import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Streamlit page configuration
st.set_page_config(page_title="Weather Dashboard", page_icon=":sunny:", layout="centered", initial_sidebar_state="auto", menu_items=None)

# Function to fetch current weather data
def get_weather_data(location):
    api_key = "c978c0732a3d3e0b91f6a62b22c7cc27"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"Error fetching current weather data: {e}")
        return {}

# Function to fetch forecast data
def get_forecast_data(location):
    api_key = "c978c0732a3d3e0b91f6a62b22c7cc27"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"Error fetching forecast data: {e}")
        return {}

# Function to process rain forecast
def check_rain_forecast(data):
    if not data or 'list' not in data:
        return None

    forecast = []
    current_time = datetime.utcnow()

    for entry in data['list'][:4]:  
        forecast_time = datetime.fromtimestamp(entry['dt'])
        if forecast_time > current_time + timedelta(hours=12):
            break

        weather = entry['weather'][0]
        rain_info = entry.get('rain', {})
        rain_volume = rain_info.get('3h', 0) 

        forecast.append({
            'time': forecast_time.strftime('%Y-%m-%d %H:%M'),
            'description': weather['description'],
            'rain_volume': rain_volume,
            'will_rain': rain_volume > 0,
            'icon': weather['icon']
        })

    return forecast

# Function to display rain forecast
def display_rain_forecast(location, forecast):
    st.subheader(f"12-Hour Rain Forecast for {location} 🌧️")
    total_entries = len(forecast)
    rain_entries = sum(1 for entry in forecast if entry['will_rain'])
    rain_percent = (rain_entries / total_entries) * 100 if total_entries > 0 else 0
    st.info(f"🌧️ Probability of rain in next 12 hours: {rain_percent:.0f}%")
    for entry in forecast:
        with st.container():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.code(f"Time: {entry['time']}")
                st.code(f"Weather: {entry['description'].capitalize()}")
                st.write(f"Icon: ![Icon](http://openweathermap.org/img/wn/{entry['icon']}@2x.png)")
            with col2:
                rain_status = "Rain expected 🌧️" if entry['will_rain'] else "No rain expected ☀️"
                st.code(f"Status: {rain_status}")
                if entry['will_rain']:
                    st.code(f"Rain Volume: {entry['rain_volume']} mm")

tab = st.tabs(["Current Weather", "Rain Forecast"])
tab1, tab2 = tab

# Streamlit app layout
with tab1:
    st.title("Weather Dashboard 🌤️")
    location = st.text_input("Enter a city name:", value="chandigarh")

    col1, col2 = st.columns(2)

    if location:
        # Fetch and display current weather
        weather_data = get_weather_data(location)
        if weather_data.get("main"):
            with col1:
                st.code(f" 🗺️ Current Weather in {location}")
                st.code(f" 🌡️ Temperature: {weather_data['main']['temp']} °C")
                st.code(f" ☁️ Weather: {weather_data['weather'][0]['description']}")
                st.code(f" 💧 Humidity: {weather_data['main']['humidity']}%")
                st.code(f" 💨 Wind Speed: {weather_data['wind']['speed']} m/s ")
                st.code(f" 🌍 Coordinates: {weather_data['coord']['lon']}, {weather_data['coord']['lat']}")

            with col2:
                st.code(f" 🌞 Sunrise: {pd.to_datetime(weather_data['sys']['sunrise'], unit='s')}")
                st.code(f" 🌜 Sunset: {pd.to_datetime(weather_data['sys']['sunset'], unit='s')}")
                st.code(f" 🪟 Visibility: {weather_data['visibility'] / 1000} km")
                st.code(f" 🌤️ Cloudiness: {weather_data['clouds']['all']}%")
                st.code(f" 📍 Pressure: {weather_data['main']['pressure']} hPa")
                st.write(f" ☁️ Weather Icon: ![Icon](http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@2x.png)")
        else:
            st.error("Location not found. Please try again.")

with tab2:
    if location:
        with st.spinner("Fetching rain forecast..."):
            forecast_data = get_forecast_data(location)
            if forecast_data.get("list"):
                forecast = check_rain_forecast(forecast_data)
                if forecast:
                    display_rain_forecast(location, forecast)
                else:
                    st.error("No forecast data available.")
    else:
        st.error("Location not found. Please try again.")