# app/public.py – troca o JSON por render_template
from flask import Blueprint, render_template
public_bp = Blueprint("web_auth", __name__)  # simplificando o nome para bater com os templates

@public_bp.get("/")
def home():
    return render_template("index.html")

@public_bp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@public_bp.get("/login")
def login():
    return render_template("login.html", form=None)

@public_bp.get("/register")
def register():
    return render_template("register.html", form=None)
