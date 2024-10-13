from flask import Flask
from dotenv import load_dotenv

from app.views import views


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.register_blueprint(views)

    return app
