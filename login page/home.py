import streamlit as st

# Check for query parameters to display different content
query_params = st.query_params

# Using key notation
if query_params.get("page") == "home":
    st.title("Home Page")
    st.write("Welcome to the home page!")
else:
    st.title("Access Denied")
    st.write("You need to log in first.")