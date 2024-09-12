import pyodbc

server = "" # Container Name
database = "" # Database
username = "" # Username
password = "" # Password


connection_string = f""


connection = pyodbc.connect(connection_string)
cursor = connection.cursor()


cursor.execute("SELECT * FROM your_table")
rows = cursor.fetchall()
for row in rows:
    print(row)

connection.close()

