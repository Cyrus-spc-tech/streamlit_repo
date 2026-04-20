"""Streamlit app for working with DatabaseManager.

Run with:
    streamlit run db_manager_app.py
"""

import json
from pathlib import Path

import pandas as pd
import sqlite3
import streamlit as st

import dynamicdatab

st.set_page_config(page_title="Dynamic DB Manager", page_icon="🗄️", layout="wide")

st.title("🗄️ Dynamic Database Manager")

# ------------------------------------------------------------------
# Initialise / retrieve DatabaseManager in session state
# ------------------------------------------------------------------
if "db_manager" not in st.session_state:
    st.session_state.db_manager = dynamicdatab.DatabaseManager()

mgr: dynamicdatab.DatabaseManager = st.session_state.db_manager

# ------------------------------------------------------------------
# Sidebar – pick / create database
# ------------------------------------------------------------------
st.sidebar.header("Databases")

db_names = sorted(mgr.databases.keys())
selected_db = st.sidebar.selectbox("Select database", db_names, index=0 if db_names else None, key="selected_db")

if st.sidebar.button("Connect") and selected_db:
    mgr.connect_to_database(selected_db)

new_db_name = st.sidebar.text_input("New database name", key="new_db")
if st.sidebar.button("Create DB") and new_db_name:
    mgr.create_database(new_db_name)
    st.rerun()

if mgr.selected_db:
    st.sidebar.success(f"Connected to: {mgr.selected_db}")
else:
    st.sidebar.warning("No database selected.")

# ------------------------------------------------------------------
# Main area – operations only if a DB is selected
# ------------------------------------------------------------------
if mgr.selected_db:
    tabs = st.tabs(["Tables", "Create Table", "Run SQL", "Visualize", "Analyze"])

    # ----------------- Tables tab -----------------
    with tabs[0]:
        tables = mgr.show_tables(mgr.selected_db) or []
        st.subheader("Tables in database")
        if tables:
            chosen_table = st.selectbox("Select a table to preview", tables, key="preview_table")
            if st.button("Refresh", key="refresh_preview"):
                pass  # triggers rerun
            if chosen_table:
                try:
                    rows = mgr.fetch(chosen_table)
                    df = pd.DataFrame(rows, columns=[desc[0] for desc in mgr.databases[mgr.selected_db].cursor().execute(f"PRAGMA table_info({chosen_table})").fetchall()])
                    st.dataframe(df)
                except sqlite3.Error as e:
                    st.error(f"Error fetching table: {e}")
        else:
            st.info("No tables found in this database.")

    # ----------------- Create Table tab -----------------
    with tabs[1]:
        st.subheader("Create a New Table")
        with st.form("create_table_form"):
            table_name = st.text_input("Table name", key="ct_name")
            columns_raw = st.text_area(
                "Columns (one per line, format: name TYPE, e.g. id INTEGER PRIMARY KEY)",
                key="ct_cols",
            )
            submitted = st.form_submit_button("Create Table")
            if submitted:
                if not table_name or not columns_raw.strip():
                    st.error("Provide table name and at least one column definition.")
                else:
                    columns = {}
                    for line in columns_raw.splitlines():
                        if not line.strip():
                            continue
                        try:
                            col_name, col_type = line.strip().split(None, 1)
                        except ValueError:
                            st.error(f"Invalid definition: {line}")
                            st.stop()
                        columns[col_name] = col_type
                    mgr.create_table(table_name, columns)
                    st.success(f"Table '{table_name}' created (if not existed).")
                    st.rerun()

    # ----------------- SQL tab -----------------
    with tabs[2]:
        st.subheader("Run SQL or Quick Commands")
        cmd_mode = st.radio("Mode", ["Raw SQL", "Fetch", "Update", "Delete"], horizontal=True)

        if cmd_mode == "Raw SQL":
            sql_code = st.text_area("SQL", height=150, key="sql_area")
            if st.button("Execute", key="execute_sql") and sql_code.strip():
                con = mgr.databases[mgr.selected_db]
                cursor = con.cursor()
                try:
                    cursor.execute(sql_code)
                    con.commit()
                    if sql_code.strip().lower().startswith("select"):
                        rows = cursor.fetchall()
                        cols = [desc[0] for desc in cursor.description] if cursor.description else []
                        st.dataframe(pd.DataFrame(rows, columns=cols))
                    else:
                        st.success(f"Query executed successfully. Rows affected: {cursor.rowcount}")
                except sqlite3.Error as e:
                    st.error(f"SQL Error: {e}")
        elif cmd_mode == "Fetch":
            table = st.selectbox("Table", mgr.show_tables(mgr.selected_db), key="fetch_tbl")
            where = st.text_input("WHERE clause (optional)")
            if st.button("Fetch"):
                rows = mgr.fetch(table, where_clause=where or None)
                st.dataframe(pd.DataFrame(rows))
        elif cmd_mode == "Update":
            table = st.selectbox("Table", mgr.show_tables(mgr.selected_db), key="upd_tbl")
            col_vals = st.text_area("Set columns (JSON: {\"name\":\"Alice\"})", key="upd_vals")
            where = st.text_input("WHERE clause")
            if st.button("Update"):
                try:
                    updates = json.loads(col_vals)
                    mgr.update(table, updates, where)
                    st.success("Rows updated.")
                except Exception as e:
                    st.error(f"Error: {e}")
        elif cmd_mode == "Delete":
            table = st.selectbox("Table", mgr.show_tables(mgr.selected_db), key="del_tbl")
            where = st.text_input("WHERE clause (leave blank to delete all rows)")
            if st.button("Delete"):
                mgr.delete(table, where)
                st.success("Rows deleted.")
    # ----------------- Visualize tab -----------------
    with tabs[3]:
        st.subheader("Visualize Table Data")
        tables_for_viz = mgr.show_tables(mgr.selected_db) or []
        if tables_for_viz:
            table_v = st.selectbox("Table", tables_for_viz, key="viz_tbl")
            if table_v:
                df_v = pd.DataFrame(mgr.fetch(table_v))
                if not df_v.empty:
                    st.dataframe(df_v.head())
                    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Histogram", "Pie"])
                    x_col = st.selectbox("X Column", df_v.columns)
                    y_col = None
                    if chart_type in ["Bar", "Line", "Scatter"]:
                        y_col = st.selectbox("Y Column", df_v.columns, index=1)
                    import plotly.express as px
                    fig = None
                    if chart_type == "Bar":
                        fig = px.bar(df_v, x=x_col, y=y_col)
                    elif chart_type == "Line":
                        fig = px.line(df_v, x=x_col, y=y_col)
                    elif chart_type == "Scatter":
                        fig = px.scatter(df_v, x=x_col, y=y_col)
                    elif chart_type == "Histogram":
                        fig = px.histogram(df_v, x=x_col)
                    elif chart_type == "Pie":
                        fig = px.pie(df_v, names=x_col)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Create a table first.")

    # ----------------- Analyze tab -----------------
    with tabs[4]:
        st.subheader("Analyze Table")
        tables_an = mgr.show_tables(mgr.selected_db) or []
        if tables_an:
            table_a = st.selectbox("Table", tables_an, key="an_tbl")
            if table_a:
                df_a = pd.DataFrame(mgr.fetch(table_a))
                if not df_a.empty:
                    st.write("Summary Statistics")
                    st.write(df_a.describe(include='all'))
        else:
            st.info("No tables to analyze.")
else:
    st.info("Use the sidebar to create or connect to a database.")
