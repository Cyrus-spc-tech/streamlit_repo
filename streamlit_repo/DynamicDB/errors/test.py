import dynamicdatab

if __name__ == "__main__":
    db = dynamicdatab.DatabaseManager()

    # 1️⃣  Create or connect to a database
    db.create_database("test1")
    db.connect_to_database("test1")  # redundant if just created but works either way

    # 2️⃣  Create a table with custom columns
    db.create_table(
        table_name="users",
        columns={
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "age": "INTEGER",
        },
    )

    # 3️⃣  Insert some rows
    db.insert("users", {"name": "Alice", "age": 30})
    db.insert("users", {"name": "Bob", "age": 25})

    # 4️⃣  Query the data
    rows = db.fetch("users")
    print("All users:", rows)

    # 5️⃣  Update and delete examples
    db.update("users", updates={"age": 31}, where_clause="name = 'Alice'")
    db.delete("users", where_clause="name = 'Bob'")

    print("After modifications:", db.fetch("users"))

    # 6️⃣  Show available tables
    print("Tables in test1:", db.show_tables("test1"))

    db.close()
