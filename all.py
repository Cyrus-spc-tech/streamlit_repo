import streamlit as st
import time
import numpy as np
import pandas as pd
st.set_page_config(layout="centered", page_icon=":knot:", page_title="All-Configurations")
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
# with st.spinner("""Loading..."""):
#     time.sleep(5)
#     st.balloons()
# if st.button("Snow"):
#     with st.spinner("Loading..."):
#         time.sleep(5)
#         st.snow()
with st.echo("This is the echo"):
    st.write("This is the echo")
#Adding Input Boxes
st.text_input("Enter the text")
st.number_input("Enter the number")
st.text_area("Enter the text")
st.date_input("Enter the date")
st.time_input("Enter the time", value=None)
st.selectbox("Select the option", ["1", "2", "3"])
st.multiselect("Select the option", ["1", "2", "3"])
a=st.slider("Select the range", 0, 100)
st.write(a)
#Adding 

b=st.button("Toast")
if b:
    st.toast("clicked")
st.markdown("___")

#Graphs and figures 
element=st.container()
element.write("This is the container")
element.line_chart({"data":[1,2,3,4,5]})
element.bar_chart({"data":[1,2,3,4,5]})
element.area_chart({"data":[1,2,3,4,5]})
# element.pyplot()
# element.altair_chart()
# element.vega_lite_chart()
# element.deck_gl_chart()
# element.pydeck_chart()
# element.map()

element.image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png")
element.video("https://www.youtube.com/watch?v=9bZkp7q19f0")
element.audio("https://www.youtube.com/watch?v=9bZkp7q19f0")
#downloading text file 
element.download_button("Click me", "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png")
element.file_uploader("Upload the file")
#Tables
table=pd.DataFrame({"A":[1,2,3,4,5], "B":[6,7,8,9,10], "C":[11,12,13,14,15], "D":[16,17,18,19,20]})
element.write(table)

def change():
    print(st.session_state.checker)
def btnclicked():
    st.toast("clicked")

state=st.checkbox("Select the option",value=True,on_change=change,key="checker")
radio=st.radio("Select the option",["1", "2", "3"],index=0,key="radio")
btn=st.button("Click me for a toast",on_click=btnclicked,key="btn")
multiselect=st.multiselect("Select the option",["1", "2", "3"],key="multiselect")


# if state:
#     element.write("hi")
# else:
#     pass
