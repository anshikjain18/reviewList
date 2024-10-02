from flask import Flask

from app.views import views


def create_app():
    app = Flask(__name__)
    app.register_blueprint(views)

    return app
