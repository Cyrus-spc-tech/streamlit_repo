import streamlit as st
import time
st.title("This is the title ")
st.subheader("This is the subheader")




st.text("This is the text")
st.write("This is the write")
st.markdown("This is the markdown")
st.markdown("[Sportify](https://open.spotify.com/)  [Youtube](https://www.youtube.com/)")
st.caption("This is the caption ")

st.markdown("___")

st.latex(" \\pm\\sqrt{a^2 + b^2}") #kathex go to the site and lern more math symbols

st.markdown("___")


st.success("This is the success")
st.info("This is the info")
st.warning("This is **the** warning")

st.error("This is the error")
st.exception("This is the exception")

st.markdown("___")   
col1, col2 = st.columns(2)
col1.title("This is Column1")
col1.subheader("This is the subheading")
col1.code("import sklearn as sk\n"
          "import pandas as pd")

col2.title("This is Column2")
col2.subheader("This is the subheading")
with st.spinner("""Loading..."""):
    time.sleep(5)
    st.balloons()
if st.button("Snow"):
    with st.spinner("Loading..."):
        time.sleep(5)
        st.snow()
