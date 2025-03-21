import sqlite3

conn = sqlite3.connect("etiquetas.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, nome TEXT, endereco TEXT, telefone TEXT, transportadora TEXT)''')
conn.commit()
conn.close()

print("Banco de dados configurado!")
