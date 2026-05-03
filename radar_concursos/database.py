import sqlite3

DB_NAME = "radar_concursos.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            estado TEXT,
            cidade TEXT,
            distancia INTEGER,
            cargo TEXT,
            escolaridade TEXT,
            salario REAL
        )
    """)

    conn.commit()
    conn.close()


def salvar_preferencia(nome, email, estado, cidade, distancia, cargo, escolaridade, salario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO preferencias (
            nome, email, estado, cidade, distancia, cargo, escolaridade, salario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, estado, cidade, distancia, cargo, escolaridade, salario))

    conn.commit()
    conn.close()


def listar_preferencias():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, estado, cidade, distancia, cargo, escolaridade, salario
        FROM preferencias
        ORDER BY id DESC
    """)

    dados = cursor.fetchall()

    conn.close()
    return dados