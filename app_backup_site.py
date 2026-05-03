
import streamlit as st

from database import (
    criar_tabela_usuarios,
    criar_tabela_pagamentos,
    atualizar_banco,
    cadastrar_usuario,
    verificar_login,
    salvar_preferencias,
    obter_preferencias
)

from services.bancas import BANCAS
from services.buscador import buscar_concursos
from services.pagamento import criar_pagamento


st.set_page_config(
    page_title="Radar Concursos Brasil",
    page_icon="🚨",
    layout="wide"
)

criar_tabela_usuarios()
criar_tabela_pagamentos()
atualizar_banco()


ESTADOS = [
    "", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]


def tela_login():
    st.title("🔐 Radar Concursos Brasil")
    st.write("Acesse sua conta para usar o sistema.")

    aba_login, aba_cadastro = st.tabs(["Entrar", "Cadastrar"])

    with aba_login:
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        if st.button("Entrar"):
            usuario = verificar_login(email, senha)

            if usuario:
                st.session_state["usuario"] = usuario
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")

    with aba_cadastro:
        nome = st.text_input("Nome completo")
        email_cadastro = st.text_input("E-mail", key="cadastro_email")
        senha_cadastro = st.text_input("Senha", type="password", key="cadastro_senha")

        if st.button("Cadastrar"):
            if not nome or not email_cadastro or not senha_cadastro:
                st.warning("Preencha todos os campos.")
            else:
                sucesso, mensagem = cadastrar_usuario(nome, email_cadastro, senha_cadastro)

                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)


def tela_pagamento(usuario):
    st.title("💳 Ative seu acesso")
    st.warning("Seu plano ainda não está ativo.")
    st.write("Para usar o Radar Concursos Brasil, ative seu plano.")

    st.markdown("### Plano Mensal")
    st.write("✅ Busca nacional de concursos")
    st.write("✅ Filtros por banca, estado e cargo")
    st.write("✅ Alertas por e-mail")
    st.write("✅ Acesso completo ao sistema")
    st.write("💰 Valor: R$ 19,90")

    if st.button("💳 Pagar agora"):
        try:
            link_pagamento = criar_pagamento(usuario[2])
            st.success("Link de pagamento criado.")
            st.markdown(f"[🔗 Clique aqui para pagar]({link_pagamento})")
        except Exception as erro:
            st.error("Erro ao criar pagamento.")
            st.code(str(erro))


def atualizar_usuario_sessao(email, senha=""):
    """
    Se precisar atualizar a sessão depois de salvar preferência,
    buscamos os dados direto do banco usando a senha apenas no login normal.
    Aqui vamos apenas manter a sessão atual e recarregar ao novo login.
    """
    pass


def tela_principal():
    usuario = st.session_state["usuario"]

    nome_usuario = usuario[1]
    email_usuario = usuario[2]
    plano_ativo = usuario[3]

    if plano_ativo == 0:
        tela_pagamento(usuario)
        return

    st.sidebar.title("📌 Menu")

    pagina = st.sidebar.radio(
        "Escolha uma opção",
        [
            "Painel inicial",
            "Buscar concursos",
            "Minhas preferências",
            "Alertas por e-mail",
            "Plano / pagamento",
            "Sair"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {nome_usuario}")
    st.sidebar.write(f"📧 {email_usuario}")

    if pagina == "Painel inicial":
        st.title("🚨 Radar Concursos Brasil")
        st.success("Sistema ativo.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Bancas monitoradas", len(BANCAS))

        with col2:
            st.metric("Cobertura", "Brasil")

        with col3:
            st.metric("Alertas", "E-mail")

        st.markdown("---")
        st.subheader("Resumo")
        st.write("Use o menu lateral para buscar concursos, salvar preferências e configurar alertas.")

        preferencias = obter_preferencias(email_usuario)

        if preferencias:
            estado_pref, cargo_pref = preferencias

            st.info(
                f"Preferências atuais: Estado: **{estado_pref or 'não definido'}** | "
                f"Cargo: **{cargo_pref or 'não definido'}**"
            )

    elif pagina == "Buscar concursos":
        st.title("🔎 Buscar concursos no Brasil")

        preferencias = obter_preferencias(email_usuario)
        estado_salvo = ""
        cargo_salvo = "administrativo"

        if preferencias:
            estado_salvo = preferencias[0] or ""
            cargo_salvo = preferencias[1] or "administrativo"

        index_estado = ESTADOS.index(estado_salvo) if estado_salvo in ESTADOS else 26

        with st.sidebar:
            st.markdown("---")
            st.subheader("Filtros da busca")

            bancas_escolhidas = st.multiselect(
                "Bancas",
                list(BANCAS.keys()),
                default=["VUNESP", "IBAM", "FGV", "FCC", "Cebraspe"]
            )

            estado = st.selectbox("Estado", ESTADOS, index=index_estado)

            cargo = st.text_input("Cargo ou área", cargo_salvo)
            palavra_extra = st.text_input("Palavra extra", "")
            limite = st.slider("Limite de resultados", 10, 200, 50)

        if st.button("🔍 Verificar agora"):
            with st.spinner("Buscando nas bancas selecionadas..."):
                resultados = buscar_concursos(
                    bancas_escolhidas=bancas_escolhidas,
                    estado=estado,
                    cargo=cargo,
                    palavra_extra=palavra_extra
                )

            if resultados:
                st.success(f"{len(resultados)} resultado(s) encontrado(s).")

                for item in resultados[:limite]:
                    st.markdown("---")
                    st.subheader(item["titulo"])
                    st.write(f"**Banca:** {item['banca']}")
                    st.markdown(f"[🔗 Acessar página oficial]({item['link']})")
            else:
                st.warning("Nenhum concurso encontrado com esses filtros.")

    elif pagina == "Minhas preferências":
        st.title("⚙️ Minhas preferências")
        st.write("Salve aqui os filtros principais para o sistema usar nos alertas automáticos.")

        preferencias = obter_preferencias(email_usuario)

        estado_atual = ""
        cargo_atual = ""

        if preferencias:
            estado_atual = preferencias[0] or ""
            cargo_atual = preferencias[1] or ""

        index_estado = ESTADOS.index(estado_atual) if estado_atual in ESTADOS else 0

        novo_estado = st.selectbox("Estado de interesse", ESTADOS, index=index_estado)
        novo_cargo = st.text_input("Cargo ou área de interesse", cargo_atual or "administrativo")

        if st.button("💾 Salvar preferências"):
            salvar_preferencias(email_usuario, novo_estado, novo_cargo)
            st.success("Preferências salvas com sucesso.")
            st.info("Para atualizar totalmente os dados da sessão, saia e entre novamente.")

    elif pagina == "Alertas por e-mail":
        st.title("📧 Alertas por e-mail")

        preferencias = obter_preferencias(email_usuario)

        if preferencias:
            estado_pref, cargo_pref = preferencias
        else:
            estado_pref, cargo_pref = "", ""

        st.write("Seus alertas serão enviados com base nestas preferências:")

        st.markdown(f"- **E-mail:** {email_usuario}")
        st.markdown(f"- **Estado:** {estado_pref or 'não definido'}")
        st.markdown(f"- **Cargo/área:** {cargo_pref or 'não definido'}")

        if not estado_pref or not cargo_pref:
            st.warning("Configure suas preferências antes de ativar alertas.")
        else:
            st.success("Preferências configuradas.")
            st.info("Próximo passo: conectar estas preferências ao envio automático do main.py.")

    elif pagina == "Plano / pagamento":
        st.title("💳 Plano / pagamento")
        st.success("Seu plano está ativo.")
        st.write("Plano atual: **Mensal**")
        st.write("Valor: **R$ 19,90**")
        st.info("Em breve: histórico de pagamentos, renovação e cancelamento.")

    elif pagina == "Sair":
        st.session_state.clear()
        st.rerun()


if "usuario" not in st.session_state:
    tela_login()
else:
    tela_principal()