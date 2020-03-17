import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="UVSE"
)

mycursor = mydb.cursor()

mycursor.execute(
    "CREATE TABLE captions (id INT AUTO_INCREMENT PRIMARY KEY, vid_name VARCHAR(255), img_name VARCHAR(255), caption VARCHAR(255))")
