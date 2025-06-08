from DB import DB
import pandas as pd 

obj=DB()

print("1. Insert Data")
print("2. Fetch Data")
print("3. Describe Table")
print("4. Delete Data")

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
    # print("Data deleted successfully.")
else:
    print("Invalid choice. Please try again.")