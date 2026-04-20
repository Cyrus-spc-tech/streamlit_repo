import streamlit as st
from PIL import Image
from PIL.ImageFilter import *

# st.set_page_config(page_title="Image Editor",page_icon=":camera:",layout="centered")
st.markdown("<h1 style='text-align: center;'><u style='color:lightgreen;'>ImgPod</u></h1>",unsafe_allow_html=True)
st.markdown("---")


image=st.file_uploader("Upload image you want to edit ")

size=st.empty()
mode=st.empty()
format=st.empty()

tab1,tab2=st.tabs(["Image","Edited Image"])


with tab1:
    if image:   
        img = Image.open(image)
        st.image(img, caption="Uploaded Image", use_column_width="auto")
        size.code(f"size: {img.size}       mode: {img.mode}       format: {img.format if hasattr(img, 'format') else 'N/A'}")
        
        st.markdown("<h2 style='color: lightgreen; text-align: center;'>Resize</h2>",unsafe_allow_html=True)
        width = st.number_input("Width: ", value=img.width)
        height = st.number_input("Height: ", value=img.height)
    else:
        st.info("Please upload an image to enable editing options")

    
    st.markdown("<h2 style='color: lightgreen; text-align: center;'>Rotation</h2>",unsafe_allow_html=True)
    rot=st.number_input("Degree :")

with tab2:
    st.markdown("<h2 style='color: lightgreen; text-align: center;'>Filters</h2>",unsafe_allow_html=True)
    filters=st.selectbox("Filters",options=["none","blur","detail","smooth","contour","edge_enhance","emboss","find_edges","sharpen"])

    s_btn=st.button("submit")
    if s_btn:
        edited=img.resize((width,height)).rotate(rot)
        filtered=edited 
        with tab2: # st.image(edited)
            if filters != "none":
                if filters=="blur":
                    filtered=edited.filter(BLUR)
                elif filters == "detail":
                    filtered=edited.filter(DETAIL)
                elif filters =="smooth":
                    filtered=edited.filter(SMOOTH)
                elif filters == "contour":
                    filtered=edited.filter(CONTOUR)
                elif filters == "edge_enhance":
                    filtered=edited.filter(EDGE_ENHANCE)
                elif filters == "emboss":
                    filtered=edited.filter(EMBOSS)
                elif filters == "find_edges":
                    filtered=edited.filter(FIND_EDGES)
                elif filters == "sharpen":
                    filtered=edited.filter(SHARPEN)
        st.image(filtered)
