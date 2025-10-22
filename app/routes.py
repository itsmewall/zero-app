# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User, Company, Membership, Invite, ROLE_CHOICES
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

        # 1) Cria empresa
        company = Company(
            legal_name=form.company_legal_name.data.strip(),
            trade_name=(form.company_trade_name.data or "").strip() or None,
            tax_id=(form.tax_id.data or "").strip() or None,
            country=form.country.data.strip().upper(),
            tz=form.company_tz.data,
            plan="free",
        )
        db.session.add(company)
        db.session.flush()  # pega id

        # 2) Cria usuário
        user = User(
            email=email,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            job_title=(form.job_title.data or "").strip() or None,
            phone=(form.phone.data or "").strip() or None,
            tz=form.tz.data,
            locale="pt-BR",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        # 3) Owner da empresa
        company.owner_user_id = user.id

        # 4) Vínculo como owner
        membership = Membership(user_id=user.id, company_id=company.id, role="owner", is_active=True)
        db.session.add(membership)

        db.session.commit()
        flash("Conta e empresa criadas. Faça login.", "success")
        return redirect(url_for("web_auth.login"))
    return render_template("register.html", form=form, title="Criar conta e empresa")

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
    # Descobre a empresa ativa do usuário. Aqui pegamos a primeira.
    m = Membership.query.filter_by(user_id=current_user.id, is_active=True).first()
    company = m.company if m else None
    return render_template("dashboard.html", title="Dashboard", company=company)

# Health
@web_auth.get("/healthz")
def healthz():
    return "ok", 200, {"Content-Type": "text/plain"}
