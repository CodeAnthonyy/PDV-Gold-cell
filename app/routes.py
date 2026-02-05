from main import app

from flask import render_template, request, redirect

from database.engine import (
    get_products_with_items,
    search_products,
    add_product,
    add_item
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
