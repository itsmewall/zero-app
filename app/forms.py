# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=72)])
    confirm = PasswordField("Confirme a senha", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Criar conta")

class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")
