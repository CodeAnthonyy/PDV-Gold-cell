import os
import sys
from flask import Flask
from database.engine import init_db
from database.engine import add_product
from database.engine import add_item

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _resource_path(*parts):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, *parts)
    return os.path.join(BASE_DIR, *parts)

templates_dir = _resource_path("templates")
static_dir = _resource_path("static")

app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
app.secret_key = 'your-secret-key-change-this-in-production'

init_db()

# Importar e registrar rotas
from routes import register_routes
register_routes(app)


if __name__ == "__main__":
    app.run(debug=True)
