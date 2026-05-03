import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from services.bancas import BANCAS


def buscar_concursos(bancas_escolhidas=None, estado="", cargo="", palavra_extra=""):
    resultados = []

    if not bancas_escolhidas:
        bancas_escolhidas = list(BANCAS.keys())

    for banca in bancas_escolhidas:
        url = BANCAS.get(banca)

        if not url:
            continue

        try:
            resposta = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            resposta.raise_for_status()

            soup = BeautifulSoup(resposta.text, "html.parser")
            links = soup.find_all("a")

            for link in links:
                titulo = link.get_text(" ", strip=True)
                href = link.get("href")

                if not titulo or not href or len(titulo) < 5:
                    continue

                texto = f"{titulo} {href}".lower()

                passou_estado = True
                passou_cargo = True
                passou_extra = True

                if estado:
                    passou_estado = estado.lower() in texto

                if cargo:
                    passou_cargo = cargo.lower() in texto

                if palavra_extra:
                    passou_extra = palavra_extra.lower() in texto

                if passou_estado and passou_cargo and passou_extra:
                    resultados.append({
                        "banca": banca,
                        "titulo": titulo,
                        "link": urljoin(url, href),
                    })

        except Exception as erro:
            resultados.append({
                "banca": banca,
                "titulo": f"Erro ao consultar {banca}: {erro}",
                "link": url,
            })

    return resultados