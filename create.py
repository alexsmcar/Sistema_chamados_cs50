import sqlite3

connection = sqlite3.connect("sistema_chamados.db")
cursor = connection.cursor()
cursor.execute(''' CREATE TABLE clientes (
               id INTEGER PRIMARY KEY,
               nome TEXT NOT NULL,
               cpf_cnpj TEXT NOT NULL,
               telefone TEXT NOT NULL,
               logradouro TEXT NOT NULL,
               bairro TEXT NOT NULL,
               numero INTEGER,
               complemento TEXT,
               cidade TEXT NOT NULL,
               uf TEXT NOT NULL
               )''')
connection.close()