import smtplib
import json
import os
from email.mime.text import MIMEText

from database import (
    criar_tabela_usuarios,
    criar_tabela_pagamentos,
    atualizar_banco,
    listar_usuarios_com_alerta
)

from services.bancas import BANCAS
from services.buscador import buscar_concursos


EMAIL_ORIGEM = "fabiosantos720@gmail.com"
EMAIL_SENHA = "SUA_SENHA_DE_APP"
ARQUIVO_VISTOS = "vistos.json"


def carregar_vistos():
    if not os.path.exists(ARQUIVO_VISTOS):
        return {}

    with open(ARQUIVO_VISTOS, "r", encoding="utf-8") as arquivo:
        try:
            return json.load(arquivo)
        except json.JSONDecodeError:
            return {}


def salvar_vistos(vistos):
    with open(ARQUIVO_VISTOS, "w", encoding="utf-8") as arquivo:
        json.dump(vistos, arquivo, ensure_ascii=False, indent=2)


def enviar_email(destino, assunto, corpo):
    mensagem = MIMEText(corpo, "plain", "utf-8")
    mensagem["Subject"] = assunto
    mensagem["From"] = EMAIL_ORIGEM
    mensagem["To"] = destino

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(EMAIL_ORIGEM, EMAIL_SENHA)
        servidor.sendmail(EMAIL_ORIGEM, destino, mensagem.as_string())


def chave_resultado(item):
    return f"{item['banca']}|{item['titulo']}|{item['link']}"


def main():
    criar_tabela_usuarios()
    criar_tabela_pagamentos()
    atualizar_banco()

    print("🚨 Iniciando alerta automático...")

    usuarios = listar_usuarios_com_alerta()

    if not usuarios:
        print("Nenhum usuário com alerta configurado.")
        return

    vistos = carregar_vistos()

    for nome, email, estado, cargo in usuarios:
        print(f"🔎 Buscando para {email} | {estado} | {cargo}")

        resultados = buscar_concursos(
            bancas_escolhidas=list(BANCAS.keys()),
            estado=estado,
            cargo=cargo,
            palavra_extra=""
        )

        novos = []

        if email not in vistos:
            vistos[email] = []

        for item in resultados:
            chave = chave_resultado(item)

            if chave not in vistos[email]:
                novos.append(item)
                vistos[email].append(chave)

        if novos:
            corpo = f"Olá, {nome}!\n\n"
            corpo += "Encontramos novos concursos com base nas suas preferências:\n\n"
            corpo += f"Estado: {estado}\n"
            corpo += f"Cargo/área: {cargo}\n\n"

            for item in novos[:20]:
                corpo += f"📌 {item['titulo']}\n"
                corpo += f"Banca: {item['banca']}\n"
                corpo += f"Link: {item['link']}\n\n"

            enviar_email(
                email,
                "🚨 Novos concursos encontrados para você",
                corpo
            )

            print(f"📧 E-mail enviado para {email} com {len(novos)} resultado(s).")
        else:
            print(f"✔️ Nenhuma novidade para {email}.")

    salvar_vistos(vistos)
    print("✅ Alerta automático finalizado.")


if __name__ == "__main__":
    main()