import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Nome do banco
DB_PATH = os.path.join(BASE_DIR, "products.db")


def get_connection():
    return sqlite3.connect(DB_PATH)

#cria o banco de dados
def init_db():
    from database.models import create_tables

    conn = get_connection()
    cursor = conn.cursor()

    create_tables(cursor)

    conn.commit()
    conn.close()

#adiciona produtos ao banco de dados
def add_product (name):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""

    INSERT INTO products (name)
    VALUES (?)
   """, (name,))

    conn.commit()
    conn.close()
    print ("produto cadastrado com sucesso")

#adiciona itens derivados de determinado produto
def add_item(product_id, name, price=None, stock=None):
    conn = get_connection()
    cursor = conn.cursor ()

    cursor.execute("""
    INSERT INTO items(product_id, name, price, stock)
    VALUES (?, ?, ?, ?)
    """, (product_id, name, price, stock))

    conn.commit()
    conn.close()
    print("item cadastrado com sucesso")

# Listar todos os produtos (não tem filtro)
def get_products_with_items():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.id,
            p.name AS product_name,
            i.id AS item_id,
            i.name AS item_name,
            i.price,
            i.stock
        FROM products p
        LEFT JOIN items i ON p.id = i.product_id
        ORDER BY p.id
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

# buscar produtos no banco (tem filtro)
def search_products(text=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.id,
            p.name,
            i.id,
            i.name,
            i.price,
            i.stock
        FROM products p
        LEFT JOIN items i ON p.id = i.product_id
        WHERE p.name LIKE ?
        ORDER BY p.id
    """, (f"%{text}%",))

    rows = cursor.fetchall()
    conn.close()

    return rows
