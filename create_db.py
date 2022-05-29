import pymysql

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='useruser',
                             cursorclass=pymysql.cursors.DictCursor)

with connection:
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS users")
        cursor.execute("SHOW DATABASES")
        for db in cursor:
            print(db)
