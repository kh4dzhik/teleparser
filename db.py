import sqlite3
import os


db_connection = sqlite3.connect("database.db") 
cursor = db_connection.cursor()


def execute_query(query):
    cursor.execute(query)
    db_connection.commit()