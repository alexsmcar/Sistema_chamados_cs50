import sqlite3

connection = sqlite3.connect("sistema_chamados.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id = 1")
nomes = cursor.fetchall()
for nome in nomes:
    print(nome["id"], nome["nome"])
connection.close()