from flask import Flask
from database.engine import init_db
from database.engine import add_product
from database.engine import add_item

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

init_db()

# Importar e registrar rotas
from routes import register_routes
register_routes(app)


if __name__ == "__main__":
    app.run(debug=True)