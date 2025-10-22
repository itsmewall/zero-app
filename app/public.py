# app/public.py
from flask import Blueprint, jsonify

public = Blueprint("public", __name__)

@public.get("/")
def index():
    return jsonify({
        "name": "App Zero API",
        "status": "ok",
        "docs": "/docs",
        "health": "/healthz"
    })

@public.get("/healthz")
def healthz():
    return "ok", 200, {"Content-Type": "text/plain"}