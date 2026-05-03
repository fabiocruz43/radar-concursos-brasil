import smtplib
import requests
import json
import os
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# CONFIG
EMAIL_ORIGEM = "fabiosantos720@gmail.com"
EMAIL_SENHA = "ceowkhvedxhqgcix"
EMAIL_DESTINO = "fabiosantos720@gmail.com"

ARQUIVO_VISTOS = "vistos.json"

FONTES = {
    "VUNESP": "https://www.vunesp.com.br/busca/concurso/inscricoes%20abertas",
    "IBAM-SP": "https://www.ibamsp-concursos.org.br/",
    "Avança SP": "https://avancasp.selecao.net.br/index/abertos/",
}


def carregar_vistos():
    if not os.path.exists(ARQUIVO_VISTOS):
        return []
    with open(ARQUIVO_VISTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_vistos(vistos):
    with open(ARQUIVO_VISTOS, "w", encoding="utf-8") as f:
        json.dump(vistos, f, indent=2, ensure_ascii=False)


def enviar_email(corpo):
    mensagem = MIMEText(corpo, "plain", "utf-8")
    mensagem["Subject"] = "🚨 Novo Concurso Encontrado"
    mensagem["From"] = EMAIL_ORIGEM
    mensagem["To"] = EMAIL_DESTINO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(EMAIL_ORIGEM, EMAIL_SENHA)
        servidor.sendmail(EMAIL_ORIGEM, EMAIL_DESTINO, mensagem.as_string())


def buscar():
    vistos = carregar_vistos()
    novos = []

    for nome, url in FONTES.items():
        print(f"🔎 Verificando {nome}...")

        try:
            r = requests.get(url, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            links = soup.find_all("a")

            for link in links:
                texto = link.get_text(strip=True)
                href = link.get("href")

                if texto and href:
                    chave = f"{nome}|{texto}"

                    if chave not in vistos:
                        novos.append(f"{nome}: {texto}\n{href}\n")
                        vistos.append(chave)

        except Exception as e:
            print(f"Erro em {nome}: {e}")

    if novos:
        corpo = "🚨 Novos concursos encontrados:\n\n"
        corpo += "\n".join(novos)

        enviar_email(corpo)
        salvar_vistos(vistos)

        print("📧 Novos concursos enviados por e-mail!")
    else:
        print("✔️ Nenhum concurso novo.")


if __name__ == "__main__":
    buscar()