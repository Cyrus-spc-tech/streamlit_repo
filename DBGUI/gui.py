from DB import DB
import streamlit as st
import pandas as pd

st.set_page_config(page_title="DB GUI", page_icon=":guardsman:", layout="wide")

tab1,tab2,tab3 = st.tabs(["Insert Data", "Fetch Data", "Describe"])

tab1.subheader("Insert Data")
with tab1:
    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Insert Data"):
        db = DB()
        db.insert(name, email, password)
        st.success("Data inserted successfully.")
        st.balloons()


tab2.subheader("Fetch Data")




tab3.subheader("Describe Table")


