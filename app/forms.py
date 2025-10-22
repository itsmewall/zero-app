# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


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

class InviteCreateForm(FlaskForm):
    email = StringField("E-mail do convidado", validators=[DataRequired(), Email(), Length(max=160)])
    role = SelectField("Papel", choices=[
        ("viewer","Viewer"),
        ("operator","Operator"),
        ("manager","Manager"),
        ("admin","Admin"),
    ], default="viewer")
    days_valid = StringField("Validade (dias)", default="7")
    submit = SubmitField("Gerar convite")

class AcceptInviteForm(FlaskForm):
    first_name = StringField("Nome", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Sobrenome", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=72)])
    confirm = PasswordField("Confirme a senha", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Criar conta e entrar")

    # Wizard: escolha de modo
class RegisterModeForm(FlaskForm):
    mode = SelectField(
        "Como deseja começar?",
        choices=[("company", "Criar empresa"), ("invite", "Entrar com convite")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Continuar")

# Fluxo Criar Empresa
class RegUserStepForm(FlaskForm):
    first_name = StringField("Nome", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Sobrenome", validators=[DataRequired(), Length(max=80)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=72)])
    confirm = PasswordField("Confirme a senha", validators=[DataRequired(), EqualTo("password")])
    job_title = StringField("Cargo", validators=[Optional(), Length(max=80)])
    phone = StringField("Telefone", validators=[Optional(), Length(max=32)])
    tz = SelectField("Seu fuso horário", choices=[
        ("America/Sao_Paulo","America/Sao_Paulo"), ("America/New_York","America/New_York"), ("UTC","UTC")
    ], default="America/Sao_Paulo")
    submit = SubmitField("Próximo")

class RegCompanyStepForm(FlaskForm):
    company_legal_name = StringField("Nome da empresa", validators=[DataRequired(), Length(max=160)])
    company_trade_name = StringField("Nome fantasia", validators=[Optional(), Length(max=160)])
    tax_id = StringField("Documento fiscal", validators=[Optional(), Length(max=32)])
    country = StringField("País", default="BR", validators=[DataRequired(), Length(max=2)])
    company_tz = SelectField("Fuso da empresa", choices=[
        ("America/Sao_Paulo","America/Sao_Paulo"), ("America/New_York","America/New_York"), ("UTC","UTC")
    ], default="America/Sao_Paulo")
    submit = SubmitField("Revisar")

class RegConfirmForm(FlaskForm):
    accept_terms = BooleanField("Li e concordo com os Termos de Uso", validators=[DataRequired()])
    submit = SubmitField("Criar conta e empresa")

# Fluxo Convite
class InviteTokenForm(FlaskForm):
    token = StringField("Token do convite", validators=[DataRequired(), Length(min=10, max=80)])
    submit = SubmitField("Validar token")

class InviteProfileForm(FlaskForm):
    first_name = StringField("Nome", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Sobrenome", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=72)])
    confirm = PasswordField("Confirme a senha", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Finalizar e entrar")
