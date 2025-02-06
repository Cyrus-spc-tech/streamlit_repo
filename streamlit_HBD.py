import streamlit as st

# title 
st.header("Happy Birthday! 🎂" )

#can show on the left or right side of the page
st.write("Happy birthday to you ... ")

#color picker box 
color=st.color_picker("Pic a color ")

# number slider
number=st.slider("Pick a no. ", 0,100)

# print the data
# print.write(f'you select {color} and {number}')

# add a button 
if st.button("Click Me!"):
    st.write("Hello There ! How are you ? ")
else :
    st.write("GoodBye !")


# adding a radio button 
genre=st.radio(
    "what is your movie genera : ",
    ("Drama", "Action","Entertainment","Thriller")
)
st.balloons()
st.snow()