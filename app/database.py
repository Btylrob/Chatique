import mysql.connector
from dotenv import load_dotenv
import os



load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_DATABSE")


db = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database = database
)

cursor = db.cursor()

cursor.execute("show databases")
print(f"Connecting with host={host}, user={user}")
