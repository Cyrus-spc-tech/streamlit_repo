import streamlit as st
import requests
from bs4 import BeautifulSoup
# this is using unsplase web scrap

st.markdown("<h1>WebPod</h1>",unsafe_allow_html=True)
# st.image("https://plus.unsplash.com/premium_photo-1675714692342-01dfd2e6b6b5")
with st.form("Search > "):
    keyword=st.text_input("Search the keyword : ")
    search=st.form_submit_button("Go")

    if search :
        page=requests.get(f"https://unsplash.com/s/photos/{keyword}")
        soup=BeautifulSoup(page.content,'lxml')
        rows=soup.find_all("div",class_="I7e4t")
        print(len(rows))