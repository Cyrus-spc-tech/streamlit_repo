import streamlit as st
from DB import DB
import pandas as pd
import os

st.set_page_config(page_title="Dynamic DB", page_icon=":package:")
db = DB()

st.markdown("<p style='color:red;font-size:40px;font-family:Sreda'>Dynamic DB", unsafe_allow_html=True)

# Get all tables
tables = db.get_all_tables()
if not tables:
    st.error("No tables found in database!")
    st.stop()
st.sidebar.title("DB Config")
selected_table = st.sidebar.selectbox("Select Table", tables)
# table structure will be displayed here 
st.sidebar.subheader("Table Structure")
columns_info = db.get_table_columns(selected_table)
if columns_info:
    structure_text = f"Table: {selected_table}\n[\n"
    for col in columns_info:
        structure_text += f"{col['name']} ({col['type']})\n"
    structure_text += "]"
    st.sidebar.code(structure_text)

# Main menu
menu = ["Create Custom Table","Insert Data", "View All Data", "Table Structure", "Update Record", "Delete Record", "Get Record by ID", "Visualize Data"]
choice = st.selectbox("Select Operation", menu)


if choice == "Insert Data":
    st.subheader(f"Insert Data into {selected_table}")
    pass
    

elif choice == "Create Custom Table":
    st.subheader("Create Custom Table")
    table_name = st.text_input("Table Name")
    pass


elif choice == "View All Data":
     st.subheader(f"All Data from {selected_table}")
     data = db.fetch_custom_table(selected_table)

     if data is not None and not data.empty:
        st.dataframe(data, use_container_width=True)


        
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{selected_table}_data.csv",
            mime="text/csv"
        )




elif choice == "Table Structure":
    st.subheader(f"Structure of {selected_table}")
    structure = db.describe_custom_table(selected_table)

    if structure is not None:
        st.dataframe(structure, use_container_width=True)
    else:
        st.error("Could not fetch table structure.")



elif choice == "Update Record ":
    st.subheader(f"Update Record in {selected_table}")

    pass



elif choice == "Delete Record ":
    st.subheader(f"Delete Record from {selected_table}")
    pass


elif choice == "Get Reccord by ID":
    st.subheader(f"Get Record from {selected_table}")
    pass


elif choice == "Visualize Data":
    st.subheader(f"Visualize Data from {selected_table}")
    pass