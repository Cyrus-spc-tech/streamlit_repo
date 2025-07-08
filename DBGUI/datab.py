import sqlite3
import streamlit as st
class UserDatabase:
    def __init__(self, db_name="Users.db"):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )""")
        con.commit()
        con.close()

    def insert(self, name, email, password):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        con.commit()
        con.close()

    def fetch(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM user")
        data = cur.fetchall()
        con.close()
        return data

    def describe(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("PRAGMA table_info(user)")
        data = cur.fetchall()
        con.close()
        return data

    def delete(self, id):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("DELETE FROM user WHERE id=?", (id,))
        con.commit()
        con.close()

    def update(self, id, name, email, password):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("UPDATE user SET name=?, email=?, password=? WHERE id=?", (name, email, password, id))
        con.commit()
        con.close()

    def get_user_by_id(self, id):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE id=?", (id,))
        data = cur.fetchone()
        con.close()
        return data
