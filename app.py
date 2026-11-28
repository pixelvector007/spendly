from functools import wraps
import os
import re
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

with app.app_context():
    init_db()
    seed_db()

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
DUPLICATE_EMAIL_ERROR = "An account with this email already exists."
INVALID_LOGIN_ERROR = "Invalid email or password."
MISSING_LOGIN_FIELDS_ERROR = "Please enter your email and password."


def login_required(view):
    """Redirect unauthenticated requests to the sign-in page."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def _validate_registration(name, email, password):
    """Return a validation error message for registration fields, or None."""
    if not name:
        return "Please enter your full name."
    if not email or not EMAIL_PATTERN.match(email):
        return "Please enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH or not password.strip():
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
    return None


def _render_register_error(message, name="", email=""):
    """Render the registration page with an error and preserved non-secret fields."""
    return render_template("register.html", error=message, name=name, email=email)


def _render_login_error(message, email=""):
    """Render the login page with an error and preserved email field."""
    return render_template("login.html", error=message, email=email)


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = _validate_registration(name, email, password)
        if error:
            return _render_register_error(error, name, email)

        if get_user_by_email(email) is not None:
            return _render_register_error(DUPLICATE_EMAIL_ERROR, name, email)

        password_hash = generate_password_hash(password)
        try:
            create_user(name, email, password_hash)
        except sqlite3.IntegrityError:
            return _render_register_error(DUPLICATE_EMAIL_ERROR, name, email)

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return _render_login_error(MISSING_LOGIN_FIELDS_ERROR, email)

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            return _render_login_error(INVALID_LOGIN_ERROR, email)

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("landing"))

    if "user_id" in session:
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
