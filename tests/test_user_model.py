from app.extensions import db
from app.models import User


def test_user_password_is_hashed(app):
    with app.app_context():
        user = User(
            email="simon@example.com",
            display_name="Simon Lartey",
            password_hash="",
        )

        user.set_password("secure-password-123")

        assert user.password_hash != "secure-password-123"
        assert user.check_password("secure-password-123")
        assert not user.check_password("incorrect-password")


def test_user_can_be_persisted(app):
    with app.app_context():
        db.create_all()

        user = User(
            email="simon@example.com",
            display_name="Simon Lartey",
            password_hash="",
        )
        user.set_password("secure-password-123")

        db.session.add(user)
        db.session.commit()

        saved_user = db.session.execute(
            db.select(User).where(User.email == "simon@example.com")
        ).scalar_one()

        assert saved_user.id is not None
        assert saved_user.display_name == "Simon Lartey"