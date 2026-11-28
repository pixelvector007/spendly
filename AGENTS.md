# AGENTS.md

Guidance for coding agents working in the **Spendly** (`expense-tracker`) repository.

## Project Overview

**Spendly** is a personal expense tracking web application (styled for INR / `₹` currency) built with Python, Flask, Jinja2 templates, SQLite, and vanilla CSS/JavaScript.

The repository is currently in an early incremental build state: the landing page, auth UI templates, legal pages, and route stubs are in place, while database setup (`database/db.py`), authentication logic, and expense CRUD routes are scaffolded for upcoming implementation steps.

---

## Tech Stack

- **Runtime:** Python 3.12 (`.venv` in the project root)
- **Web Framework:** Flask `3.1.3` (Werkzeug `3.1.6`)
- **Templating:** Jinja2 (server-rendered HTML via Flask)
- **Database:** SQLite (`sqlite3` standard library; local database file `expense_tracker.db` is gitignored)
- **Frontend:** Vanilla HTML5, CSS3 (`static/css/style.css`, `static/css/landing.css`), and vanilla JavaScript (`static/js/main.js` + page-scoped inline scripts)
- **Typography:** Google Fonts (`DM Serif Display`, `DM Sans`, and `Plus Jakarta Sans` on the landing page) loaded via CDN
- **Testing:** `pytest==8.3.5` and `pytest-flask==1.3.0`

---

## Architecture & Directory Structure

```text
expense-tracker/
├── app.py                  # Flask app instance, route definitions, dev server entrypoint (port 5001)
├── requirements.txt        # Pinned Python dependencies (Flask, Werkzeug, pytest, pytest-flask)
├── .gitignore              # Ignores venv/, expense_tracker.db, __pycache__/, *.pyc, .env, .DS_Store, .claude/plans/
├── database/
│   ├── __init__.py         # Package marker (currently empty)
│   └── db.py               # Database module stub (Step 1: get_db, init_db, seed_db)
├── static/
│   ├── css/
│   │   ├── style.css       # Global design tokens, layout, navbar, footer, auth, legal, and shared styles
│   │   └── landing.css     # Landing page hero, dashboard mockup, and video modal overrides
│   └── js/
│       └── main.js         # Shared client-side JS entry point (currently a stub)
└── templates/
    ├── base.html           # Base layout (navbar, main container, footer, global CSS/JS, template blocks)
    ├── landing.html        # Marketing landing page + "How Spendly works" video modal script
    ├── login.html          # Sign-in form (POST /login)
    ├── register.html       # Registration form (POST /register)
    ├── terms.html          # Terms and Conditions page
    └── privacy.html        # Privacy Policy page
```

### Routing (`app.py`)

- **Implemented page routes:**
  - `GET /` → `landing` (`templates/landing.html`)
  - `GET /register` → `register` (`templates/register.html`)
  - `GET /login` → `login` (`templates/login.html`)
  - `GET /terms` → `terms` (`templates/terms.html`)
  - `GET /privacy` → `privacy` (`templates/privacy.html`)
- **Placeholder routes (pending implementation):**
  - `/logout` (Step 3)
  - `/profile` (Step 4)
  - `/expenses/add` (Step 7)
  - `/expenses/<int:id>/edit` (Step 8)
  - `/expenses/<int:id>/delete` (Step 9)

### Database Design (`database/db.py`)

`database/db.py` is designated to contain all SQLite setup and connection logic:
- `get_db()` — return a `sqlite3.Connection` with `row_factory` set (e.g., `sqlite3.Row`) and foreign keys enabled (`PRAGMA foreign_keys = ON`).
- `init_db()` — create all tables idempotently using `CREATE TABLE IF NOT EXISTS`.
- `seed_db()` — insert sample data for local development.

---

## Coding Conventions

### Python & Flask
- Use `snake_case` for functions, variables, and route handler names.
- Keep section divider comments consistent with the existing `# ------------------------------------------------------------------ #` style in `app.py`.
- Route handlers should keep database queries inside `database/db.py` (or dedicated database helpers) rather than scattering raw SQL setup across templates or inline strings.
- Auth templates (`login.html`, `register.html`) expect:
  - `POST /login` with form fields `email` and `password`.
  - `POST /register` with form fields `name`, `email`, and `password`.
  - Validation/auth errors passed back to the template via the `error` context variable (rendered inside `.auth-error`).

### Templates (Jinja2)
- All pages extend `base.html` (`{% extends "base.html" %}`).
- Available blocks in `base.html`: `title`, `head`, `content`, `scripts`.
- Use `url_for('static', filename=...)` for static assets and prefer `url_for('<route_fn>')` for internal links.
- Keep page-specific CSS in `{% block head %}` and page-specific JS in `{% block scripts %}`.

### CSS
- Reuse the design tokens defined in `:root` in `static/css/style.css` (`--ink`, `--ink-soft`, `--ink-muted`, `--ink-faint`, `--paper`, `--paper-warm`, `--paper-card`, `--accent`, `--accent-light`, `--accent-2`, `--danger`, `--border`, `--font-display`, `--font-body`, `--radius-sm`, `--radius-md`, `--radius-lg`, `--max-width`, `--auth-width`).
- Organize stylesheets into clearly labeled sections using `/* ------------------------------------------------------------------ */` headers.
- Place page-specific overrides in separate stylesheets (like `static/css/landing.css`) loaded via `{% block head %}` instead of overloading `style.css`.
- Use kebab-case class names and `.is-*` state modifier classes (e.g., `.is-open`, `.is-up`, `.is-good`, `.is-neutral`).

### JavaScript
- No frontend build tools or frameworks are used; write clean, ES6+ vanilla JavaScript.
- Wrap page-specific inline scripts in an IIFE (`(function () { ... })();`) and guard DOM queries before attaching event listeners.
- Put reusable/global behaviors in `static/js/main.js`.

### Git Commits
- Follow the existing `<scope>: <imperative description>` commit message pattern (for example: `landing: add youtube modal on see how it works click`).

---

## Development Instructions

### 1. Environment Setup

Use the existing virtual environment (`.venv`) or create one and install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Running the Development Server

```bash
python app.py
```

- Runs Flask in debug mode on **port `5001`** (`http://127.0.0.1:5001`) to avoid macOS AirPlay Receiver conflicts on port `5000`.

### 3. Running Tests

`pytest` and `pytest-flask` are included in `requirements.txt`. Once tests are added (e.g., under `tests/`), run:

```bash
pytest
```

### 4. Important Guardrails
- **Do not commit** `expense_tracker.db`, `.env`, or `.venv/`/`.pyc` artifacts.
- When implementing Flask sessions or authentication, load secrets (such as `app.secret_key`) from environment variables rather than hardcoding them in `app.py`.
- Keep SQLite foreign keys enabled (`PRAGMA foreign_keys = ON`) on every database connection returned by `get_db()`.
