from flask import Flask
from .extensions import db, migrate, jwt, api, ma
from .config import load_config
from .tenants.middleware import tenant_before_request
from .auth.routes import blp as auth_blp
from .core.routes import blp as core_blp
from .public import public

def create_app():
    app = Flask(__name__)
    load_config(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    api.init_app(app)
    ma  # touch
    app.before_request(tenant_before_request)
    api.register_blueprint(auth_blp, url_prefix="/auth")
    api.register_blueprint(core_blp, url_prefix="/api")
    app.register_blueprint(public)
    return app
