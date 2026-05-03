import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.title("🚨 Radar de Concursos")

FONTES = {
    "VUNESP": "https://www.vunesp.com.br/busca/concurso/inscricoes%20abertas",
    "IBAM-SP": "https://www.ibamsp-concursos.org.br/",
    "Avança SP": "https://avancasp.selecao.net.br/index/abertos/",
    "Instituto Mais": "https://www.institutomais.org.br/Concursos",
    "RBO": "https://www.rboconcursos.com.br/",
    "Instituto Consulplan": "https://www.institutoconsulplan.org.br/Concursos.aspx",
    "FGV": "https://conhecimento.fgv.br/concursos",
    "Fundatec": "https://fundatec.org.br/portal/concursos/",
}

REGIOES = {
    "Grande São Paulo": [
        "são paulo", "osasco", "guarulhos", "santo andré", "são bernardo",
        "são caetano", "mauá", "diadema", "barueri", "carapicuíba",
        "itapevi", "taboão", "embu", "franco da rocha", "francisco morato"
    ],
    "ABC Paulista": [
        "santo andré", "são bernardo", "são caetano", "mauá", "diadema",
        "ribeirão pires", "rio grande da serra"
    ],
    "Interior próximo": [
        "sorocaba", "jundiaí", "campinas", "itu", "boituva", "indaiatuba",
        "vinhedo", "valinhos", "americana", "sumaré"
    ],
    "Litoral": [
        "santos", "são vicente", "praia grande", "guarujá", "cubatão"
    ],
    "Todo o estado de SP": ["sp", "são paulo"],
}

CARGOS = [
    "administrativo",
    "analista",
    "assistente",
    "agente",
    "técnico",
    "edificações",
    "engenharia",
    "recursos humanos",
    "fiscal",
    "auxiliar",
]

with st.sidebar:
    st.header("🔎 Filtros")

    bancas_escolhidas = st.multiselect(
        "Bancas",
        list(FONTES.keys()),
        default=["VUNESP", "IBAM-SP", "Avança SP"]
    )

    regiao = st.selectbox(
        "Região",
        list(REGIOES.keys())
    )

    cargos_escolhidos = st.multiselect(
        "Área/cargo",
        CARGOS,
        default=["administrativo", "analista", "assistente", "técnico"]
    )

    palavra_extra = st.text_input("Palavra extra", "")

    limite = st.slider("Máximo de resultados", 10, 100, 50)


def texto_interessa(texto, cidades, cargos, palavra_extra):
    texto = texto.lower()

    tem_local = any(cidade in texto for cidade in cidades)
    tem_cargo = any(cargo in texto for cargo in cargos)

    if palavra_extra.strip():
        tem_extra = palavra_extra.lower().strip() in texto
    else:
        tem_extra = True

    return tem_local and tem_cargo and tem_extra


def buscar_concursos():
    resultados = []

    cidades = REGIOES[regiao]

    for banca in bancas_escolhidas:
        url = FONTES[banca]

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

                if not titulo or not href:
                    continue

                texto_completo = f"{titulo} {href}"

                if texto_interessa(texto_completo, cidades, cargos_escolhidos, palavra_extra):
                    resultados.append({
                        "banca": banca,
                        "titulo": titulo,
                        "link": urljoin(url, href)
                    })

        except Exception as erro:
            resultados.append({
                "banca": banca,
                "titulo": f"Erro ao consultar {banca}: {erro}",
                "link": url
            })

    return resultados


st.subheader("📌 Buscar concursos abertos")

if st.button("🔍 Verificar agora"):
    with st.spinner("Buscando concursos nas bancas selecionadas..."):
        dados = buscar_concursos()

    if dados:
        st.success(f"{len(dados)} resultado(s) encontrado(s).")

        for item in dados[:limite]:
            st.markdown("---")
            st.markdown(f"### {item['titulo']}")
            st.write(f"**Banca:** {item['banca']}")
            st.markdown(f"[🔗 Acessar página oficial]({item['link']})")
    else:
        st.warning("Nenhum concurso encontrado com esses filtros.")

st.info("Use o menu lateral para escolher região, banca e tipo de cargo.")