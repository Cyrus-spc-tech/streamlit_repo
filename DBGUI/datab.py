import sqlite3

con = sqlite3.connect("Users.db")
cur=con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def describe():
    con = sqlite3.connect("Users.db")
    cur = con.cursor()
    cur.execute("PRAGMA table_info(user)")
    data = cur.fetchall()
    con.close()
    return data

def delete(id):
    con = sqlite3.connect("Users.db")
    cur = con.cursor()
    cur.execute("DELETE FROM user WHERE id=?", (id,))
    con.commit()
    con.close()

def update(id, name, email, password):
    con = sqlite3.connect("Users.db")
    cur = con.cursor()
    cur.execute("UPDATE user SET name=?, email=?, password=? WHERE id=?", (name, email, password, id))
    con.commit()
    con.close()

def get_user_by_id(id):
    con = sqlite3.connect("Users.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM user WHERE id=?", (id,))
    data = cur.fetchone()
    con.close()
    return data

print("Database and table created successfully.")

print("Available functions:")
print("1. insert(name, email, password)")
print("2. fetch()")
print("3. describe()")
print("4. delete(id)")
print("5. update(id, name, email, password)")
print("6. get_user_by_id(id)")
print("7. exit()")

while True:
    choice = input("Enter your choice: ")
    
    if choice == '1':
        name = input("Enter name: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        insert(name, email, password)
        print("Data inserted successfully.")
    
    elif choice == '2':
        data = fetch()
        for row in data:
            print(row)
    
    elif choice == '3':
        data = describe()
        for row in data:
            print(row)
    
    elif choice == '4':
        id = int(input("Enter id to delete: "))
        delete(id)
        print("Data deleted successfully.")
    
    elif choice == '5':
        id = int(input("Enter id to update: "))
        name = input("Enter new name: ")
        email = input("Enter new email: ")
        password = input("Enter new password: ")
        update(id, name, email, password)
        print("Data updated successfully.")
    
    elif choice == '6':
        id = int(input("Enter id to fetch user: "))
        user = get_user_by_id(id)
        if user:
            print(user)
        else:
            print("User not found.")
    
    elif choice == '7':
        break
    
    else:
        print("Invalid choice. Please try again.")
    
# This code initializes a SQLite database and provides functions to insert, fetch, describe, delete, update, and get user data by ID.