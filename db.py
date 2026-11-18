import sqlite3

def conectar_db():
    conn = sqlite3.connect("juego.db")
    return conn

def crear_tabla():

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS retos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()