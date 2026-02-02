from flask import Flask
from database.engine import init_db

app = Flask(__name__)

init_db()

from routes import *


if __name__ == "__main__":
    app.run(debug=True)
