import os
from dotenv import load_dotenv

def load_config(app):
    load_dotenv()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["API_TITLE"] = "App Zero API"
    app.config["API_VERSION"] = "1.0"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "insecure")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "insecure")
    app.config["TENANT_HEADER"] = os.getenv("TENANT_HEADER", "X-Tenant")
    app.config["DEFAULT_BLUEPRINT"] = os.getenv("DEFAULT_BLUEPRINT", "restaurant.yaml")
