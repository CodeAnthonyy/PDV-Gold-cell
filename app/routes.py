from main import app
from flask import render_template

# Rota principal
@app.route("/")
def home():
    return render_template("base.html")
