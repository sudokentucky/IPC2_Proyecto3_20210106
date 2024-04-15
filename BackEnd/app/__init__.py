# app/__init__.py

from flask import Flask
from .views import bp  # Asegúrate de tener la ruta correcta al importar

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
