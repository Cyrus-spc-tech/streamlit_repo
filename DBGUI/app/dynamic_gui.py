import streamlit as st
from DB import DB
import pandas as pd

st.set_page_config(page_title="Dynamic DB GUI", page_icon=":package:")
db = DB()

st.title("Dynamic Database GUI")

# Get all tables
tables = db.get_all_tables()
if not tables:
    st.error("No tables found in database!")
    st.stop()

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
menu = ["Insert Data", "View All Data", "Table Structure", "Update Record", "Delete Record", "Get Record by ID", "Create Custom Table", "Visualize Data"]
choice = st.selectbox("Select Operation", menu)
