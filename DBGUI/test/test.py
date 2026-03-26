from DB import DB
import pandas as pd 

obj=DB()

print("1. Insert Data (user_data)")
print("2. Fetch Data (user_data)")
print("3. Describe Table (user_data)")
print("4. Delete Data (user_data)")

print("5. Create Custom Table with Columns")
print("6. Insert Data into Custom Table")
print("7. Fetch Custom Table Data")
print("8. Describe Custom Table")
print("9. Delete from Custom Table")

choice = input("Enter your choice: ")

if choice =='1':
    name = input("Enter name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    obj.insert(name, email, password)
    print("Data inserted successfully.")
elif choice == '2':
    obj.fetch()
elif choice == '3':
    obj.describe()
elif choice == '4':
    id = int(input("Enter ID to delete: "))
    obj.Delete(id)
    print("Data deleted successfully.")
    
elif choice == '5':
    # Create custom table
    table_name = input("Enter table name: ")
    print("Enter columns and types (format: column_name:type)")
    print("Supported types: int, varchar, text, float, datetime, boolean")
    print("Example: name:varchar age:int email:varchar")
    
    columns_input = input("Enter columns (comma separated): ")
    columns_with_types = {}
    
    for col_def in columns_input.split(','):
        col_def = col_def.strip()
        if ':' in col_def:
            col_name, col_type = col_def.split(':', 1)
            columns_with_types[col_name.strip()] = col_type.strip()
    
    if columns_with_types:
        obj.create_custom_table(table_name, columns_with_types)
    else:
        print("Invalid column format!")
        
elif choice == '6':
    # Insert into custom table
    table_name = input("Enter table name: ")
    
    # Get table structure first
    print(f"Fetching structure of '{table_name}'...")
    structure = obj.describe_custom_table(table_name)
    
    if structure is not None:
        data = {}
        for field in structure['Field']:
            if field != 'id':  # Skip auto-increment ID
                value = input(f"Enter value for {field} ({structure[structure['Field'] == field]['Type'].values[0]}): ")
                data[field] = value
        
        obj.insert_into_custom_table(table_name, data)
        
elif choice == '7':
    # Fetch custom table
    table_name = input("Enter table name: ")
    obj.fetch_custom_table(table_name)
    
elif choice == '8':
    # Describe custom table
    table_name = input("Enter table name: ")
    obj.describe_custom_table(table_name)
    
elif choice == '9':
    # Delete from custom table
    table_name = input("Enter table name: ")
    id = int(input("Enter ID to delete: "))
    obj.delete_from_custom_table(table_name, id)
    
else:
    print("Invalid choice. Please try again.")