from flask_smorest import Blueprint
from flask import request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from ..tenants.models import User

blp = Blueprint("auth", __name__, description="Auth")

@blp.route("/login", methods=["POST"])
def login():
    payload = request.get_json() or {}
    user = User.query.filter_by(email=payload.get("email")).first()
    if not user or not check_password_hash(user.password_hash, payload.get("password","")):
        return {"msg":"invalid credentials"}, 401
    token = create_access_token(identity={"uid": user.id, "tenant": user.tenant_id, "role": user.role})
    return {"access_token": token}
