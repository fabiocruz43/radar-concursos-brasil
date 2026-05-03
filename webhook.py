from flask import Flask, request
import mercadopago
import sqlite3

ACCESS_TOKEN = "APP_USR-8912645578248744-050201-d40174ff1bffd2cb5b8572f3be3811cf-165208380"

app = Flask(__name__)

sdk = mercadopago.SDK(ACCESS_TOKEN)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "data" in data and "id" in data["data"]:
        payment_id = data["data"]["id"]

        pagamento = sdk.payment().get(payment_id)
        status = pagamento["response"]["status"]

        if status == "approved":
            email = pagamento["response"]["external_reference"]

            conn = sqlite3.connect("usuarios.db")
            cursor = conn.cursor()

            cursor.execute("UPDATE usuarios SET plano_ativo = 1 WHERE email = ?", (email,))
            conn.commit()
            conn.close()

            return "OK", 200

    return "IGNORADO", 200


if __name__ == "__main__":
    app.run(port=5000)