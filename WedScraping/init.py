import streamlit as st
import requests
from bs4 import BeautifulSoup
import base64

st.set_page_config(layout="centered", page_icon=":camera:", page_title="PhotoPhilia", initial_sidebar_state="expanded")
st.markdown("<h1 style='text-align: center; color:#9d0208; background-color:#ffdab9'>PhotoPhilia</h1>", unsafe_allow_html=True)
st.markdown("")

def get_google_images(query, num_images=6):
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    
    image_urls = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        images = soup.find_all("img")
        for img in images[1:num_images+1]:  # Skipping the first image (usually Google's logo)
            image_urls.append(img["src"])
    return image_urls

def get_image_download_link(img_url, index):
    response = requests.get(img_url)
    if response.status_code == 200:
        b64 = base64.b64encode(response.content).decode()
        href = f'<a href="data:file/jpg;base64,{b64}" download="image{index+1}.jpg">Download Image</a>'
        return href
    return ""

with st.form("Search"):
    keyword = st.text_input("Search the image")
    search = st.form_submit_button("Search")
    load_more = st.form_submit_button("Load More")
    clear = st.form_submit_button("Clear Photos")
    
    if clear:
        st.error("Search Again to see more images.")
    
    if search or load_more:
        if keyword:
            image_urls = get_google_images(keyword, num_images=9)
            if image_urls:
                cols = st.columns(3)  # Display images in 3 columns
                for index, image_url in enumerate(image_urls):
                    with cols[index % 3]:
                        st.image(image_url, caption=f"Image {index+1}", use_container_width=True)
                        st.markdown(get_image_download_link(image_url, index), unsafe_allow_html=True)
            else:
                st.error("No images found. Try another search term.")
        else:
            st.warning("Please enter a search term.")