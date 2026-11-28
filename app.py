import re
import sqlite3

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)

with app.app_context():
    init_db()
    seed_db()

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
DUPLICATE_EMAIL_ERROR = "An account with this email already exists."


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


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


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
