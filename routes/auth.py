from flask import Blueprint, render_template, request, redirect, session, flash
from core.database import SessionLocal
from core.auth import create_token, current_user_id
from models.user import User

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.get("/register")
def register_page():
    if current_user_id():
        return redirect("/cabinet")
    return render_template("auth/register.html")


@auth.post("/register")
def register():
    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not all([name, email, password]):
        flash("Заполните все поля", "error")
        return render_template("auth/register.html")

    if len(password) < 8:
        flash("Пароль минимум 8 символов", "error")
        return render_template("auth/register.html")

    db = SessionLocal()
    try:
        if db.query(User).filter_by(email=email).first():
            flash("Email уже зарегистрирован", "error")
            return render_template("auth/register.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_token(user.id, user.email)
        session["token"] = token
        return redirect("/cabinet")
    finally:
        db.close()


@auth.get("/login")
def login_page():
    if current_user_id():
        return redirect("/cabinet")
    return render_template("auth/login.html")


@auth.post("/login")
def login():
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Неверный email или пароль", "error")
            return render_template("auth/login.html")

        token = create_token(user.id, user.email)
        session["token"] = token
        return redirect("/cabinet")
    finally:
        db.close()


@auth.get("/logout")
def logout():
    session.pop("token", None)
    return redirect("/")
