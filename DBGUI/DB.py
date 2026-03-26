import mysql.connector as conn
import pandas as pd 

class DB:
    def __init__(self):
        # First connect without specifying database to create it if needed
        temp_db = conn.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Tanishh#123'
        )
        cursor = temp_db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS techstack")
        temp_db.close()
        
        # Now connect to the specific database
        self.db=conn.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Tanishh#123',
            database='techstack'        
        )
    
        query="create table if not exists user_data (id int primary key auto_increment, name varchar(50), email varchar(50), password varchar(50))"
        c=self.db.cursor()
        c.execute(query)
        self.db.commit()
        print("Table created successfully")
        c.close()


# for sidebar on st
    def get_all_tables(self):
        try:
            query = "SHOW TABLES"
            c = self.db.cursor()
            c.execute(query)
            tables = [table[0] for table in c.fetchall()]
            c.close()
            return tables
        except Exception as e:
            print(f"Error fetching tables: {e}")
            return []
    def get_table_columns(self, table_name):

        query = f"DESCRIBE `{table_name}`"
        c = self.db.cursor()
        c.execute(query)
        columns_info = c.fetchall()
        c.close()
        
        # Return list of tuples: (column_name, data_type, is_nullable, key)
        columns = []
        for col in columns_info:
            columns.append({
                'name': col[0],
                'type': col[1],
                'nullable': col[2],
                'key': col[3],
                'default': col[4],
                'extra': col[5]
            })
        return columns


# custom tbl fx 

    def create_custom_table(self, table_name, columns_with_types):
    
        try:
            # Mapping Py types to MySQL types
            type_mapping = {
                'int': 'INT',
                'varchar': 'VARCHAR(300)',
                'text': 'TEXT',
                'float': 'FLOAT',
                'datetime': 'DATETIME',
                'boolean': 'BOOLEAN'
            }
            
            # Build column definitions
            column_defs = []
            for col_name, col_type in columns_with_types.items():
                mysql_type = type_mapping.get(col_type.lower(), 'VARCHAR(300)')
                column_defs.append(f"`{col_name}` {mysql_type}")

            column_defs.insert(0, "id INT PRIMARY KEY AUTO_INCREMENT")
        
            columns_str = ", ".join(column_defs)
            query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_str})"
            
            c = self.db.cursor()
            c.execute(query)
            self.db.commit()
            c.close()
            print(f"Table '{table_name}' created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating table: {e}")
            return False


# insert fx
    def insert_into_custom_table(self, table_name, data):
        try:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ", ".join(["%s"] * len(values))
            columns_str = ", ".join([f"`{col}`" for col in columns])
            
            query = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
            
            c = self.db.cursor()
            c.execute(query, values)
            self.db.commit()
            c.close()
            print(f"Data inserted into '{table_name}' successfully!")
            return True
            
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False


# spec fetch fx 

    def fetch_custom_table(self, table_name):
        
        try:
            query = f"SELECT * FROM `{table_name}`"
            c = self.db.cursor()
            c.execute(query)
            data = c.fetchall()
            
            c.execute(f"DESCRIBE `{table_name}`")
            columns_info = c.fetchall()
            columns = [col[0] for col in columns_info]
            
            df = pd.DataFrame(data, columns=columns)
            print(f"Data from '{table_name}':")
            print(df)
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

# struct of tbl 

    def describe_custom_table(self, table_name):

        try:
            query = f"DESCRIBE `{table_name}`"
            c = self.db.cursor()
            c.execute(query)
            data = c.fetchall()
            df = pd.DataFrame(data, columns=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra'])
            print(f"Structure of '{table_name}':")
            print(df)
            return df
            
        except Exception as e:
            print(f"Error describing table: {e}")
            return None

# spec del fx

    def delete_from_custom_table(self, table_name, id):
        try:
            query = f"DELETE FROM `{table_name}` WHERE id = %s"
            c = self.db.cursor()
            c.execute(query, (id,))
            self.db.commit()
            c.close()
            print(f"Record deleted from '{table_name}' successfully!")
            return True
            
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False
    
    

    
    
    
    



# default fx
'''
    def insert(self, name, email, password):
        query="insert into user_data (name, email, password) values (%s, %s, %s)"
        c=self.db.cursor()
        c.execute(query, (name, email, password))
        self.db.commit()
        c.close()

    def fetch(self):
        query="select * from user_data"
        c=self.db.cursor()
        c.execute(query)
        data=c.fetchall()
        df=pd.DataFrame(data, columns=['id', 'name', 'email', 'password'])
        
        print(df)
    
    def describe(self):
        query="describe user_data"
        c=self.db.cursor()
        c.execute(query)
        data=c.fetchall()
        df=pd.DataFrame(data, columns=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra'])
        
        print(df)
    
    def Delete(self,id):
        query="delete from user_data where id=%s"
        c=self.db.cursor()
        c.execute(query, (id,))
        self.db.commit()
        c.close()
        print("Data deleted successfully")

'''