import streamlit as st

# Set page title
st.title("User Login Page")

# Create input fields for username and password
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Create a login button
if st.button("Login"):
    if username == "correct_username" and password == "correct_password":
        st.query_params = {"page": "home"}
        st.success("Login successful! Redirecting...")
        st.experimental_rerun()
    else:
        st.error("Invalid username or password")

# Check for query parameters to display different content
query_params = st.query_params


# Using key notation
if query_params.get("page") == "home":
    st.write('<meta http-equiv="refresh" content="0; url=home.py">', unsafe_allow_html=True)