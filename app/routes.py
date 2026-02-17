from main import app

from flask import render_template, request, redirect

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
    search_sellers
)

# Tela inicial
@app.route("/")
def home():
    return render_template("base.html")


# Lista de produtos
@app.route("/products")
def list_products():
    data = get_products_with_items()
    return render_template("products.html", data=data)


# Busca
@app.route("/produtos")
def produtos():

    search = request.args.get("search", "")

    data = search_products(search)

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


    # GET → carregar lista
    products = get_products_with_items()

    return render_template(
        "cadastro_de_produtos.html",
        products=products
    )


# -------- VENDEDORES --------

# Lista de vendedores
@app.route("/vendedores")
def list_sellers():
    data = get_all_sellers()
    return render_template("vendedores.html", data=data)


# Busca de vendedores
@app.route("/vendas")
def vendas():
    search = request.args.get("search", "")
    data = search_sellers(search)
    return render_template("vendedores.html", data=data)


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
