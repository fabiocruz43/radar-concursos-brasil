import streamlit as st
from database import criar_tabelas, salvar_preferencia, listar_preferencias
from scraper import buscar_concursos

criar_tabelas()

st.set_page_config(
    page_title="Radar Concursos",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Radar Concursos")
st.subheader("Sistema inteligente de alerta de concursos públicos")

st.markdown("""
Cadastre suas preferências e o sistema encontrará concursos automaticamente.
""")

st.divider()

# FORMULÁRIO
st.header("Cadastro de Preferências")

with st.form("form"):
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    estado = st.selectbox("Estado", ["SP", "RJ", "MG", "BA", "PR"])
    cidade = st.text_input("Cidade base")
    distancia = st.number_input("Distância máxima (km)", min_value=0, value=100)
    cargo = st.text_input("Cargo de interesse")
    escolaridade = st.selectbox("Escolaridade", ["Fundamental", "Médio", "Superior"])
    salario = st.number_input("Salário mínimo", min_value=0.0, value=3000.0)

    salvar = st.form_submit_button("Salvar")

if salvar:
    salvar_preferencia(nome, email, estado, cidade, distancia, cargo, escolaridade, salario)
    st.success("Salvo no banco!")

# LISTAR DADOS
st.divider()
st.header("Preferências cadastradas")

dados = listar_preferencias()

for d in dados:
    st.write(d)

# BUSCAR CONCURSOS
st.divider()
st.header("Buscar concursos")

if st.button("Buscar agora"):
    resultados = buscar_concursos()

    for r in resultados:
        st.write(r)