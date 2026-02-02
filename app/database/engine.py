import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Nome do banco
DB_PATH = os.path.join(BASE_DIR, "products.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    from database.models import create_tables

    conn = get_connection()
    cursor = conn.cursor()

    create_tables(cursor)

    conn.commit()
    conn.close()

    print("Banco 'products.db' iniciado com sucesso!")
