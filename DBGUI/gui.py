from DB import DB
import streamlit as st
import pandas as pd

st.set_page_config(page_title="DB GUI", page_icon=":guardsman:", layout="wide")

tab1,tab2,tab3 = st.tabs(["Insert Data", "Fetch Data", "Describe"])
