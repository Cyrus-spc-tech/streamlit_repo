import streamlit as st
import numpy as np 

st.set_page_config(page_icon="🎮",page_title="Gamezzz",layout="centered")
st.title("🎮 Welcome to Gamezzz!")
st.subheader("Your ultimate destination for fun and exciting games!")
st.image("scenery.jpg", use_column_width=True)


st.write("""
Gamezzz is your go-to platform for simple yet entertaining games like "Guess the Number" and more. 
Stay tuned as we keep adding new games to keep the fun going!
""")

st.markdown("<h1 style ='color:lightgreen; align:center;'>Gallary</h1>",unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.image("18.jpg")
    st.image("1.jpg")
    st.image("2.jpg")
with col2:
    st.image("17.jpg")
    st.image("3.jpg")
    st.image("5.jpg")
with col3:
    st.image("11.jpg")
    st.image("4.jpg")
    st.image("6.jpg")

