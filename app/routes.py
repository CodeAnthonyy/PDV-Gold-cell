from main import app
from flask import render_template
from database.engine import get_products_with_items
from database.engine import search_products
from flask import request


# Rota tela inicial
@app.route("/")
def home():
    return render_template("base.html")

#rota para buscar produtos
@app.route("/products")
def list_products():
    data = get_products_with_items()
    return render_template("products.html", data=data)

#DEFINIR
@app.route("/produtos")
def produtos():

    search = request.args.get("search", "")

    data = search_products(search)

    return render_template("products.html", data=data)
