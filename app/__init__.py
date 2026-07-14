from flask import Flask

from config import Config


def create_app(config_class=Config):
    """Create and configure the CityGuide Flask application."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app