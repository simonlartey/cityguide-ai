from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.auth_service import (
    DuplicateEmailError,
    SignupData,
    SignupValidationError,
    authenticate_user,
    create_user,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    signup_success = request.args.get("signup") == "success"
    error = ""
    email_value = ""

    if request.method == "POST":
        email_value = request.form.get("email", "")
        password = request.form.get("password", "")

        user = authenticate_user(email_value, password)

        if user is None:
            error = "Invalid email or password."
        else:
            session.clear()
            session["user_id"] = user.id
            session.permanent = request.form.get("remember") == "on"

            return redirect(url_for("main.index"))

    return render_template(
        "login.html",
        signup_success=signup_success,
        error=error,
        email_value=email_value,
    )


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    errors: dict[str, str] = {}
    form_data = {
        "displayName": "",
        "email": "",
    }

    if request.method == "POST":
        form_data = {
            "displayName": request.form.get("displayName", ""),
            "email": request.form.get("email", ""),
        }

        signup_data = SignupData(
            display_name=form_data["displayName"],
            email=form_data["email"],
            password=request.form.get("password", ""),
            confirm_password=request.form.get("confirmPassword", ""),
            accepted_terms=request.form.get("terms") == "on",
        )

        try:
            create_user(signup_data)
        except SignupValidationError as error:
            errors = error.errors
        except DuplicateEmailError as error:
            errors = {"email": str(error)}
        else:
            return redirect(url_for("auth.login", signup="success"))

    return render_template(
        "signup.html",
        errors=errors,
        form_data=form_data,
    )


@auth_bp.post("/logout")
def logout():
    session.clear()

    return redirect(url_for("auth.login"))