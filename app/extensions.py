from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from marshmallow import Schema

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api()
ma = Schema
