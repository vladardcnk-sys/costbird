from flask import Blueprint, render_template, request, redirect, flash, jsonify
from core.auth import login_required, current_user_id
from core.database import SessionLocal
from models.user import User, MarketplaceCredential

cabinet = Blueprint("cabinet", __name__, url_prefix="/cabinet")

MARKETPLACES = {
    "wildberries":  {"name": "Wildberries",   "color": "#a020f0", "emoji": "🟣"},
    "ozon":         {"name": "Ozon",           "color": "#005bff", "emoji": "🔵"},
    "yandex_market":{"name": "Яндекс Маркет", "color": "#fc3f1d", "emoji": "🔴"},
}


def get_user(db, user_id):
    return db.query(User).filter_by(id=user_id).first()


def get_credentials(db, user_id):
    creds = db.query(MarketplaceCredential).filter_by(
        user_id=user_id, is_active=True).all()
    return {c.marketplace: c for c in creds}


@cabinet.get("/")
@cabinet.get("")
@login_required
def dashboard():
    db = SessionLocal()
    try:
        user  = get_user(db, current_user_id())
        creds = get_credentials(db, user.id)
        connected = [
            {**MARKETPLACES[mp], "key": mp, "connected": True}
            for mp in MARKETPLACES if mp in creds
        ]
        not_connected = [
            {**MARKETPLACES[mp], "key": mp, "connected": False}
            for mp in MARKETPLACES if mp not in creds
        ]
        return render_template("cabinet/dashboard.html",
                               user=user, connected=connected,
                               not_connected=not_connected)
    finally:
        db.close()


@cabinet.get("/connect")
@login_required
def connect_page():
    mp = request.args.get("mp", "wildberries")
    if mp not in MARKETPLACES:
        return redirect("/cabinet")
    return render_template("cabinet/connect.html",
                           mp=mp, mp_info=MARKETPLACES[mp])


@cabinet.post("/connect")
@login_required
def connect():
    mp          = request.form.get("marketplace")
    api_key     = request.form.get("api_key", "").strip()
    client_id   = request.form.get("client_id", "").strip()
    campaign_id = request.form.get("campaign_id", "").strip()

    if not api_key or mp not in MARKETPLACES:
        flash("Заполните API-ключ", "error")
        return redirect(f"/cabinet/connect?mp={mp}")

    db = SessionLocal()
    try:
        uid = current_user_id()
        existing = db.query(MarketplaceCredential).filter_by(
            user_id=uid, marketplace=mp).first()
        if existing:
            existing.api_key     = api_key
            existing.client_id   = client_id or None
            existing.campaign_id = campaign_id or None
            existing.is_active   = True
        else:
            cred = MarketplaceCredential(
                user_id=uid, marketplace=mp,
                api_key=api_key,
                client_id=client_id or None,
                campaign_id=campaign_id or None,
            )
            db.add(cred)
        db.commit()
        flash(f"{MARKETPLACES[mp]['name']} подключён!", "success")
        return redirect("/cabinet")
    finally:
        db.close()


@cabinet.get("/expenses")
@login_required
def expenses():
    db = SessionLocal()
    try:
        user  = get_user(db, current_user_id())
        creds = get_credentials(db, user.id)
        return render_template("cabinet/expenses.html",
                               user=user, creds=creds,
                               marketplaces=MARKETPLACES)
    finally:
        db.close()


@cabinet.get("/profile")
@login_required
def profile():
    db = SessionLocal()
    try:
        user  = get_user(db, current_user_id())
        creds = get_credentials(db, user.id)
        return render_template("cabinet/profile.html",
                               user=user, creds=creds,
                               marketplaces=MARKETPLACES)
    finally:
        db.close()


@cabinet.post("/disconnect")
@login_required
def disconnect():
    mp = request.form.get("marketplace")
    db = SessionLocal()
    try:
        cred = db.query(MarketplaceCredential).filter_by(
            user_id=current_user_id(), marketplace=mp).first()
        if cred:
            cred.is_active = False
            db.commit()
    finally:
        db.close()
    return redirect("/cabinet")
