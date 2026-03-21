from flask import render_template, request, redirect, flash, jsonify, session
from datetime import datetime

from database.engine import (
    get_products_with_items,
    search_products,
    add_product,
    add_item,
    add_seller,
    get_all_sellers,
    get_seller_by_id,
    update_seller,
    delete_seller,
    search_sellers,
    get_item_by_id,
    update_item,
    delete_item,
    get_products_grouped,
    search_products_grouped,
    get_product_by_id,
    update_product,
    delete_product,
    product_has_items,
    get_all_products,
    get_total_users,
    login_user,
    register_user,
    get_connection
)

from auth import autenticar_usuario, registrar_novo_usuario


def register_routes(app):
    """Registra todas as rotas na aplicação"""
    
    # -------- AUTENTICAÇÃO --------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            # API - JSON request
            if request.is_json:
                data = request.get_json()
                usuario = data.get("usuario")
                senha = data.get("senha")

                result = autenticar_usuario(usuario, senha)

                if result["status"]:
                    session['user_id'] = result.get('id')
                    session['usuario'] = result.get('usuario')
                    session['cargo'] = result.get('cargo')

                return jsonify(result)

            # Form request
            usuario = request.form.get("usuario")
            senha = request.form.get("senha")

            result = autenticar_usuario(usuario, senha)

            if result["status"]:
                session['user_id'] = result.get('id')
                session['usuario'] = result.get('usuario')
                session['cargo'] = result.get('cargo')
                return redirect("/")
            else:
                flash(result["message"], "error")

        return render_template("login.html")


    @app.route("/register", methods=["POST"])
    def register():
        if request.is_json:
            data = request.get_json()
            usuario = data.get("usuario")
            senha = data.get("senha")

            result = registrar_novo_usuario(usuario, senha)

            if result["status"]:
                session['user_id'] = result.get('id')
                session['usuario'] = usuario
                session['cargo'] = result.get('cargo')

            return jsonify(result)

        return jsonify({"status": False, "message": "Método inválido"}), 400


    @app.route("/api/check-first-user")
    def check_first_user():
        """Verifica se é o primeiro usuário"""
        total = get_total_users()
        return jsonify({"is_first_user": total == 0})


    @app.route("/logout")
    def logout():
        """Faz logout do usuário"""
        session.clear()
        flash("Logout realizado com sucesso!", "success")
        return redirect("/login")


    # -------- PÁGINAS iniciais --------
    @app.route("/")
    def home():
        # Redirecionar para login se não autenticado
        if 'usuario' not in session:
            return redirect("/login")
        return render_template("base.html")


    # Lista de produtos
    @app.route("/products")
    def list_products():
        data = get_products_grouped()
        return render_template("products.html", data=data)


    # Busca
    @app.route("/produtos")
    def produtos():

        search = request.args.get("search", "")

        data = search_products_grouped(search)

        return render_template("products.html", data=data)


    # Cadastro
    @app.route("/produtos/novo", methods=["GET", "POST"])
    def novo_produto():

        if request.method == "POST":

            action = request.form.get("action")

            # Cadastrar produto
            if action == "product":

                name = request.form.get("product_name")
                add_product(name)


            # Cadastrar item
            elif action == "item":

                product_id = request.form.get("product_id")
                name = request.form.get("item_name")
                price = request.form.get("price")
                stock = request.form.get("stock")

                add_item(product_id, name, price, stock)


            return redirect("/produtos")


        # GET → carregar lista de categorias únicas
        products = get_all_products()

        return render_template(
            "cadastro_de_produtos.html",
            products=products
        )


    # Editar item
    @app.route("/produtos/editar/<int:item_id>", methods=["GET", "POST"])
    def editar_produto(item_id):
        
        if request.method == "POST":
            name = request.form.get("item_name")
            price = request.form.get("price")
            stock = request.form.get("stock")
            product_id = request.form.get("product_id")
            
            update_item(item_id, name, price, stock, product_id)
            return redirect("/produtos")
        
        # GET → carregar item para edição e lista de categorias únicas
        item = get_item_by_id(item_id)
        products = get_all_products()
        
        return render_template(
            "cadastro_de_produtos.html",
            item=item,
            products=products,
            editing=True
        )


    # Editar categoria
    @app.route("/categoria/editar/<int:product_id>", methods=["GET", "POST"])
    def editar_categoria(product_id):
        
        if request.method == "POST":
            name = request.form.get("category_name")
            update_product(product_id, name)
            return redirect("/produtos")
        
        # GET → carregar categoria
        product = get_product_by_id(product_id)
        
        return render_template(
            "editar_categoria.html",
            product=product
        )


    # Deletar categoria
    @app.route("/categoria/remover/<int:product_id>")
    def remover_categoria(product_id):
        
        # Verificar se tem itens
        if product_has_items(product_id):
            from flask import jsonify
            return render_template(
                "erro_categoria.html",
                message="Não é possível remover esta categoria pois ela possui itens relacionados. Remova ou altere os itens primeiro."
            )
        
        # Se não tiver itens, deleta
        delete_product(product_id)
        return redirect("/produtos")


    # Remover item
    @app.route("/produtos/remover/<int:item_id>")
    def remover_produto(item_id):
        delete_item(item_id)
        return redirect("/produtos")


    # -------- VENDEDORES --------

    # Lista de vendedores
    @app.route("/vendedores")
    def list_sellers():
        # Support optional edit via ?id=<seller_id> so the form can be shown on the same page
        seller_id = request.args.get("id")
        search = request.args.get("search", "")
        seller = None

        if seller_id:
            seller = get_seller_by_id(seller_id)

        if search:
            data = search_sellers(search)
        else:
            data = get_all_sellers()

        return render_template("vendedores.html", data=data, seller=seller)


    # Busca de vendedores
    @app.route("/vendas")
    def vendas():
        grouped = get_products_grouped()

        products = []
        for product_id, product_data in grouped.items():
            category = product_data["name"]
            for item in product_data["items"]:
                products.append({
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"] or 0,
                    "stock": item["stock"] or 0,
                    "category": category
                })

        sellers = get_all_sellers()
        sellers_payload = [
            {"id": seller[0], "name": seller[1], "phone": seller[2]}
            for seller in sellers
        ]

        return render_template("vendas.html", products=products, sellers=sellers_payload)


    # Cadastro de vendedores
    @app.route("/vendedores/novo", methods=["GET", "POST"])
    def novo_vendedor():

        if request.method == "POST":
            action = request.form.get("action")

            # Cadastrar novo vendedor
            if action == "novo":
                name = request.form.get("seller_name")
                phone = request.form.get("phone")

                add_seller(name, phone)
                return redirect("/vendedores")

            # Editar vendedor
            elif action == "editar":
                seller_id = request.form.get("seller_id")
                name = request.form.get("seller_name")
                phone = request.form.get("phone")

                update_seller(seller_id, name, phone)
                return redirect("/vendedores")

        # GET
        seller_id = request.args.get("id")
        seller = None

        if seller_id:
            seller = get_seller_by_id(seller_id)

        return render_template(
            "cadastro_de_vendedores.html",
            seller=seller
        )


    # Remover vendedor
    @app.route("/vendedores/remover/<int:seller_id>")
    def remover_vendedor(seller_id):
        delete_seller(seller_id)
        return redirect("/vendedores")


    # -------- VENDAS / PERSISTÃŠNCIA --------

    @app.route("/api/vendas", methods=["POST"])
    def api_criar_venda():
        if not request.is_json:
            return jsonify({"erro": "Payload invÃ¡lido"}), 400

        data = request.get_json() or {}

        try:
            seller_id = int(data["seller_id"])
            seller_name = (data["seller_name"] or "").strip()
            subtotal = float(data["subtotal"])
            desconto = float(data.get("desconto", 0))
            desconto_tipo = data.get("desconto_tipo", "R$")
            total = float(data["total"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"erro": "Dados invÃ¡lidos"}), 400

        itens = data.get("itens", [])
        pagamentos = data.get("pagamentos", [])

        if not seller_name:
            return jsonify({"erro": "Vendedor invÃ¡lido"}), 400
        if not isinstance(itens, list) or not itens:
            return jsonify({"erro": "Itens invÃ¡lidos"}), 400
        if not isinstance(pagamentos, list) or not pagamentos:
            return jsonify({"erro": "Pagamentos invÃ¡lidos"}), 400

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO vendas
                (seller_id, seller_name, subtotal, desconto,
                 desconto_tipo, total, status, created_at)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    seller_id,
                    seller_name,
                    subtotal,
                    desconto,
                    desconto_tipo,
                    total,
                    "concluida",
                    agora,
                ),
            )
            venda_id = cur.lastrowid

            for item in itens:
                cur.execute(
                    """
                    INSERT INTO venda_itens
                    (venda_id, item_id, item_name,
                     quantidade, preco_unit, subtotal)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        venda_id,
                        item["item_id"],
                        item["item_name"],
                        item["quantidade"],
                        item["preco_unit"],
                        item["subtotal"],
                    ),
                )

            for pag in pagamentos:
                cur.execute(
                    "INSERT INTO venda_pagamentos VALUES (NULL,?,?,?)",
                    (venda_id, pag["metodo"], pag["valor"]),
                )

            conn.commit()

        return jsonify({"id": venda_id, "status": "ok"}), 201


    @app.route("/api/vendas", methods=["GET"])
    def api_listar_vendas():
        di = request.args.get("data_inicio", "2000-01-01")
        df = request.args.get("data_fim", "2099-12-31")
        sid = request.args.get("seller_id")
        sts = request.args.get("status")
        metodo = request.args.get("metodo")

        sql = """
            SELECT
                v.*,
                (
                    SELECT SUM(quantidade)
                    FROM venda_itens vi
                    WHERE vi.venda_id = v.id
                ) AS total_itens,
                (
                    SELECT GROUP_CONCAT(DISTINCT metodo)
                    FROM venda_pagamentos vp
                    WHERE vp.venda_id = v.id
                ) AS metodos
            FROM vendas v
            WHERE v.created_at BETWEEN ? AND ?
        """
        params = [di + " 00:00:00", df + " 23:59:59"]

        if sid:
            sql += " AND v.seller_id = ?"
            params.append(sid)
        if sts:
            sql += " AND v.status = ?"
            params.append(sts)
        if metodo:
            sql += """
                AND EXISTS (
                    SELECT 1 FROM venda_pagamentos vp2
                    WHERE vp2.venda_id = v.id
                      AND vp2.metodo = ?
                )
            """
            params.append(metodo)

        sql += " ORDER BY v.created_at DESC"

        with get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()

        return jsonify([dict(r) for r in rows])


    @app.route("/api/vendas/<int:vid>", methods=["GET"])
    def api_get_venda(vid):
        with get_connection() as conn:
            venda = conn.execute(
                "SELECT * FROM vendas WHERE id=?", (vid,)
            ).fetchone()

            if not venda:
                return jsonify({"erro": "nÃ£o encontrada"}), 404

            itens = conn.execute(
                "SELECT * FROM venda_itens WHERE venda_id=?", (vid,)
            ).fetchall()
            pags = conn.execute(
                "SELECT * FROM venda_pagamentos WHERE venda_id=?", (vid,)
            ).fetchall()

        return jsonify(
            {
                **dict(venda),
                "itens": [dict(i) for i in itens],
                "pagamentos": [dict(p) for p in pags],
            }
        )


    @app.route("/api/vendas/<int:vid>", methods=["PUT"])
    def api_editar_venda(vid):
        if not request.is_json:
            return jsonify({"erro": "Payload invÃ¡lido"}), 400

        data = request.get_json() or {}
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            subtotal = float(data["subtotal"])
            desconto = float(data.get("desconto", 0))
            desconto_tipo = data.get("desconto_tipo", "R$")
            total = float(data["total"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"erro": "Dados invÃ¡lidos"}), 400

        itens = data.get("itens", [])
        pagamentos = data.get("pagamentos", [])

        if not isinstance(itens, list) or not itens:
            return jsonify({"erro": "Itens invÃ¡lidos"}), 400
        if not isinstance(pagamentos, list) or not pagamentos:
            return jsonify({"erro": "Pagamentos invÃ¡lidos"}), 400

        with get_connection() as conn:
            conn.execute(
                """
                UPDATE vendas SET
                subtotal=?, desconto=?, desconto_tipo=?,
                total=?, status='editada', updated_at=?
                WHERE id=?
                """,
                (subtotal, desconto, desconto_tipo, total, agora, vid),
            )

            conn.execute("DELETE FROM venda_itens WHERE venda_id=?", (vid,))
            for item in itens:
                conn.execute(
                    """
                    INSERT INTO venda_itens
                    (venda_id, item_id, item_name,
                     quantidade, preco_unit, subtotal)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        vid,
                        item["item_id"],
                        item["item_name"],
                        item["quantidade"],
                        item["preco_unit"],
                        item["subtotal"],
                    ),
                )

            conn.execute("DELETE FROM venda_pagamentos WHERE venda_id=?", (vid,))
            for pag in pagamentos:
                conn.execute(
                    "INSERT INTO venda_pagamentos VALUES (NULL,?,?,?)",
                    (vid, pag["metodo"], pag["valor"]),
                )

            conn.commit()

        return jsonify({"status": "editada"})


    @app.route("/api/vendas/<int:vid>/cancelar", methods=["PATCH"])
    def api_cancelar_venda(vid):
        with get_connection() as conn:
            conn.execute("DELETE FROM venda_pagamentos WHERE venda_id=?", (vid,))
            conn.execute("DELETE FROM venda_itens WHERE venda_id=?", (vid,))
            conn.execute("DELETE FROM vendas WHERE id=?", (vid,))
            conn.commit()

        return jsonify({"status": "cancelada"})


    # -------- DASHBOARD --------

    @app.route("/api/dashboard/resumo", methods=["GET"])
    def api_dash_resumo():
        hoje = datetime.now().strftime("%Y-%m-%d")
        di = request.args.get("data_inicio", hoje)
        df = request.args.get("data_fim", hoje)
        metodo = request.args.get("metodo")

        sql = """
            SELECT
                COUNT(*)   AS qtd_vendas,
                SUM(total) AS faturamento,
                AVG(total) AS ticket_medio,
                MAX(total) AS maior_venda,
                MIN(total) AS menor_venda
            FROM vendas
            WHERE status = 'concluida'
              AND created_at BETWEEN ? AND ?
        """
        params = [di + " 00:00:00", df + " 23:59:59"]

        if metodo:
            sql += """
                AND EXISTS (
                    SELECT 1 FROM venda_pagamentos vp2
                    WHERE vp2.venda_id = vendas.id
                      AND vp2.metodo = ?
                )
            """
            params.append(metodo)

        with get_connection() as conn:
            r = conn.execute(sql, params).fetchone()

        return jsonify(dict(r) if r else {})


    @app.route("/api/dashboard/por-hora", methods=["GET"])
    def api_dash_por_hora():
        hoje = datetime.now().strftime("%Y-%m-%d")
        di = request.args.get("data_inicio", hoje)
        df = request.args.get("data_fim", hoje)
        metodo = request.args.get("metodo")

        sql = """
            SELECT
                CAST(strftime('%H', created_at) AS INTEGER) AS hora,
                COUNT(*)   AS qtd_vendas,
                SUM(total) AS faturamento
            FROM vendas
            WHERE status = 'concluida'
              AND created_at BETWEEN ? AND ?
        """
        params = [di + " 00:00:00", df + " 23:59:59"]

        if metodo:
            sql += """
                AND EXISTS (
                    SELECT 1 FROM venda_pagamentos vp2
                    WHERE vp2.venda_id = vendas.id
                      AND vp2.metodo = ?
                )
            """
            params.append(metodo)

        sql += """
            GROUP BY hora
            ORDER BY hora
        """

        with get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()

        return jsonify([dict(r) for r in rows])


    @app.route("/api/dashboard/por-vendedor", methods=["GET"])
    def api_dash_vendedor():
        hoje = datetime.now().strftime("%Y-%m-%d")
        di = request.args.get("data_inicio", hoje)
        df = request.args.get("data_fim", hoje)
        metodo = request.args.get("metodo")

        sql = """
            SELECT
                seller_name,
                COUNT(*)   AS qtd_vendas,
                SUM(total) AS faturamento,
                AVG(total) AS ticket_medio
            FROM vendas
            WHERE status = 'concluida'
              AND created_at BETWEEN ? AND ?
        """
        params = [di + " 00:00:00", df + " 23:59:59"]

        if metodo:
            sql += """
                AND EXISTS (
                    SELECT 1 FROM venda_pagamentos vp2
                    WHERE vp2.venda_id = vendas.id
                      AND vp2.metodo = ?
                )
            """
            params.append(metodo)

        sql += """
            GROUP BY seller_name
            ORDER BY faturamento DESC
        """

        with get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()

        return jsonify([dict(r) for r in rows])


    # -------- RELATÃ“RIOS --------

    @app.route("/relatorios")
    def pagina_relatorios():
        return render_template("relatorios.html")
