from flask import Blueprint, render_template

site = Blueprint("site", __name__)


@site.get("/")
def index():
    return render_template("index.html")


@site.get("/pricing")
def pricing():
    return render_template("pricing.html")


@site.get("/docs")
def docs():
    return render_template("docs.html")
