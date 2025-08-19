import sqlite3
import pandas as pd 
import os
from colorama import Fore, Style,Back

class DatabaseManager:
    def __init__(self):
        self.databases = {}
        self.selected_db = None
        self.load_existing_databases()
    def load_existing_databases(self):
        for file in os.listdir():
            if file.endswith('.db'):
                db_name = file[:-3]  
                if db_name not in self.databases:
                    try:
                        self.databases[db_name] = sqlite3.connect(file, check_same_thread=False)
                    except Exception as e:
                        print(f"Error loading database {db_name}: {str(e)}")
        if not self.databases:
            self.create_database()

    def create_database(self, db_name):
        """Create a new SQLite database on disk and make it the currently selected DB."""
        if db_name in self.databases:
            print(f"Database {db_name} already exists. Connecting …")
            self.selected_db = db_name
            return self.databases[db_name]
        con = sqlite3.connect(db_name + ".db", check_same_thread=False)
        self.databases[db_name] = con
        self.selected_db = db_name
        return con

    def connect_to_database(self, db_name):
        if db_name in self.databases:
            self.selected_db = db_name
            return self.databases[db_name]
        else:
            print(f"Database {db_name} not found.")
            return None

    def show_tables(self,db_name):
        if db_name in self.databases:
            cursor = self.databases[db_name].cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        else:
            print(f"Database {db_name} not found.")
            return None
            
    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def create_table(self, table_name: str, columns: dict[str, str]):
        """Create a table under the currently selected database.

        Parameters
        ----------
        table_name : str
            Name of the table to create.
        columns : dict[str, str]
            Mapping of column name → SQLite column type, e.g.
            {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
        """
        if not self.selected_db:
            print("No database selected. Call connect_to_database() first.")
            return
        # Quote identifiers to avoid conflicts with SQL reserved keywords
        col_defs = ", ".join([f'"{name}" {dtype}' for name, dtype in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs});"
        cursor = self.databases[self.selected_db].cursor()
        cursor.execute(sql)
        self.databases[self.selected_db].commit()

    def insert(self, table_name: str, row: dict):
        """Insert a row into table_name. `row` is a dict of column → value."""
        if not self.selected_db:
            print("No database selected.")
            return
        cols = ", ".join(row.keys())
        placeholders = ", ".join(["?" for _ in row])
        values = tuple(row.values())
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders});"
        cursor = self.databases[self.selected_db].cursor()
        cursor.execute(sql, values)
        self.databases[self.selected_db].commit()

    def update(self, table_name: str, updates: dict, where_clause: str = ""):
        """Update rows. `updates` is dict column→value, optional raw SQL where_clause."""
        if not self.selected_db:
            print("No database selected.")
            return
        set_expr = ", ".join([f"{col} = ?" for col in updates])
        values = tuple(updates.values())
        sql = f"UPDATE {table_name} SET {set_expr} " + (f"WHERE {where_clause}" if where_clause else "") + ";"
        cursor = self.databases[self.selected_db].cursor()
        cursor.execute(sql, values)
        self.databases[self.selected_db].commit()

    def delete(self, table_name: str, where_clause: str = ""):
        """Delete rows from table_name using an optional where_clause."""
        if not self.selected_db:
            print("No database selected.")
            return
        sql = f"DELETE FROM {table_name} " + (f"WHERE {where_clause}" if where_clause else "") + ";"
        cursor = self.databases[self.selected_db].cursor()
        cursor.execute(sql)
        self.databases[self.selected_db].commit()

    def fetch(self, table_name: str, where_clause: str | None = None):
        """Fetch rows from a table, optionally filtered by a SQL WHERE clause."""
        if self.selected_db:
            cursor = self.databases[self.selected_db].cursor()
            sql = f"SELECT * FROM {table_name} " + (f"WHERE {where_clause}" if where_clause else "") + ";"
            cursor.execute(sql)
            return cursor.fetchall()
        else:
            print("No database selected.")
            return None

    def close(self):
        """Close all open SQLite connections cleanly."""
        for name, con in self.databases.items():
            con.close()
        self.databases.clear()
        self.selected_db = None
    
