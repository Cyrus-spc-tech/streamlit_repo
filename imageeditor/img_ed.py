import streamlit as st
from PIL import Image
from PIL.ImageFilter import *

st.markdown("<h1 style='text-align: center;'><u style='color:lightgreen;'>ImgPod</u></h1>",unsafe_allow_html=True)
st.markdown("---")

image=st.file_uploader("Upload image you want to edit ")

size=st.empty()
mode=st.empty()
format=st.empty()


if image:   
    img = Image.open(image)
    size.code(f"size:{img.size}       mode:{img.mode}       format:{img.format}")
    st.image(img, caption="Uploaded Image", use_column_width=True)
    
    st.markdown("<h2 style='color: lightgreen; text-align: center;'>Resize</h2>",unsafe_allow_html=True)
    width=st.number_input("Width: ",value=img.width)
    height=st.number_input("height: ",value=img.height)

    
    st.markdown("<h2 style='color: lightgreen; text-align: center;'>Rotation</h2>",unsafe_allow_html=True)
    rot=st.number_input("Degree :")

    st.markdown("<h2 style='color: lightgreen; text-align: center;'>Filters</h2>",unsafe_allow_html=True)
    filters=st.selectbox("Filters",options=["none","blur","Details","smooth",""])


    s_btn=st.button("submit")
    if s_btn:
        edited=img.resize((width,height)).rotate(rot)
        filtered=edited 
        # st.image(edited)
        if filters != "none":
            if filters=="blur":
                filtered=edited.filter(BLUR)
            elif filters == "Details":
                filtered=edited.filter(DETAIL)
            elif filters =="smooth":
                filtered=edited.filter(SMOOTH)
        st.image(filtered)