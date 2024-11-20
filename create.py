import sqlite3

connection = sqlite3.connect("sistema_chamados.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute('''SELECT 
  COUNT(status),
  COUNT(CASE WHEN status = 'aberto' THEN 1 END) AS aberto,
  COUNT(CASE WHEN status = 'finalizado' THEN 1 END) AS finalizado
FROM chamados
GROUP BY status'''
)
nomes = cursor.fetchall()
print(nomes)