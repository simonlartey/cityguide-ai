from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/terms")
def terms():
    return render_template("terms.html")


@main_bp.get("/privacy")
def privacy():
    return render_template("privacy.html")