# app/models.py
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint, Index
from secrets import token_urlsafe
from . import db

ROLE_CHOICES = ("owner", "admin", "manager", "operator", "viewer")

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    legal_name = db.Column(db.String(160), nullable=False)       # razão social ou nome oficial
    trade_name = db.Column(db.String(160))                        # nome fantasia
    tax_id = db.Column(db.String(32))                             # CNPJ/Outro doc
    country = db.Column(db.String(2), default="BR")
    tz = db.Column(db.String(64), default="America/Sao_Paulo")
    plan = db.Column(db.String(32), default="free")
    industry = db.Column(db.String(64))
    owner_user_id = db.Column(db.Integer)                         # usuário "dono" inicial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_companies_tax", "tax_id"),
    )

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    job_title = db.Column(db.String(80))
    phone = db.Column(db.String(32))
    tz = db.Column(db.String(64), default="America/Sao_Paulo")
    locale = db.Column(db.String(8), default="pt-BR")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    memberships = db.relationship("Membership", backref="user", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Membership(db.Model):
    __tablename__ = "memberships"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    role = db.Column(db.String(16), default="operator")  # owner/admin/manager/operator/viewer
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", backref=db.backref("memberships", lazy="dynamic"))

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
        Index("ix_memberships_company", "company_id"),
    )

class Invite(db.Model):
    __tablename__ = "invites"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    role = db.Column(db.String(16), default="viewer")
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    accepted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company")

    @staticmethod
    def new(company_id: int, email: str, role: str = "viewer", days_valid: int = 7):
        inv = Invite(
            company_id=company_id,
            email=email.strip().lower(),
            role=role if role in ROLE_CHOICES else "viewer",
            token=token_urlsafe(24),
            expires_at=datetime.utcnow() + timedelta(days=days_valid),
        )
        db.session.add(inv)
        db.session.commit()
        return inv
