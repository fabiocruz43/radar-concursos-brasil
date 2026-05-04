import os
import mercadopago

try:
    import streamlit as st
    ACCESS_TOKEN = st.secrets.get("MP_ACCESS_TOKEN", None)
except Exception:
    ACCESS_TOKEN = None

if not ACCESS_TOKEN:
    ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise ValueError("MP_ACCESS_TOKEN não encontrado.")


def criar_pagamento(email_usuario):
    sdk = mercadopago.SDK(ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": "Plano Mensal - Radar Concursos Brasil",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 19.90,
            }
        ],
        "payer": {
            "email": email_usuario
        },
        "external_reference": email_usuario,
        "back_urls": {
            "success": "https://radar-concursos-brasil-zhsq9856dbdk6juvuzggvc.streamlit.app",
            "failure": "https://radar-concursos-brasil-zhsq9856dbdk6juvuzggvc.streamlit.app",
            "pending": "https://radar-concursos-brasil-zhsq9856dbdk6juvuzggvc.streamlit.app",
        }
    }

    response = sdk.preference().create(preference_data)

    if response.get("status") not in [200, 201]:
        raise Exception(response)

    preference = response["response"]

    registrar_pagamento(email_usuario, preference["id"])

    return preference["init_point"]


def verificar_pagamento_usuario(email_usuario):
    sdk = mercadopago.SDK(ACCESS_TOKEN)

    resultado = sdk.payment().search({
        "external_reference": email_usuario
    })

    pagamentos = resultado["response"].get("results", [])

    for pagamento in pagamentos:
        if pagamento.get("status") == "approved":
            ativar_plano(email_usuario)
            return True

    return False
