import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from airpoll import get_lat_long

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

# Function to fetch air pollution data
def get_air_pollution_data(location):
    api_key = "c978c0732a3d3e0b91f6a62b22c7cc27"
    lat, lon = get_lat_long(location)
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching air pollution data: {e}")
        return {}

def display_air_pollution_data(location, air_pollution_data):
    st.subheader(f"Air Pollution Data for {location} 🌍")
    if air_pollution_data.get("list"):
        data = air_pollution_data['list'][0]
        aqi = data['main']['aqi']
        components = data['components']
        
        # AQI Risk Profile
        aqi_levels = {
            1: {"level": "Good", "color": "🟢", "risk": "Air quality is satisfactory, and air pollution poses little or no risk.", "emoji": "😊"},
            2: {"level": "Fair", "color": "🟡", "risk": "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.", "emoji": "🙂"},
            3: {"level": "Moderate", "color": "🟠", "risk": "Members of sensitive groups may experience health effects. The general public is less likely to be affected.", "emoji": "😐"},
            4: {"level": "Poor", "color": "🔴", "risk": "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.", "emoji": "😷"},
            5: {"level": "Very Poor", "color": "🟣", "risk": "Health alert: The risk of health effects is increased for everyone.", "emoji": "☠️"}
        }
        
        aqi_info = aqi_levels.get(aqi, aqi_levels[3])
        
        # Display AQI with risk profile
        st.markdown(f"### {aqi_info['color']} Air Quality Index: {aqi} - {aqi_info['level']} {aqi_info['emoji']}")
        st.info(f"**Risk Profile:** {aqi_info['risk']}")
        
        # Display pollutant concentrations
        st.markdown("#### 🧪 Pollutant Concentrations (μg/m³)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("CO (Carbon Monoxide)", f"{components.get('co', 0):.2f}")
            st.metric("NO (Nitrogen Monoxide)", f"{components.get('no', 0):.2f}")
            st.metric("NO₂ (Nitrogen Dioxide)", f"{components.get('no2', 0):.2f}")
            st.metric("O₃ (Ozone)", f"{components.get('o3', 0):.2f}")
        
        with col2:
            st.metric("SO₂ (Sulphur Dioxide)", f"{components.get('so2', 0):.2f}")
            st.metric("PM2.5 (Fine Particles)", f"{components.get('pm2_5', 0):.2f}")
            st.metric("PM10 (Coarse Particles)", f"{components.get('pm10', 0):.2f}")
            st.metric("NH₃ (Ammonia)", f"{components.get('nh3', 0):.2f}")
        
        # Health recommendations based on AQI
        st.markdown("#### 💡 Health Recommendations")
        if aqi == 1:
            st.success("✅ Air quality is ideal for outdoor activities.")
        elif aqi == 2:
            st.info("✅ Enjoy outdoor activities. Sensitive individuals should watch for symptoms.")
        elif aqi == 3:
            st.warning("⚠️ Sensitive groups should reduce prolonged outdoor exertion.")
        elif aqi == 4:
            st.warning("⚠️ Everyone should reduce prolonged outdoor exertion. Sensitive groups should avoid it.")
        else:
            st.error("🚨 Everyone should avoid outdoor exertion. Stay indoors and keep windows closed.")
    else:
        st.error("No air pollution data available.")

tab = st.tabs(["Current Weather", "Rain Forecast","Air Pollution"])
tab1, tab2,tab3 = tab

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

with tab3:
    if location:
        with st.spinner("Fetching air pollution data..."):
            air_pollution_data = get_air_pollution_data(location)
            if air_pollution_data.get("list"):
                display_air_pollution_data(location, air_pollution_data)
            else:
                st.error("No air pollution data available.")
    else:
        st.error("Location not found. Please try again.")