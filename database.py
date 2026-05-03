import sqlite3
import hashlib

DB_NAME = "usuarios.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabela_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            plano_ativo INTEGER DEFAULT 0,
            estado TEXT DEFAULT '',
            cargo TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


def criar_tabela_pagamentos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            preference_id TEXT,
            status TEXT DEFAULT 'pendente',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def atualizar_banco():
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN estado TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN cargo TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def gerar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def cadastrar_usuario(nome, email, senha):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = gerar_hash(senha)

    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, plano_ativo, estado, cargo)
            VALUES (?, ?, ?, 0, '', '')
        """, (nome, email, senha_hash))

        conn.commit()
        return True, "Usuário cadastrado com sucesso."

    except sqlite3.IntegrityError:
        return False, "Este e-mail já está cadastrado."

    finally:
        conn.close()


def verificar_login(email, senha):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = gerar_hash(senha)

    cursor.execute("""
        SELECT id, nome, email, plano_ativo, estado, cargo
        FROM usuarios
        WHERE email = ? AND senha = ?
    """, (email, senha_hash))

    usuario = cursor.fetchone()
    conn.close()
    return usuario


def salvar_preferencias(email, estado, cargo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET estado = ?, cargo = ?
        WHERE email = ?
    """, (estado, cargo, email))

    conn.commit()
    conn.close()


def obter_preferencias(email):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT estado, cargo
        FROM usuarios
        WHERE email = ?
    """, (email,))

    dados = cursor.fetchone()
    conn.close()
    return dados


def listar_usuarios_com_alerta():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, email, estado, cargo
        FROM usuarios
        WHERE plano_ativo = 1
        AND estado IS NOT NULL
        AND estado != ''
        AND cargo IS NOT NULL
        AND cargo != ''
    """)

    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


def registrar_pagamento(email, preference_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pagamentos (email, preference_id, status)
        VALUES (?, ?, 'pendente')
    """, (email, preference_id))

    conn.commit()
    conn.close()


def ativar_plano(email):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET plano_ativo = 1
        WHERE email = ?
    """, (email,))

    conn.commit()
    conn.close()