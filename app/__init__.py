from flask import Flask

from app.extensions import db, migrate
from config import Config


def create_app(config_class=Config):
    """Create and configure the CityGuide Flask application."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app