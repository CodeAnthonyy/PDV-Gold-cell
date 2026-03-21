def create_tables(cursor):

    # Tabela de categorias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabela de itens variações/especificar produto (ex: produto= iphone 17, item = capa 17  pro max, pelicula 17 pro max)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        price REAL,
        stock INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (product_id) REFERENCES categorias(id)
    )
    """)

    # Tabela de vendedores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        cargo TEXT NOT NULL DEFAULT 'usuario',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabela de cabeÃ§alho de vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id      INTEGER NOT NULL,
        seller_name    TEXT    NOT NULL,
        subtotal       REAL    NOT NULL,
        desconto       REAL    NOT NULL DEFAULT 0,
        desconto_tipo  TEXT    NOT NULL DEFAULT 'R$',
        total          REAL    NOT NULL,
        status         TEXT    NOT NULL DEFAULT 'concluida',
        created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at     DATETIME
    )
    """)

    # Itens de cada venda
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venda_itens (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id     INTEGER NOT NULL REFERENCES vendas(id),
        item_id      INTEGER NOT NULL,
        item_name    TEXT    NOT NULL,
        quantidade   INTEGER NOT NULL,
        preco_unit   REAL    NOT NULL,
        subtotal     REAL    NOT NULL
    )
    """)

    # Pagamentos de cada venda (mÃºltiplos mÃ©todos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venda_pagamentos (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER NOT NULL REFERENCES vendas(id),
        metodo   TEXT    NOT NULL,
        valor    REAL    NOT NULL
    )
    """)
