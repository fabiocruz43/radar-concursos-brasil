import sqlite3

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE usuarios
SET plano_ativo = 1
WHERE email = 'fabiosantos720@gmail.com'
""")

conn.commit()
conn.close()

print("✅ Plano liberado com sucesso!")