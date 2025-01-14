import mysql.connector

dataBase = mysql.connector.connect(
    host= 'localhost',
    user = 'root',
    passwd = 'kritan69420'
) 

cursorObject =dataBase.cursor() 

cursorObject.execute("CREATE DATABASE miDatabase")