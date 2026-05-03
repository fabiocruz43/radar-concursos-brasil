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
            plano_ativo INTEGER DEFAULT 0
        )
    """)

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
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        """, (nome, email, senha_hash))

        conn.commit()
        return True, "Usuário cadastrado!"

    except sqlite3.IntegrityError:
        return False, "E-mail já existe."

    finally:
        conn.close()


def verificar_login(email, senha):
    conn = conectar()
    cursor = conn.cursor()

    senha_hash = gerar_hash(senha)

    cursor.execute("""
        SELECT id, nome, email, plano_ativo
        FROM usuarios
        WHERE email = ? AND senha = ?
    """, (email, senha_hash))

    usuario = cursor.fetchone()
    conn.close()

    return usuario