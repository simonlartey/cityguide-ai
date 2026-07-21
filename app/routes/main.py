from flask import Blueprint, current_app, render_template

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


@main_bp.get("/dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        maps_javascript_api_key=current_app.config.get(
            "MAPS_JAVASCRIPT_API_KEY"
        ),
        google_map_id=current_app.config.get(
            "GOOGLE_MAP_ID"
        ),
    )