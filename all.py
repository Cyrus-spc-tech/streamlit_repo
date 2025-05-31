import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt
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

st.slider("Select the range",key="slider", min_value=0, max_value=100)
st.select_slider("Select the range", options=["1","1.5", "2","2.5", "3"],key="select_slider")
title1 = st.text_input("Enter the text",key="text_input",placeholder="Enter the text")
st.header(title1) 
numb=st.number_input("Enter the number",key="number_input")
st.write(numb)
st.date_input("Enter the date",key="date_input")
val=st.time_input("Enter the time",key="time_input")
st.write(val)
 
for i in range(3):
    st.write(i)
    st.progress(i)
    time.sleep(1)

#Adding Form
st.markdown("___")
st.markdown("<h1>User Registation </h1>",unsafe_allow_html=True)
with st.form("User Registration"):

    col1,col2=st.columns(2)
    F_name=col1.text_input("First Name")
    L_name=col2.text_input("Last Name ")

    email=st.text_input("Enter the email")
    age=st.number_input("Enter the age",min_value=0, max_value=60, step=1)
    day,month,year=st.columns(3)
    st.write("Enter the DOB")
    day.text_input("Day")
    month.text_input("Month")
    year.text_input("Year")

    submit=st.form_submit_button("Submit")
    if submit:
        if F_name == "" and email== "" :
            st.error("Please enter the Details")
        else:
            st.success("The form is submitted")
            st.write(F_name)
            st.write(L_name)
            st.write(email)
            st.write("Age : "+age)

#Adding Expander
st.markdown("___")
with st.expander("FAQ"):
    st.code("Q1 > This is the box", language="python")
    st.code("Q2 > This is the box", language="python")

#aadding Sidebars
st.markdown("___")
st.sidebar.title("Sidebar")
st.sidebar.subheader("This is the subheading")
st.sidebar.markdown("[Sportify](https://open.spotify.com/)")

st.sidebar.markdown(" [Youtube](https://www.youtube.com/)")
st.sidebar.markdown("[![LinkedIn](https://image.flaticon.com/icons/png/512/174/174857.png)](https://www.linkedin.com)")
st.sidebar.markdown("[![GitHub](https://image.flaticon.com/icons/png/512/25/25231.png)](https://github/cyrus-spc-tech.com)")

#adding graphs
option=st.sidebar.radio("select any Graph : ",options=["Line","Bar","Area","vega","Pie","bokeh"])
if option=="Line":
    st.line_chart({"data":[1,2,3,4,5]})
elif option=="Bar":
    st.bar_chart({"data":[1,2,3,4,5]})
elif option=="vega":
    st.vega_lite_chart({"data":[1,2,3,4,5]})
elif option=="Pie":
    st.deck_gl_chart({"data":[1,2,3,4,5]})
elif option=="bokeh":
    st.bokeh_chart({"data":[1,2,3,4,5]})
elif option=="Area":
    st.area_chart({"data":[1,2,3,4,5]})



# tabs
tab1, tab2, tab3, tab4 = st.tabs(["PyGWalker", "Graphic Walker", "GWalkR", "RATH"])

with tab1:
    st.header("PyGWalker")
    st.write("PyGWalker is a Python library for visual data exploration.")
    st.image("logomark_website.png", caption="PyGWalker Example")

with tab2:
    st.header("Graphic Walker")
    st.write("Graphic Walker is a tool for creating interactive visualizations.")
    st.image("logomark_website.png", caption="Graphic Walker Example")


with tab3:
    st.header("GWalkR")
    st.write("GWalkR is an R package for data visualization.")
    st.image("logomark_website.png", caption="GWalkR Example")

with tab4:
    st.header("RATH")
    st.write("RATH is a platform for advanced data analytics.")
    st.image("logomark_website.png", caption="RATH Example")\


# Session state 
st.title("Session State")
"st.session_state object:",st.session_state

##work 
num=st.slider("A no : ",1,10,key="slid")
st.write(st.session_state)

co1,buff,co2=st.columns([1,0.5,1])

option=["a","b","c"]

next=st.button("Next",key="next")
if next:
    if  st.session_state["radio1"] == "a":
        st.session_state["radio1"] = "b"
    elif st.session_state["radio1"] == "b":
        st.session_state["radio1"] = "c"
    elif st.session_state["radio1"] == "c":
        st.session_state["radio1"] = "a"
else:
    st.session_state["radio1"] = "a"


opt=co1.radio("Select the option",options=option,key="radio1")
st.session_state

if opt=="a":
    co2.write("You selected option A")
elif opt=="b":
    co2.write("You selected option B")
elif opt=="c":
    co2.write("You selected option C")