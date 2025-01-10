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
    else:
        st.error("Invalid username or password")

# Check for query parameters to display different content
query_params = st.query_params

# Using key notation
if query_params.get("page") == "home":
    st.title("Home Page")
    st.write("Welcome to the home page!")

# Using attribute notation
if hasattr(query_params, 'page') and query_params.page == "home":
    st.title("Home Page")
    st.write("Welcome to the home page!")

# Change a query parameter
st.query_params = {"page": "home"}