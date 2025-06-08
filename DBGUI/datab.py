import sqlite3

con = sqlite3.connect("Users.db")
cur=con.cursor()

cur.execute("""CREATE TABLE IF NOT EXIST user(id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT NOT NULL,
password TEXT NOT NULL)""")
con.commit()
con.close()

def insert(name, email, password):
    con = sqlite3.connect("Users.db")
    cur = con.cursor()
    cur.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    con.commit()
    con.close()

def fetch():
    con = sqlite3.connect("Users.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM user")
    data = cur.fetchall()
    con.close()
    return data