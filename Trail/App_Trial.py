import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

st.title("Title of the App")
st.header("This is the header")
st.subheader("This is the SubHeader ")
st.markdown("This is the markdown text")
st.caption("This is the caption text")
st.latex(r"E = mc^2")

#code block
code_ex="""
# this is the codespace
    print("Hello World")
"""
st.code(code_ex,language="python")

st.markdown(":sunglasses: :smile: :phone: Emoji support!")

st.divider()#use for <hr>

st.text("This is the super simple text ")
st.image("slider2_4.png",width=150)
st.video("EP9A3_910_Homescreen.mp4")

# click button 
if st.button("Click Me"):
    st.write("Button clicked!")
else:
    st.write("Button not clicked")

# user input 
user_input = st.text_input("Enter some text", "Enter here ")

# Adding html element 
st.markdown(f"You entered: <span style='color:Green;'>{user_input}</span>", unsafe_allow_html=True)

data = {"Column 1": [1, 2, 3], "Column 2": [4, 5, 6]}
df = pd.DataFrame(data)

st.dataframe(df)  # Interactive table
st.table(df)      # Static table

# making a slider 
age = st.slider("Select your age", 0, 100, 25)
st.write("Your age is:", age)

# making a selectbox
option = st.selectbox("Choose an option", ["Option 1", "Option 2", "Option 3"])
st.write("You selected:", option)

#radio button 
rad=st.radio("pick one ",[ "option 1","option2","option3"])
st.write("You have selected : " ,rad)

# checkbox 
agree = st.checkbox("I agree to the T&C")
if agree:
    st.success("You agreed!")
else :
    st.error("You did not agree!")

#date and time function 
date = st.date_input("Pick a date", datetime.now())
st.write("Selected date:", date)

#graph function intractive 
data = np.random.randn(10, 2)
st.line_chart(data)
st.bar_chart(data)
st.area_chart(data)

# static using matplotlib
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [10, 20, 25, 30])
st.pyplot(fig)

# displaying messages 
st.error("This is an error!")
st.warning("This is a warning!")
st.info("This is some information.")
st.success("This is a success message!")

#layout
st.sidebar.title("Sidebar  Here ")
st.sidebar.markdown(
    '''
    <ul style="display:flex; list-style-type: none;">
        <li>
            <a href="https://www.google.com" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg" alt="Google" width="50" style="vertical-align: middle;"/>
            </a>
        </li>
        <li>
            <a href="https://www.youtube.com" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg" alt="YouTube" width="70" style="vertical-align: middle;"/>
            </a>
        </li>
        <li>
            <a href="https://www.github.com" target="_blank">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" width="30" style="vertical-align: middle;"/> 
            </a>
        </li>
    </ul>
    ''',
    unsafe_allow_html=True
)
col1, col2 = st.columns(2)
with col1:
    st.write("Column 1")
    st.write("hello")
with col2:
    st.write("Column 2")
    st.write("world")
# extendable bar 
with st.expander("See More"):
    st.write("This is inside the expander.")
#file uploding 
uploaded_file = st.file_uploader("Choose a file",type="png")
if uploaded_file is not None:
    st.write("Filename:", uploaded_file.name)
    st.image(uploaded_file,width=70)
st.divider()

# navigation bar
st.markdown("<u '><span style='color:Red;'>Use form side Bar</span><u>", unsafe_allow_html=True)
pg = st.navigation([
    st.Page("page1.py"),
    st.Page("page2.py")
])
pg.run()