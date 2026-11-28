# Spec: Login and Logout

## Overview
This feature implements user authentication (`POST /login`) and session termination (`/logout`) for Spendly using Flask's signed cookie `session` and Werkzeug password verification. At this stage of the roadmap—immediately following database setup and user registration—it enables registered users and the seeded demo account (`demo@spendly.com`) to sign in, persist their authenticated session across requests, see session-aware navigation in the header, and securely sign out. It also establishes a reusable `login_required` decorator for upcoming protected features (profile and expense CRUD).

## Depends on
- **Step 01 — Database Setup** (`01-database-setup`): Requires the `users` table, `get_db()`, and seeded demo user in `database/db.py`.
- **Step 02 — Registration** (`02-registration`): Requires user registration and `get_user_by_email(email)` in `database/db.py` (with lowercase normalized emails and Werkzeug password hashes).

## Routes
- `GET /login` — Render the sign-in form (`templates/login.html`). If the user is already authenticated (`session.get("user_id")`), redirect to `/` (`landing`) — public
- `POST /login` — Validate `email` and `password` form fields, look up the user by normalized email, verify the password hash with `check_password_hash`, store `user_id` and `user_name` in `session`, and redirect to `/` (`landing`); on invalid input or credentials, re-render `templates/login.html` with an `error` message — public
- `GET /logout` — Clear the Flask `session` (`session.clear()`) and redirect to `/login` (`login`) — logged-in (safe no-op redirect if unauthenticated)

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) in `database/db.py` already supports authentication.

## Templates
- **Create:** None
- **Modify:**
  - `templates/base.html` — Update `.nav-links` to check `session.get("user_id")`: when logged in, display the user's name (linking to `url_for('profile')`) and a `Log out` link (`url_for('logout')`); when logged out, display `Sign in` (`url_for('login')`) and `Get started` (`url_for('register')`).
  - `templates/login.html` — Preserve the submitted `email` value in the email input (`value="{{ email or '' }}"`) when re-rendering after a failed login attempt, while never pre-filling the `password` field.

## Files to change
- `app.py` — Load `app.secret_key` from environment variables; implement `GET`/`POST` handling in `login()`; replace the `/logout` stub with session-clearing logout logic; add a reusable `login_required` route decorator.
- `database/db.py` — Reuse existing `get_user_by_email(email)` (and add `get_user_by_id(user_id)` if needed for session user lookups) using parameterized `SELECT` queries.
- `templates/base.html` — Add conditional logged-in / logged-out navigation links.
- `templates/login.html` — Repopulate the `email` field on error.
- `static/css/style.css` — Add styling for the logged-in navbar user label/link if needed, using existing CSS custom properties.

## Files to create
- `tests/test_auth.py` — Pytest suite covering `GET /login`, valid login (including seeded demo user), invalid email/password handling, session persistence, `login_required` behavior, and `/logout`.

## New dependencies
No new dependencies. Uses `flask` (`session`, `redirect`, `url_for`, `request`, `render_template`), `werkzeug.security` (`check_password_hash`), and `pytest` / `pytest-flask` already pinned in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`check_password_hash` for verification against `generate_password_hash` hashes)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Load `app.secret_key` from an environment variable (e.g., `os.environ.get("SECRET_KEY")`), never hardcode a production secret string in `app.py` (use a runtime-generated fallback such as `os.urandom(24)` only when `SECRET_KEY` is unset in local development)
- Keep all SQL queries inside `database/db.py` rather than writing raw SQL in `app.py` or templates
- Normalize `email` with `.strip().lower()` before querying
- Return a generic error message (e.g., `"Invalid email or password."`) for both unknown emails and incorrect passwords to avoid account enumeration
- Never store `password_hash` in `session` or expose it in templates or responses

## Definition of done
- [ ] Running `python app.py` starts without errors and loads `SECRET_KEY` from the environment (with a safe local fallback if unset).
- [ ] `GET /login` returns HTTP 200 and renders the sign-in form with `email` and `password` fields.
- [ ] `POST /login` with the seeded demo credentials (`demo@spendly.com` / `demo123`) authenticates the user, sets `session["user_id"]` and `session["user_name"]`, and redirects to `/`.
- [ ] `POST /login` with an unknown email or wrong password re-renders `login.html` with `.auth-error` showing a generic error message, preserves the entered email, and does not set a session.
- [ ] `POST /login` with empty email or password returns an error message without crashing.
- [ ] When logged in, the navbar in `base.html` displays the user's name and a `Log out` link instead of `Sign in` and `Get started`; visiting `GET /login` while logged in redirects to `/`.
- [ ] `GET /logout` clears the session and redirects to `/login`, after which the navbar reverts to `Sign in` and `Get started`.
- [ ] A `login_required` decorator exists in `app.py` and redirects unauthenticated requests to `/login`.
- [ ] `pytest` passes all tests in `tests/test_auth.py` with zero failures.
