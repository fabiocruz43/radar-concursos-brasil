import sqlite3
import mercadopago

ACCESS_TOKEN = "SEU_ACCESS_TOKEN"

sdk = mercadopago.SDK(ACCESS_TOKEN)

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

cursor.execute("SELECT email FROM pagamentos WHERE status = 'pendente'")
pagamentos = cursor.fetchall()

for pagamento in pagamentos:
    email = pagamento[0]

    # Aqui depois vamos consultar pagamento real
    # Por enquanto libera direto para teste

    cursor.execute("""
        UPDATE usuarios
        SET plano_ativo = 1
        WHERE email = ?
    """, (email,))

    cursor.execute("""
        UPDATE pagamentos
        SET status = 'aprovado'
        WHERE email = ?
    """, (email,))

conn.commit()
conn.close()

print("✔️ Verificação concluída")