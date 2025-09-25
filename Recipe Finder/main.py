import streamlit as st
import requests
import json 
from rich import print


st.title("Recipe Finder and Meal Planner")


ingre=st.text_input("Enter the ingredients you have (separated by commas )")
num=st.number_input("Enter the number of recipes you want to find", min_value=1, max_value=10)

url="https://www.themealdb.com/api/json/v1/1/search.php?s={}".format(ingre)
res=requests.get(url)
data=res.json()
col1,col2=st.columns(2)
with col1:
    if st.button("Find Recipes"):
        st.image(data["meals"][0]["strMealThumb"],width=400)
        # st.write(data["meals"][0]["strMeal"])
with col2:
    st.header(data["meals"][0]["strMeal"]) 
    st.subheader(data["meals"][0]["strCategory"]) 
    st.subheader(data["meals"][0]["strArea"]) 

# st.subheader(data["meals"][0]["strYoutube"]) 
st.markdown(f"[Watch Video]({data['meals'][0]['strYoutube']})")
   
    