import sqlite3
import os
import bcrypt
import json
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Nome do banco
DB_PATH = os.path.join(BASE_DIR, "products.db")

# Arquivo de credenciais
CREDENTIALS_FILE = os.path.join(os.path.dirname(BASE_DIR), "credentials.json")

def _ensure_db_exists():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_connection():
    _ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

#cria o banco de dados
def init_db():
    from database.models import create_tables

    conn = get_connection()
    cursor = conn.cursor()

    create_tables(cursor)
    _ensure_vendas_columns(cursor)

    conn.commit()
    conn.close()


def _ensure_vendas_columns(cursor):
    cursor.execute("PRAGMA table_info(vendas)")
    cols = {row["name"] for row in cursor.fetchall()}

    if "desconto" not in cols:
        cursor.execute(
            "ALTER TABLE vendas ADD COLUMN desconto REAL NOT NULL DEFAULT 0"
        )

    if "desconto_tipo" not in cols:
        cursor.execute(
            "ALTER TABLE vendas ADD COLUMN desconto_tipo TEXT NOT NULL DEFAULT 'R$'"
        )

#adiciona categorias ao banco de dados
def add_product (name):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""

    INSERT INTO categorias (name)
    VALUES (?)
   """, (name,))

    conn.commit()
    conn.close()
    print ("categoria cadastrada com sucesso")

# Buscar categoria por ID
def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM categorias
        WHERE id = ?
    """, (product_id,))

    row = cursor.fetchone()
    conn.close()

    return row

# Atualizar categoria
def update_product(product_id, name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE categorias
    SET name = ?
    WHERE id = ?
    """, (name, product_id))

    conn.commit()
    conn.close()
    print("categoria atualizada com sucesso")

# Deletar categoria - só se não tiver itens
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

    cursor.execute("DELETE FROM categorias WHERE id = ?", (product_id,))

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

# Listar apenas as categorias (sem duplicatas)
def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM categorias
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

# Listar todas as categorias com itens (não tem filtro)
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
        FROM categorias p
        LEFT JOIN items i ON p.id = i.product_id
        ORDER BY p.id
    """)

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

# -------- VENDAS / RELATORIOS --------

def _build_vendas_filters(data_inicio=None, data_fim=None, metodo=None, somente_concluidas=False):
    where = []
    params = []

    if somente_concluidas:
        where.append("v.status != 'cancelada'")

    if data_inicio and data_fim:
        where.append("date(v.created_at) BETWEEN ? AND ?")
        params.extend([data_inicio, data_fim])
    elif data_inicio:
        where.append("date(v.created_at) >= ?")
        params.append(data_inicio)
    elif data_fim:
        where.append("date(v.created_at) <= ?")
        params.append(data_fim)

    if metodo:
        where.append("""
            EXISTS (
                SELECT 1
                FROM venda_pagamentos vp
                WHERE vp.venda_id = v.id AND vp.metodo = ?
            )
        """)
        params.append(metodo)

    if not where:
        return "1=1", params

    return " AND ".join(where), params


def add_venda(payload):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO vendas (
                seller_id, seller_name, subtotal, desconto, desconto_tipo, total, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'concluida', ?)
        """, (
            payload.get("seller_id"),
            payload.get("seller_name"),
            payload.get("subtotal"),
            payload.get("desconto", 0),
            payload.get("desconto_tipo", "R$"),
            payload.get("total"),
            created_at
        ))

        venda_id = cursor.lastrowid

        for item in payload.get("itens", []):
            cursor.execute("""
                INSERT INTO venda_itens (
                    venda_id, item_id, item_name, quantidade, preco_unit, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                venda_id,
                item.get("item_id"),
                item.get("item_name"),
                item.get("quantidade"),
                item.get("preco_unit"),
                item.get("subtotal")
            ))

            # Atualiza estoque sem permitir negativo (estoque pode ser nulo)
            cursor.execute("""
                UPDATE items
                SET stock = MAX(COALESCE(stock, 0) - ?, 0)
                WHERE id = ?
            """, (
                item.get("quantidade") or 0,
                item.get("item_id")
            ))

        for pag in payload.get("pagamentos", []):
            cursor.execute("""
                INSERT INTO venda_pagamentos (venda_id, metodo, valor)
                VALUES (?, ?, ?)
            """, (
                venda_id,
                pag.get("metodo"),
                pag.get("valor")
            ))

        conn.commit()
        return venda_id
    finally:
        conn.close()


def get_vendas(data_inicio=None, data_fim=None, metodo=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_sql, params = _build_vendas_filters(data_inicio, data_fim, metodo)

    cursor.execute(f"""
        SELECT
            v.id,
            v.created_at,
            v.seller_name,
            v.total,
            v.status,
            (
                SELECT COALESCE(SUM(quantidade), 0)
                FROM venda_itens vi
                WHERE vi.venda_id = v.id
            ) AS total_itens,
            (
                SELECT COALESCE(GROUP_CONCAT(DISTINCT metodo), '')
                FROM venda_pagamentos vp2
                WHERE vp2.venda_id = v.id
            ) AS metodos
        FROM vendas v
        WHERE {where_sql}
        ORDER BY v.created_at DESC
    """, params)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_venda_by_id(venda_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, seller_id, seller_name, subtotal, desconto,
               desconto_tipo, total, status, created_at
        FROM vendas
        WHERE id = ?
    """, (venda_id,))

    venda = cursor.fetchone()
    if not venda:
        conn.close()
        return None

    cursor.execute("""
        SELECT item_id, item_name, quantidade, preco_unit, subtotal
        FROM venda_itens
        WHERE venda_id = ?
    """, (venda_id,))
    itens = cursor.fetchall()

    cursor.execute("""
        SELECT metodo, valor
        FROM venda_pagamentos
        WHERE venda_id = ?
    """, (venda_id,))
    pagamentos = cursor.fetchall()

    conn.close()

    resultado = dict(venda)
    resultado["itens"] = [dict(row) for row in itens]
    resultado["pagamentos"] = [dict(row) for row in pagamentos]

    return resultado


def cancelar_venda(venda_id):
    conn = get_connection()
    cursor = conn.cursor()

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE vendas
        SET status = 'cancelada', updated_at = ?
        WHERE id = ?
    """, (updated_at, venda_id))

    conn.commit()
    conn.close()

    return True


def get_dashboard_resumo(data_inicio=None, data_fim=None, metodo=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_sql, params = _build_vendas_filters(
        data_inicio, data_fim, metodo, somente_concluidas=True
    )

    cursor.execute(f"""
        SELECT
            COALESCE(SUM(v.total), 0) AS faturamento,
            COUNT(*) AS qtd_vendas,
            COALESCE(MAX(v.total), 0) AS maior_venda
        FROM vendas v
        WHERE {where_sql}
    """, params)

    row = cursor.fetchone()
    conn.close()

    faturamento = row["faturamento"] or 0
    qtd_vendas = row["qtd_vendas"] or 0
    ticket_medio = (faturamento / qtd_vendas) if qtd_vendas else 0

    return {
        "faturamento": faturamento,
        "qtd_vendas": qtd_vendas,
        "ticket_medio": ticket_medio,
        "maior_venda": row["maior_venda"] or 0
    }


def get_dashboard_por_hora(data_inicio=None, data_fim=None, metodo=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_sql, params = _build_vendas_filters(
        data_inicio, data_fim, metodo, somente_concluidas=True
    )

    cursor.execute(f"""
        SELECT
            CAST(strftime('%H', v.created_at) AS INTEGER) AS hora,
            COUNT(*) AS qtd_vendas
        FROM vendas v
        WHERE {where_sql}
        GROUP BY hora
        ORDER BY hora
    """, params)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_dashboard_por_vendedor(data_inicio=None, data_fim=None, metodo=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_sql, params = _build_vendas_filters(
        data_inicio, data_fim, metodo, somente_concluidas=True
    )

    cursor.execute(f"""
        SELECT
            v.seller_name,
            COALESCE(SUM(v.total), 0) AS faturamento,
            COUNT(*) AS qtd_vendas,
            CASE WHEN COUNT(*) > 0 THEN (SUM(v.total) / COUNT(*)) ELSE 0 END AS ticket_medio
        FROM vendas v
        WHERE {where_sql}
        GROUP BY v.seller_id, v.seller_name
        ORDER BY faturamento DESC
    """, params)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

# Retorna categorias agrupadas com seus itens
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
        FROM categorias p
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


# -------- AUTENTICAÇÃO --------

def hash_password(senha):
    """Criptografa a senha com bcrypt"""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

def verify_password(senha, hash_senha):
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(senha.encode(), hash_senha)

def user_exists(usuario):
    """Verifica se o usuário já existe"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    
    return exists

def get_total_users():
    """Retorna o total de usuários cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]
    conn.close()
    
    return total

def register_user(usuario, senha):
    """Registra um novo usuário
    Primeiro usuário é admin, demais são usuarios"""
    
    if user_exists(usuario):
        return {"status": False, "message": "Usuário já existe!"}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Define cargo automaticamente
    total = get_total_users()
    cargo = "admin" if total == 0 else "usuario"
    
    # Criptografa a senha
    hash_senha = hash_password(senha)
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (usuario, senha, cargo)
            VALUES (?, ?, ?)
        """, (usuario, hash_senha, cargo))
        
        conn.commit()
        
        # Salva credencial em JSON
        save_credentials(usuario, cargo)
        
        conn.close()
        return {"status": True, "message": f"Usuário {cargo} criado com sucesso!", "cargo": cargo}
    
    except Exception as e:
        conn.close()
        return {"status": False, "message": f"Erro ao registrar: {str(e)}"}

def login_user(usuario, senha):
    """Autentica um usuário"""
    
    if not user_exists(usuario):
        return {"status": False, "message": "Usuário não encontrado!"}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, usuario, senha, cargo FROM usuarios WHERE usuario = ?", (usuario,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return {"status": False, "message": "Usuário não encontrado!"}
    
    user_id, user_name, hash_senha, cargo = row
    
    # Verifica a senha
    if verify_password(senha, hash_senha):
        return {
            "status": True,
            "message": "Login realizado com sucesso!",
            "id": user_id,
            "usuario": user_name,
            "cargo": cargo
        }
    else:
        return {"status": False, "message": "Senha incorreta!"}


def verify_admin_password(senha):
    """Verifica se a senha pertence a algum usuario admin"""
    if not senha:
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE cargo = 'admin'")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        hash_senha = row["senha"]
        try:
            if verify_password(senha, hash_senha):
                return True
        except Exception:
            continue

    return False

def save_credentials(usuario, cargo):
    """Salva as credenciais em um arquivo JSON"""
    
    credentials = {}
    
    # Se o arquivo já existe, carrega
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
        except:
            credentials = {}
    
    # Adiciona novo usuário
    if "usuarios" not in credentials:
        credentials["usuarios"] = []
    
    credentials["usuarios"].append({
        "usuario": usuario,
        "cargo": cargo,
        "criado_em": os.path.getmtime(CREDENTIALS_FILE) if os.path.exists(CREDENTIALS_FILE) else 0
    })
    
    # Salva o arquivo
    try:
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(credentials, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar credenciais: {str(e)}")

 
# Buscar categorias agrupadas com filtro
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
        FROM categorias p
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
