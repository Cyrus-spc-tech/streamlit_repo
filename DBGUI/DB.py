import mysql.connector as conn
import pandas as pd 

class DB:
    def __init__(self):
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




