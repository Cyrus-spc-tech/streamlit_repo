import streamlit as st
import time
from datetime import datetime
import threading

def play_alarm():
    st.write("⏰ Time's up!")
    st.balloons()

st.title("Timer with Progress Bar and Alarm")

# Input for the timer duration
duration = st.number_input("Enter the duration in seconds:", min_value=1, max_value=3600, value=10)

if st.button("Start Timer"):
    bar = st.progress(0)
    for i in range(duration):
        bar.progress((i + 1) * 100 // duration)
        time.sleep(1)
    play_alarm()
