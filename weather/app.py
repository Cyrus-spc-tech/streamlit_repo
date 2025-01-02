import streamlit as st
import requests

# Function to fetch weather data
def get_weather_data(location):
    api_key = "c978c0732a3d3e0b91f6a62b22c7cc27"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Streamlit app layout
st.title("Weather Dashboard 🌤️")
location = st.text_input("Enter a city name:")

if location:
    weather_data = get_weather_data(location)
    if weather_data.get("main"):
        st.subheader(f"Current Weather in {location}")
        st.write(f" 🌡️ Temperature: {weather_data['main']['temp']} °C")
        st.write(f" ☁️ Weather: {weather_data['weather'][0]['description']}")
        st.write(f" 💧 Humidity: {weather_data['main']['humidity']}%")
        st.write(f" 💨 Wind Speed: {weather_data['wind']['speed']} m/s ")
    else:
        st.error("Location not found. Please try again.")
