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

# Buscar produto por ID
def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM products
        WHERE id = ?
    """, (product_id,))

    row = cursor.fetchone()
    conn.close()

    return row

# Atualizar produto (categoria)
def update_product(product_id, name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE products
    SET name = ?
    WHERE id = ?
    """, (name, product_id))

    conn.commit()
    conn.close()
    print("categoria atualizada com sucesso")

# Verificar se produto tem itens
def product_has_items(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM items
        WHERE product_id = ?
    """, (product_id,))

    count = cursor.fetchone()[0]
    conn.close()

    return count > 0

# Deletar produto (categoria) - só se não tiver itens
def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se tem itens
    cursor.execute("""
        SELECT COUNT(*) FROM items
        WHERE product_id = ?
    """, (product_id,))

    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        return False  # Não pode deletar

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()
    print("categoria deletada com sucesso")
    return True

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

# Buscar item por ID
def get_item_by_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, product_id, name, price, stock
        FROM items
        WHERE id = ?
    """, (item_id,))

    row = cursor.fetchone()
    conn.close()

    return row

# Atualizar item
def update_item(item_id, name, price=None, stock=None, product_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if product_id:
        cursor.execute("""
        UPDATE items
        SET name = ?, price = ?, stock = ?, product_id = ?
        WHERE id = ?
        """, (name, price, stock, product_id, item_id))
    else:
        cursor.execute("""
        UPDATE items
        SET name = ?, price = ?, stock = ?
        WHERE id = ?
        """, (name, price, stock, item_id))

    conn.commit()
    conn.close()
    print("item atualizado com sucesso")

# Deletar item
def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()
    print("item deletado com sucesso")

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

# -------- VENDEDORES --------

# Adiciona vendedor ao banco
def add_seller(name, phone=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO sellers (name, phone)
    VALUES (?, ?)
    """, (name, phone))

    conn.commit()
    conn.close()
    print("vendedor cadastrado com sucesso")

# Lista todos os vendedores
def get_all_sellers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone
        FROM sellers
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

# Buscar vendedor por ID
def get_seller_by_id(seller_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone
        FROM sellers
        WHERE id = ?
    """, (seller_id,))

    row = cursor.fetchone()
    conn.close()

    return row

# Atualizar vendedor
def update_seller(seller_id, name, phone=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE sellers
    SET name = ?, phone = ?
    WHERE id = ?
    """, (name, phone, seller_id))

    conn.commit()
    conn.close()
    print("vendedor atualizado com sucesso")

# Deletar vendedor
def delete_seller(seller_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sellers WHERE id = ?", (seller_id,))

    conn.commit()
    conn.close()
    print("vendedor deletado com sucesso")

# Buscar vendedores por texto
def search_sellers(text=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone
        FROM sellers
        WHERE name LIKE ?
        ORDER BY name
    """, (f"%{text}%",))

    rows = cursor.fetchall()
    conn.close()

    return rows

# Retorna produtos agrupados com seus itens
def get_products_grouped():
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
        ORDER BY p.id, i.id
    """)

    rows = cursor.fetchall()
    conn.close()

    # Agrupar por categoria
    grouped = {}
    for row in rows:
        product_id = row[0]
        product_name = row[1]
        
        if product_id not in grouped:
            grouped[product_id] = {
                'name': product_name,
                'items': []
            }
        
        if row[2] is not None:  # Se há um item
            grouped[product_id]['items'].append({
                'id': row[2],
                'name': row[3],
                'price': row[4],
                'stock': row[5]
            })
    
    return grouped

# Buscar produtos agrupados com filtro
def search_products_grouped(text=""):
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
        WHERE p.name LIKE ? OR i.name LIKE ?
        ORDER BY p.id, i.id
    """, (f"%{text}%", f"%{text}%"))

    rows = cursor.fetchall()
    conn.close()

    # Agrupar por categoria
    grouped = {}
    for row in rows:
        product_id = row[0]
        product_name = row[1]
        
        if product_id not in grouped:
            grouped[product_id] = {
                'name': product_name,
                'items': []
            }
        
        if row[2] is not None:  # Se há um item
            grouped[product_id]['items'].append({
                'id': row[2],
                'name': row[3],
                'price': row[4],
                'stock': row[5]
            })
    
    return grouped
