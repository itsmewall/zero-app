# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

TZ_CHOICES = [
    ("America/Sao_Paulo", "America/Sao_Paulo"),
    ("America/New_York", "America/New_York"),
    ("UTC", "UTC"),
]

ROLE_CHOICES = [
    ("owner", "Owner"),
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("operator", "Operator"),
    ("viewer", "Viewer"),
]

class RegisterForm(FlaskForm):
    # Usuário
    first_name = StringField("Nome", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Sobrenome", validators=[DataRequired(), Length(max=80)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=72)])
    confirm = PasswordField("Confirme a senha", validators=[DataRequired(), EqualTo("password")])
    job_title = StringField("Cargo", validators=[Optional(), Length(max=80)])
    phone = StringField("Telefone", validators=[Optional(), Length(max=32)])
    tz = SelectField("Fuso horário", choices=TZ_CHOICES, default="America/Sao_Paulo")

    # Empresa
    company_legal_name = StringField("Nome da empresa", validators=[DataRequired(), Length(max=160)])
    company_trade_name = StringField("Nome fantasia", validators=[Optional(), Length(max=160)])
    tax_id = StringField("Documento fiscal", validators=[Optional(), Length(max=32)])
    country = StringField("País", default="BR", validators=[DataRequired(), Length(max=2)])
    company_tz = SelectField("Fuso da empresa", choices=TZ_CHOICES, default="America/Sao_Paulo")

    # Opções
    accept_terms = BooleanField("Aceito os termos", validators=[DataRequired()])
    submit = SubmitField("Criar conta e empresa")

class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")
