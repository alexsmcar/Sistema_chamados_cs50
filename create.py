import sqlite3

connection = sqlite3.connect("sistema_chamados.db")
if connection:
    print("ok")
cursor = connection.cursor()
connection.close()