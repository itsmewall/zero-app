# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "web_auth.login"

    # modelos precisam ser importados antes de create_all
    from .models import User  # noqa

    # rotas
    from .routes import web_auth as web_auth_bp
    app.register_blueprint(web_auth_bp)

    # cria tabelas na primeira subida
    with app.app_context():
        db.create_all()
    
    return app

wsgi_app = create_app()