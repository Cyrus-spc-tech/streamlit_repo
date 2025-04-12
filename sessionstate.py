import streamlit as st
import pandas as pd 

st.title("A session State : ")

csv = pd.read_csv("data.csv",sep=";")
df=pd.DataFrame(csv)
if 'row' not in st.session_state:
    st.session_state.row = 5

inc = st.button('Add more row ')
if inc :
    st.session_state.row += 1

dec= st.button("Decrease row ")
if dec:
    st.session_state.row -= 1

st.table(df.head(st.session_state.row))
st.write("This is the session state row : ", st.session_state.row)