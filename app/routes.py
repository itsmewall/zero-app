# app/routes.py
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    session, current_app
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)

from . import db, login_manager
from .models import User, Company, Membership, Invite, ROLE_CHOICES
from .forms import (
    # login básico
    LoginForm,
    # convites
    InviteCreateForm, AcceptInviteForm,
    # wizard de registro
    RegisterModeForm, RegUserStepForm, RegCompanyStepForm, RegConfirmForm,
    InviteTokenForm, InviteProfileForm,
)

web_auth = Blueprint("web_auth", __name__)

# =========================
# Helpers
# =========================
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

def _current_company_or_none():
    m = Membership.query.filter_by(user_id=current_user.id, is_active=True).first()
    return m.company if m else None

def _must_company():
    c = _current_company_or_none()
    if not c:
        flash("Você não está vinculado a nenhuma empresa.", "danger")
        return None
    return c

def _require_role(company, roles=("owner", "admin")):
    mem = Membership.query.filter_by(
        user_id=current_user.id,
        company_id=company.id,
        is_active=True
    ).first()
    return bool(mem and mem.role in roles)

# Wizard session helpers
def _reg_reset():
    session.pop("reg", None)

def _reg_get():
    return session.get("reg", {})

def _reg_set(data: dict):
    session["reg"] = {**_reg_get(), **data}

# =========================
# Rotas públicas
# =========================
@web_auth.get("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    return render_template("index.html", title="App Zero")

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
    return render_template("auth/login.html", form=form, title="Entrar")

@web_auth.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("web_auth.home"))

@web_auth.get("/terms")
def terms():
    return render_template("legal/terms.html", title="Termos de Uso")

# =========================
# Dashboard
# =========================
@web_auth.get("/dashboard")
@login_required
def dashboard():
    company = _current_company_or_none()
    team = []
    pending_invites = []
    if company:
        team = Membership.query.filter_by(company_id=company.id, is_active=True).all()
        pending_invites = Invite.query.filter(
            Invite.company_id == company.id,
            Invite.accepted_at.is_(None),
            Invite.expires_at > datetime.utcnow(),
        ).all()

    return render_template(
        "dashboard/dashboard.html",
        title="Dashboard",
        company=company,
        team=team,
        pending_invites=pending_invites,
        users_count=len(team) if team else 1,
        projects_count=0,
    )

# =========================
# Convites
# =========================
@web_auth.route("/invites", methods=["GET", "POST"])
@login_required
def invites():
    company = _must_company()
    if company is None:
        return redirect(url_for("web_auth.dashboard"))

    form = InviteCreateForm()
    if form.validate_on_submit():
        if not _require_role(company, roles=("owner", "admin")):
            flash("Sem permissão para convidar.", "danger")
            return redirect(url_for("web_auth.invites"))
        try:
            days = int((form.days_valid.data or "7").strip())
        except ValueError:
            days = 7
        inv = Invite.new(
            company_id=company.id,
            email=form.email.data,
            role=form.role.data,
            days_valid=days
        )
        link = url_for("web_auth.accept_invite", token=inv.token, _external=True)
        flash(f"Convite criado. Envie este link: {link}", "success")
        return redirect(url_for("web_auth.invites"))

    pending = Invite.query.filter(
        Invite.company_id == company.id,
        Invite.accepted_at.is_(None),
        Invite.expires_at > datetime.utcnow(),
    ).order_by(Invite.created_at.desc()).all()

    used = Invite.query.filter(
        Invite.company_id == company.id,
        Invite.accepted_at.isnot(None),
    ).order_by(Invite.accepted_at.desc()).limit(20).all()

    return render_template(
        "dashboard/invites.html",
        form=form,
        company=company,
        pending=pending,
        used=used,
        title="Convites",
    )

@web_auth.post("/invites/<int:invite_id>/revoke")
@login_required
def revoke_invite(invite_id):
    company = _must_company()
    if company is None:
        return redirect(url_for("web_auth.invites"))
    if not _require_role(company, roles=("owner", "admin")):
        flash("Sem permissão para revogar.", "danger")
        return redirect(url_for("web_auth.invites"))

    inv = Invite.query.get(invite_id)
    if not inv or inv.company_id != company.id:
        flash("Convite não encontrado.", "warning")
        return redirect(url_for("web_auth.invites"))
    if inv.accepted_at:
        flash("Convite já foi aceito.", "warning")
        return redirect(url_for("web_auth.invites"))

    inv.expires_at = datetime.utcnow()  # invalida
    db.session.commit()
    flash("Convite revogado.", "info")
    return redirect(url_for("web_auth.invites"))

@web_auth.route("/accept-invite", methods=["GET", "POST"])
def accept_invite():
    token = request.args.get("token", "").strip()
    if not token:
        flash("Token ausente.", "danger")
        return redirect(url_for("web_auth.home"))

    inv = Invite.query.filter_by(token=token).first()
    if not inv:
        flash("Convite inválido.", "danger")
        return redirect(url_for("web_auth.home"))

    if inv.accepted_at:
        flash("Este convite já foi usado.", "warning")
        return redirect(url_for("web_auth.login"))

    if inv.expires_at <= datetime.utcnow():
        flash("Convite expirado.", "warning")
        return redirect(url_for("web_auth.home"))

    # Usuário já logado
    if current_user.is_authenticated:
        if current_user.email.strip().lower() != inv.email.strip().lower():
            flash("E-mail do convite é diferente do seu. Saia e acesse com o e-mail convidado.", "danger")
            return redirect(url_for("web_auth.dashboard"))
        exists = Membership.query.filter_by(
            user_id=current_user.id, company_id=inv.company_id
        ).first()
        if not exists:
            db.session.add(Membership(
                user_id=current_user.id,
                company_id=inv.company_id,
                role=inv.role,
                is_active=True
            ))
        inv.accepted_at = datetime.utcnow()
        db.session.commit()
        flash("Convite aceito. Você agora faz parte da empresa.", "success")
        return redirect(url_for("web_auth.dashboard"))

    # Usuário não logado
    existing = User.query.filter_by(email=inv.email.strip().lower()).first()
    if existing:
        flash("Já existe uma conta para este e-mail. Faça login para aceitar o convite.", "info")
        login_url = url_for("web_auth.login") + f"?next={url_for('web_auth.accept_invite', token=token)}"
        return redirect(login_url)

    # Renderiza tela de criação de conta a partir do convite
    form = AcceptInviteForm()
    if form.validate_on_submit():
        user = User(
            email=inv.email.strip().lower(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            tz="America/Sao_Paulo",
            locale="pt-BR",
        )
        user.set_password(form.password.data)
        db.session.add(user); db.session.flush()
        db.session.add(Membership(
            user_id=user.id,
            company_id=inv.company_id,
            role=inv.role,
            is_active=True
        ))
        inv.accepted_at = datetime.utcnow()
        db.session.commit()
        login_user(user, remember=True)
        flash("Conta criada e convite aceito. Bem-vindo.", "success")
        return redirect(url_for("web_auth.dashboard"))

    return render_template("dashboard/accept_invite.html", form=form, invite=inv, title="Aceitar convite")

# =========================
# Wizard de registro
# =========================
@web_auth.route("/register", methods=["GET", "POST"], endpoint="register")
def register_mode():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    form = RegisterModeForm()
    url_token = request.args.get("token")
    if url_token:
        form.mode.data = "invite"
    if form.validate_on_submit():
        _reg_reset()
        if form.mode.data == "invite":
            return redirect(url_for("web_auth.register_invite_step1", token=url_token or ""))
        return redirect(url_for("web_auth.register_company_step1"))
    return render_template("register/register_choose.html", form=form, title="Como deseja começar?")

# Alias para manter url_for('web_auth.register_mode') válido nos templates antigos
web_auth.add_url_rule(
    "/register",
    endpoint="register_mode",
    view_func=register_mode,
    methods=["GET", "POST"],
)

# Criar empresa - passo 1
@web_auth.route("/register/company/step-1", methods=["GET", "POST"])
def register_company_step1():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    form = RegUserStepForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado. Faça login.", "warning")
            return redirect(url_for("web_auth.login"))
        _reg_set({
            "mode": "company",
            "user": {
                "first_name": form.first_name.data.strip(),
                "last_name": form.last_name.data.strip(),
                "email": email,
                "password": form.password.data,
                "job_title": (form.job_title.data or "").strip() or None,
                "phone": (form.phone.data or "").strip() or None,
                "tz": form.tz.data,
            }
        })
        return redirect(url_for("web_auth.register_company_step2"))
    return render_template("register/register_company_step1.html", form=form, title="Seus dados")

# Criar empresa - passo 2
@web_auth.route("/register/company/step-2", methods=["GET", "POST"])
def register_company_step2():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    reg = _reg_get()
    if not reg or reg.get("mode") != "company" or "user" not in reg:
        return redirect(url_for("web_auth.register_company_step1"))
    form = RegCompanyStepForm()
    if form.validate_on_submit():
        _reg_set({
            "company": {
                "legal_name": form.company_legal_name.data.strip(),
                "trade_name": (form.company_trade_name.data or "").strip() or None,
                "tax_id": (form.tax_id.data or "").strip() or None,
                "country": form.country.data.strip().upper(),
                "tz": form.company_tz.data,
            }
        })
        return redirect(url_for("web_auth.register_company_confirm"))
    return render_template("register/register_company_step2.html", form=form, title="Dados da empresa")

# Criar empresa - confirmar
@web_auth.route("/register/company/confirm", methods=["GET", "POST"])
def register_company_confirm():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    reg = _reg_get()
    if not reg or reg.get("mode") != "company" or "user" not in reg or "company" not in reg:
        return redirect(url_for("web_auth.register_company_step1"))

    form = RegConfirmForm()
    if not current_app.config.get("REQUIRE_TERMS", True):
        form.accept_terms.validators = []
        form.accept_terms.data = True

    if form.validate_on_submit():
        u = reg["user"]; c = reg["company"]
        if User.query.filter_by(email=u["email"]).first():
            flash("E-mail já cadastrado. Faça login.", "warning")
            return redirect(url_for("web_auth.login"))

        company = Company(
            legal_name=c["legal_name"], trade_name=c["trade_name"], tax_id=c["tax_id"],
            country=c["country"], tz=c["tz"], plan="free"
        )
        db.session.add(company); db.session.flush()

        user = User(
            email=u["email"], first_name=u["first_name"], last_name=u["last_name"],
            job_title=u["job_title"], phone=u["phone"], tz=u["tz"], locale="pt-BR"
        )
        user.set_password(u["password"])
        db.session.add(user); db.session.flush()

        company.owner_user_id = user.id
        db.session.add(Membership(
            user_id=user.id, company_id=company.id, role="owner", is_active=True
        ))

        db.session.commit()
        _reg_reset()
        login_user(user, remember=True)
        flash("Conta e empresa criadas. Bem-vindo.", "success")
        return redirect(url_for("web_auth.dashboard"))

    return render_template("register/register_company_confirm.html", form=form, reg=reg, title="Revisar e confirmar")

# Entrar com convite - passo 1
@web_auth.route("/register/invite/step-1", methods=["GET", "POST"])
def register_invite_step1():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    form = InviteTokenForm()
    pre = request.args.get("token", "").strip()
    if pre:
        form.token.data = pre
    if form.validate_on_submit():
        token = form.token.data.strip()
        inv = Invite.query.filter_by(token=token).first()
        if not inv or inv.accepted_at or inv.expires_at <= datetime.utcnow():
            flash("Convite inválido ou expirado.", "danger")
            return redirect(url_for("web_auth.register_invite_step1"))
        _reg_set({"mode": "invite", "invite": {"token": token}})
        return redirect(url_for("web_auth.register_invite_step2"))
    return render_template("register/register_invite_step1.html", form=form, title="Informe o convite")

# Entrar com convite - passo 2
@web_auth.route("/register/invite/step-2", methods=["GET", "POST"])
def register_invite_step2():
    if current_user.is_authenticated:
        return redirect(url_for("web_auth.dashboard"))
    reg = _reg_get()
    if not reg or reg.get("mode") != "invite" or "invite" not in reg:
        return redirect(url_for("web_auth.register_invite_step1"))

    inv = Invite.query.filter_by(token=reg["invite"]["token"]).first()
    if not inv or inv.accepted_at or inv.expires_at <= datetime.utcnow():
        flash("Convite inválido ou expirado.", "danger")
        return redirect(url_for("web_auth.register_invite_step1"))

    form = InviteProfileForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=inv.email.strip().lower()).first()
        if existing:
            flash("Já existe conta para este e-mail. Faça login para aceitar o convite.", "info")
            return redirect(url_for("web_auth.login", next=url_for("web_auth.accept_invite", token=inv.token)))

        user = User(
            email=inv.email.strip().lower(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            tz="America/Sao_Paulo", locale="pt-BR"
        )
        user.set_password(form.password.data)
        db.session.add(user); db.session.flush()
        db.session.add(Membership(
            user_id=user.id, company_id=inv.company_id, role=inv.role, is_active=True
        ))
        inv.accepted_at = datetime.utcnow()
        db.session.commit()
        _reg_reset()
        login_user(user, remember=True)
        flash("Convite aceito. Bem-vindo à empresa.", "success")
        return redirect(url_for("web_auth.dashboard"))

    return render_template("register/register_invite_step2.html", form=form, invite=inv, title="Seu perfil")

# =========================
# Healthcheck
# =========================
@web_auth.get("/healthz")
def healthz():
    return "ok", 200, {"Content-Type": "text/plain"}
