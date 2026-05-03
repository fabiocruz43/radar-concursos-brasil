import mercadopago
from database import registrar_pagamento, ativar_plano

ACCESS_TOKEN = "TEST-8912645578248744-050201-bd5db7405963e24101a943ea94a9118c-165208380"


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
            "success": "https://www.google.com",
            "failure": "https://www.google.com",
            "pending": "https://www.google.com"
        }
    }

    response = sdk.preference().create(preference_data)

    if response.get("status") not in [200, 201]:
        raise Exception(response)

    preference = response["response"]

    preference_id = preference["id"]
    link_pagamento = preference["init_point"]

    registrar_pagamento(email_usuario, preference_id)

    return link_pagamento


def verificar_pagamento_manual(email_usuario):
    ativar_plano(email_usuario)
    return True