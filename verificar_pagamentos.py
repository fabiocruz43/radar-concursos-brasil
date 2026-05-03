import sqlite3
import mercadopago
import streamlit as st

ACCESS_TOKEN = st.secrets["MP_ACCESS_TOKEN"]

sdk = mercadopago.SDK(ACCESS_TOKEN)

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

cursor.execute("SELECT email, preference_id FROM pagamentos WHERE status = 'pendente'")
pagamentos = cursor.fetchall()

for email, preference_id in pagamentos:
    resultado = sdk.payment().search({
        "external_reference": email
    })

    pagamentos_mp = resultado["response"]["results"]

    for p in pagamentos_mp:
        if p["status"] == "approved":
            print(f"Pagamento aprovado para {email}")

            cursor.execute("UPDATE usuarios SET plano_ativo = 1 WHERE email = ?", (email,))
            cursor.execute("UPDATE pagamentos SET status = 'aprovado' WHERE email = ?", (email,))

conn.commit()
conn.close()

print("Verificação finalizada")