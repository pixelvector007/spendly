from pathlib import Path
import re
import sys

import pytest

ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app as app_module
from database import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Provide a Flask test client backed by an isolated temporary SQLite database."""
    test_db = tmp_path / "test_spendly_auth.db"
    monkeypatch.setattr(db, "DB_PATH", str(test_db))
    db.init_db()
    db.seed_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def _extract_password_input_tag(html):
    """Return the password <input ...> tag markup from rendered HTML."""
    match = re.search(r"<input\b[^>]*\bid=[\"']password[\"'][^>]*>", html, re.IGNORECASE | re.DOTALL)
    assert match is not None
    return match.group(0)


def test_get_login_renders_form_and_logged_out_navbar(client):
    """GET /login renders the sign-in form and logged-out navbar links."""
    resp = client.get("/login")
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "Welcome back" in html
    assert 'name="email"' in html
    assert 'name="password"' in html
    assert "Sign in" in html
    assert "Get started" in html
    assert "Log out" not in html


@pytest.mark.parametrize("login_email", ["demo@spendly.com", "  DEMO@Spendly.COM  "])
def test_post_login_demo_user_sets_session_and_updates_navbar(client, login_email):
    """Valid login authenticates the user, populates session, and updates the navbar."""
    resp = client.post(
        "/login",
        data={"email": login_email, "password": "demo123"},
        follow_redirects=False,
    )

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")

    with client.session_transaction() as sess:
        assert "user_id" in sess
        assert isinstance(sess["user_id"], int)
        assert sess["user_name"] == "Demo User"
        assert "password_hash" not in sess

    home_resp = client.get("/")
    home_html = home_resp.get_data(as_text=True)
    assert home_resp.status_code == 200
    assert "Demo User" in home_html
    assert "Log out" in home_html
    assert "Get started" not in home_html


def test_post_login_newly_registered_user(client):
    """A user created via POST /register can sign in immediately via POST /login."""
    reg_resp = client.post(
        "/register",
        data={
            "name": "Priya Nair",
            "email": "priya@example.com",
            "password": "password123",
        },
        follow_redirects=False,
    )
    assert reg_resp.status_code == 302

    login_resp = client.post(
        "/login",
        data={"email": "PRIYA@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert login_resp.status_code == 302
    assert login_resp.headers["Location"].endswith("/")

    with client.session_transaction() as sess:
        assert "user_id" in sess
        assert sess["user_name"] == "Priya Nair"


@pytest.mark.parametrize(
    "email_input, password_input",
    [
        ("unknown@example.com", "demo123"),
        ("  Demo@Spendly.COM ", "wrong-secret-password"),
    ],
)
def test_post_login_invalid_credentials_preserves_email_and_omits_password_value(
    client, email_input, password_input
):
    """Invalid login shows generic error, keeps normalized email, and omits password value."""
    resp = client.post(
        "/login",
        data={"email": email_input, "password": password_input},
    )
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "auth-error" in html
    assert "Invalid email or password." in html
    assert f'value="{email_input.strip().lower()}"' in html

    password_tag = _extract_password_input_tag(html)
    assert "value=" not in password_tag.lower()
    assert password_input not in html

    with client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "", "password": "demo123"},
        {"email": "   ", "password": "demo123"},
        {"email": "demo@spendly.com", "password": ""},
        {"email": "", "password": ""},
    ],
)
def test_post_login_missing_fields(client, payload):
    """Blank email or password renders an error without crashing or setting a session."""
    resp = client.post("/login", data=payload)
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "auth-error" in html
    assert "Please enter your email and password." in html

    password_tag = _extract_password_input_tag(html)
    assert "value=" not in password_tag.lower()

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_get_login_while_authenticated_redirects_home(client):
    """Authenticated users visiting GET /login are redirected to /."""
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})

    resp = client.get("/login", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")


def test_logout_clears_session_and_redirects_to_login(client):
    """GET /logout clears the session, redirects to /login, and resets navbar."""
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})

    logout_resp = client.get("/logout", follow_redirects=False)
    assert logout_resp.status_code == 302
    assert logout_resp.headers["Location"].endswith("/login")

    with client.session_transaction() as sess:
        assert dict(sess) == {}

    login_html = client.get("/login").get_data(as_text=True)
    assert "Sign in" in login_html
    assert "Get started" in login_html
    assert "Log out" not in login_html


def test_logout_when_unauthenticated_redirects_cleanly(client):
    """GET /logout is safe when called without an active session."""
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_login_required_decorator_behavior_and_wraps(client):
    """login_required preserves metadata, redirects when logged out, and allows when logged in."""
    @app_module.login_required
    def protected_sample():
        """Protected sample docstring."""
        return "protected-ok"

    assert protected_sample.__name__ == "protected_sample"
    assert protected_sample.__doc__ == "Protected sample docstring."

    with app_module.app.test_request_context("/protected"):
        unauth_resp = protected_sample()
        assert unauth_resp.status_code == 302
        assert unauth_resp.headers["Location"].endswith("/login")

    with app_module.app.test_request_context("/protected"):
        app_module.session["user_id"] = 1
        assert protected_sample() == "protected-ok"


def test_placeholder_routes_remain_unprotected_in_step_3(client):
    """Step 4+ placeholder routes remain unchanged and do not redirect to /login yet."""
    resp = client.get("/profile", follow_redirects=False)
    assert resp.status_code == 200
    assert "Profile page" in resp.get_data(as_text=True)


def test_get_user_by_id_excludes_password_hash(client):
    """get_user_by_id returns non-secret columns only and None for unknown IDs."""
    demo_user = db.get_user_by_email("demo@spendly.com")
    assert demo_user is not None

    fetched = db.get_user_by_id(demo_user["id"])
    assert fetched is not None
    assert fetched["id"] == demo_user["id"]
    assert fetched["name"] == "Demo User"
    assert fetched["email"] == "demo@spendly.com"
    assert "password_hash" not in fetched.keys()
    assert db.get_user_by_id(999999) is None


def test_secret_key_is_configured_and_uses_env():
    """app.secret_key is populated and never empty."""
    assert app_module.app.secret_key
