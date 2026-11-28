from pathlib import Path
import sys

import pytest
from werkzeug.security import check_password_hash

ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app as app_module
from database import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Provide a Flask test client backed by an isolated temporary SQLite database."""
    test_db = tmp_path / "test_spendly.db"
    monkeypatch.setattr(db, "DB_PATH", str(test_db))
    db.init_db()
    db.seed_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def _user_count():
    """Return total rows in the users table for the active test database."""
    conn = db.get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def test_get_register_renders_form(client):
    """GET /register should render the registration form extending base layout."""
    resp = client.get("/register")
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "Create your account" in html
    assert 'name="name"' in html
    assert 'name="email"' in html
    assert 'name="password"' in html


def test_post_register_creates_user_and_redirects(client):
    """Valid registration stores normalized email, hashed password, and redirects to /login."""
    resp = client.post(
        "/register",
        data={
            "name": "  Asha Verma  ",
            "email": "  Asha.Verma@Example.COM ",
            "password": "securepass123",
        },
        follow_redirects=False,
    )

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    assert _user_count() == 2

    user = db.get_user_by_email("asha.verma@example.com")
    assert user is not None
    assert user["name"] == "Asha Verma"
    assert user["email"] == "asha.verma@example.com"
    assert user["password_hash"] != "securepass123"
    assert check_password_hash(user["password_hash"], "securepass123")


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
            {"name": "   ", "email": "asha@example.com", "password": "password123"},
            "Please enter your full name.",
        ),
        (
            {"name": "Asha", "email": "not-an-email", "password": "password123"},
            "Please enter a valid email address.",
        ),
        (
            {"name": "Asha", "email": "asha@example", "password": "password123"},
            "Please enter a valid email address.",
        ),
        (
            {"name": "Asha", "email": "asha@example.com", "password": "short"},
            "Password must be at least 8 characters long.",
        ),
        (
            {"name": "Asha", "email": "asha@example.com", "password": "        "},
            "Password must be at least 8 characters long.",
        ),
    ],
)
def test_post_register_validation_errors(client, payload, expected_error):
    """Invalid registration inputs should render .auth-error without creating a user."""
    resp = client.post("/register", data=payload)
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "auth-error" in html
    assert expected_error in html
    assert _user_count() == 1
    assert f'value="{payload["name"].strip()}"' in html
    assert f'value="{payload["email"].strip().lower()}"' in html
    assert f'value="{payload["password"]}"' not in html


@pytest.mark.parametrize("duplicate_email", ["demo@spendly.com", "DEMO@spendly.com", "  Demo@Spendly.COM "])
def test_post_register_rejects_duplicate_email_case_insensitive(client, duplicate_email):
    """Duplicate emails (regardless of case/whitespace) must be rejected cleanly."""
    resp = client.post(
        "/register",
        data={
            "name": "Duplicate Tester",
            "email": duplicate_email,
            "password": "password123",
        },
    )
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "auth-error" in html
    assert "An account with this email already exists." in html
    assert _user_count() == 1
    assert 'value="Duplicate Tester"' in html
    assert f'value="{duplicate_email.strip().lower()}"' in html


def test_post_register_handles_integrity_error(client, monkeypatch):
    """IntegrityError during insert should render .auth-error instead of raising 500."""
    monkeypatch.setattr(app_module, "get_user_by_email", lambda _email: None)

    resp = client.post(
        "/register",
        data={
            "name": "Race Condition",
            "email": "demo@spendly.com",
            "password": "password123",
        },
    )
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "auth-error" in html
    assert "An account with this email already exists." in html
    assert _user_count() == 1


def test_public_routes_regression(client):
    """Existing public pages continue returning HTTP 200."""
    for path in ["/", "/register", "/login", "/terms", "/privacy"]:
        resp = client.get(path)
        assert resp.status_code == 200
