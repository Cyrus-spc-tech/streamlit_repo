import streamlit as st
import requests
import json 

st.title("Recipe Finder and Meal Planner")

ingre=st.text_input("Enter the ingredients you have (separated by commas )")

url="https://www.themealdb.com/api/json/v1/1/search.php?s={}".format(ingre)
res=requests.get(url)
data=res.json()
if st.button("Find Recipes"):
    st.dataframe(data["meals"])