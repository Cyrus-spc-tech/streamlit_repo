import streamlit as st

# Set page title
st.title("User Login Page")

# Create input fields for username and password
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Create a login button
if st.button("Login"):
    if username == username and password == password:
        st.success("Login successful!")
    else:
        st.error("Invalid username or password")
