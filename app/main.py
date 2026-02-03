from flask import Flask
from database.engine import init_db
from database.engine import add_product
from database.engine import add_item

app = Flask(__name__)

init_db()

from routes import *


if __name__ == "__main__":
    app.run(debug=True)
