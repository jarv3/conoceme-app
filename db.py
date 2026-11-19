import sqlite3


def conectar_db():
    return sqlite3.connect(
        "juego.db",
        check_same_thread=False
    )


def crear_tablas():

    conn = conectar_db()
    cursor = conn.cursor()

    # -----------------------
    # GRUPOS
    # -----------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT UNIQUE NOT NULL,
        creador TEXT NOT NULL
    )
    """)

    # -----------------------
    # PARTICIPANTES
    # -----------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grupo_id INTEGER,
        nombre TEXT
    )
    """)

    # -----------------------
    # RETOS
    # -----------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS retos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grupo_id INTEGER,
        creador TEXT,
        p1 TEXT,
        p2 TEXT,
        p3 TEXT,
        p4 TEXT,
        p5 TEXT,
        p6 TEXT,
        p7 TEXT,
        p8 TEXT,
        p9 TEXT,
        p10 TEXT
    )
    """)

    # -----------------------
    # RESULTADOS
    # -----------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resultados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reto_id INTEGER,
        jugador TEXT,
        porcentaje INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()