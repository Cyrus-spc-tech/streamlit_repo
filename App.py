import streamlit as st
import pandas as pd


st.title("Data Vizulizer")

uplode_file=st.file_uploader("Choose a Csv file", type="csv")
if uplode_file is not None:
    st.write("File Uploded ... ")
