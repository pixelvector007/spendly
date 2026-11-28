# Spec: Registration

## Overview
This feature implements user account registration on `GET /register` and `POST /register`, allowing new visitors to create a Spendly account using their full name, email address, and password. It validates form input, enforces unique email addresses, hashes passwords securely with Werkzeug, persists the new user to SQLite, and redirects to `/login`. It builds directly on Step 1's SQLite schema (`users` table) so real users can be created before Step 3 introduces login, logout, and session management.

## Depends on
- Step 1: Database Setup (`.agents/specs/01-database-setup.md`) — requires `get_db()`, `init_db()`, and the `users` table in `database/db.py`.

## Routes
- `GET /register` — render the registration form (`templates/register.html`) — public (existing route, update to accept `GET` and `POST`)
- `POST /register` — validate `name`, `email`, and `password`, create a new user in `users`, and redirect to `/login` on success or re-render `templates/register.html` with `error` on failure — public

## Database changes
No database changes.

Verified against `database/db.py`: the `users` table already defines `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`), `name` (`TEXT NOT NULL`), `email` (`TEXT UNIQUE NOT NULL`), `password_hash` (`TEXT NOT NULL`), and `created_at` (`TEXT DEFAULT (datetime('now'))`). Add helper functions in `database/db.py` (for example `get_user_by_email` and `create_user`) to keep SQL queries out of `app.py`.

## Templates
- **Create:** None
- **Modify:** `templates/register.html` — preserve submitted `name` and `email` values in the form inputs when re-rendering after a validation error (never pre-fill `password`), while keeping error display via `.auth-error` and the `error` context variable.

## Files to change
- `app.py` — update `/register` to accept `GET` and `POST`, validate `name`, `email` (normalized with `.strip().lower()`), and `password` (minimum 8 characters), hash passwords with `generate_password_hash`, handle duplicate email registration gracefully, and redirect to `url_for('login')` on success.
- `database/db.py` — add parameterized helper functions for looking up a user by email and inserting a new user row.
- `templates/register.html` — add `value` attributes for `name` and `email` so user input is preserved when validation fails.

## Files to create
- `tests/test_registration.py` — automated tests for `GET /register` and `POST /register` validation, hashing, duplicate email handling, and redirect behavior.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Keep all database queries inside `database/db.py` rather than writing raw SQL in `app.py`
- Normalize email addresses (`.strip().lower()`) before lookup and insertion, and catch `sqlite3.IntegrityError` so duplicate emails return a friendly `error` message instead of a 500 error
- Validate required fields (`name`, `email`, `password`) server-side, including a minimum password length of 8 characters matching the placeholder in `templates/register.html`
- Never store plaintext passwords or expose `password_hash` in responses or templates

## Definition of done
- [ ] Visiting `GET /register` in the running app renders the registration form (`name`, `email`, `password`) extending `base.html`.
- [ ] Submitting `POST /register` with a valid name, unused email, and password of at least 8 characters creates a row in `users` in `spendly.db` with a Werkzeug-hashed `password_hash` and redirects to `/login`.
- [ ] Submitting `POST /register` with blank fields, an invalid email, or a password shorter than 8 characters does not insert a user and renders `.auth-error` with an informative error message.
- [ ] Submitting `POST /register` with an already registered email (such as `demo@spendly.com` or different casing like `DEMO@spendly.com`) does not insert a duplicate user and renders `.auth-error` with an informative error message.
- [ ] Previously entered `name` and `email` remain filled in on `templates/register.html` when validation fails, while `password` stays empty.
- [ ] Running `pytest` passes all tests in `tests/test_registration.py`.
