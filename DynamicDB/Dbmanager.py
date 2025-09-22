import sqlite3
import pandas as pd
import os 

class DBManager:
    def __init__(self):
        self.databases = {}
        self.selected_db = None
        self.load_existing_databases()

    def show_tables(self,db_name):
        if db_name in self.databases:
            cursor = self.databases[db_name].cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        else:
            print(f"Database {db_name} not found.")
            return None
    
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
    
        col_defs = ", ".join([f'\"{name}\" {dtype}' for name, dtype in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs});"
        cursor = self.databases[self.selected_db].cursor()
        cursor.execute(sql)
        self.databases[self.selected_db].commit()

    def insert():
        