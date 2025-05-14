import streamlit as st
import requests
import pandas as pd
# Function to fetch weather data
st.set_page_config(page_title="Weather Dashboard", page_icon=":sunny:", layout="centered", initial_sidebar_state="auto", menu_items=None)
def get_weather_data(location):
    api_key = "c978c0732a3d3e0b91f6a62b22c7cc27"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Streamlit app layout
st.title("Weather Dashboard 🌤️")
location = st.text_input("Enter a city name:")
col1, col2= st.columns(2)

if location:
    weather_data = get_weather_data(location)
    if weather_data.get("main"):
        
        
        with col1:
            st.code(f" 🗺️ Current Weather in {location}")
           
            st.code(f" 🌡️ Temperature: {weather_data['main']['temp']} °C")
            st.code(f" ☁️ Weather: {weather_data['weather'][0]['description']}")
            st.code(f" 💧 Humidity: {weather_data['main']['humidity']}%")
            st.code(f" 💨 Wind Speed: {weather_data['wind']['speed']} m/s ")
            st.code(f" 🌍 Coordinates: {weather_data['coord']['lon']}, {weather_data['coord']['lat']}")
            # st.code(f" 🌡️ Min Temperature: {weather_data['main']['temp_min']} °C")
            # st.code(f" 🌡️ Max Temperature: {weather_data['main']['temp_max']} °C")

        with col2:
            st.code(f" 🌞 Sunrise: {pd.to_datetime(weather_data['sys']['sunrise'], unit='s')}")
            st.code(f" 🌜 Sunset: {pd.to_datetime(weather_data['sys']['sunset'], unit='s')}")
            st.code(f" 🪟 Visibility: {weather_data['visibility'] / 1000} km")
            st.code(f" 🌤️ Cloudiness: {weather_data['clouds']['all']}%")
            st.code(f" 📍 Pressure: {weather_data['main']['pressure']} hPa")
            st.write(f" ☁️ Weather Icon: ![Icon](http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@2x.png)")

    else:
        st.error("Location not found. Please try again.")
