import streamlit as st
from datab import UserDatabase

st.set_page_config(page_title="Local DB", page_icon=":package:")
db = UserDatabase()

st.title("Local DB")

menu = ["Insert User", "Fetch All Users", "Describe Table", "Delete User", "Update User", "Get User by ID","Vizulize Data"]
choice = st.sidebar.selectbox("Menu", menu)
st.sidebar.subheader("Table Discription")
st.sidebar.code('''
table user 
[
id 
name 
email 
password 
]
''')

if choice == "Insert User":
    st.subheader("Insert New User")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Insert"):
        if name and email and password:
            db.insert(name, email, password)
            st.success("Data inserted successfully.")
        else:
            st.warning("Please fill all fields.")

elif choice == "Fetch All Users":
    st.subheader("All Users")
    data = db.fetch()
    if data:
        st.dataframe(data)
    else:
        st.info("No users found.")

elif choice == "Describe Table":
    st.subheader("Table Structure")
    data = db.describe()
    st.dataframe(data)

elif choice == "Delete User":
    st.subheader("Delete User")
    id = st.number_input("Enter ID to delete", min_value=1, step=1)
    if st.button("Delete"):
        db.delete(id)
        st.success("Data deleted successfully.")

elif choice == "Update User":
    st.subheader("Update User")
    id = st.number_input("Enter ID to update", min_value=1, step=1)
    name = st.text_input("New Name")
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Update"):
        if name and email and password:
            db.update(id, name, email, password)
            st.success("Data updated successfully.")
        else:
            st.warning("Please fill all fields.")

elif choice == "Get User by ID":
    st.subheader("Get User by ID")
    id = st.number_input("Enter ID to fetch user", min_value=1, step=1)
    if st.button("Fetch User"):
        user = db.get_user_by_id(id)
        if user:
            st.write(user)
        else:
            st.warning("User not found.")

elif choice == "Vizulize Data":
    st.subheader("Visualize Data")
    data = db.fetch()
    if data:
        import pandas as pd
        import matplotlib.pyplot as plt

        df = pd.DataFrame(data, columns=["ID", "Name", "Email", "Password"])
        st.dataframe(df)

        # Example visualization: Count of users by name
        user_counts = df['Name'].value_counts()
        st.bar_chart(user_counts)
    else:
        st.info("No data to visualize.")