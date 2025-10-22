# app/__init__.py
import os, pathlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # cfg
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # use caminho absoluto para não criar db perdido em outra pasta
    base = pathlib.Path(__file__).resolve().parent.parent
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{base / 'app.db'}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["REQUIRE_TERMS"] = True

    db.init_app(app)
    login_manager.init_app(app)

    # IMPORTA OS MODELS AQUI
    from . import models  # noqa

    migrate.init_app(app, db)

    from .routes import web_auth
    app.register_blueprint(web_auth)

    return app
