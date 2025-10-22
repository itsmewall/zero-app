# app/routes.py
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User
from .forms import RegisterForm, LoginForm

web_auth = Blueprint("web_auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

@web_auth.get("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    return render_template("index.html", title="App Zero")

@web_auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "warning")
            return redirect(url_for("web_auth.login"))
        user = User(email=email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Conta criada. Faça login.", "success")
        return redirect(url_for("web_auth.login"))
    return render_template("register.html", form=form, title="Criar conta")

@web_auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(form.password.data):
            flash("Credenciais inválidas.", "danger")
            return redirect(url_for("web_auth.login"))
        login_user(user, remember=True)
        nxt = request.args.get("next") or url_for("web_auth.dashboard")
        return redirect(nxt)
    return render_template("login.html", form=form, title="Entrar")

@web_auth.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("web_auth.home"))

@web_auth.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard")

# Healthcheck simples
@web_auth.get("/healthz")
def healthz():
    return "ok", 200, {"Content-Type": "text/plain"}
