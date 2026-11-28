import os
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")


# ------------------------------------------------------------------ #
# Connection                                                          #
# ------------------------------------------------------------------ #

def get_db():
    """Return a SQLite connection with Row factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ------------------------------------------------------------------ #
# Schema & Seeding                                                    #
# ------------------------------------------------------------------ #

def init_db():
    """Create database tables idempotently using CREATE TABLE IF NOT EXISTS."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert demo user and 8 sample expenses if users table is empty."""
    conn = get_db()
    try:
        existing_user = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if existing_user is not None:
            return

        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        today = date.today()
        sample_expenses = [
            (user_id, 320.0, "Food", today.replace(day=1).isoformat(), "Breakfast and filter coffee"),
            (user_id, 450.0, "Transport", today.replace(day=4).isoformat(), "Metro card recharge"),
            (user_id, 1899.0, "Bills", today.replace(day=7).isoformat(), "Electricity and broadband bill"),
            (user_id, 650.0, "Health", today.replace(day=10).isoformat(), "Pharmacy and vitamins"),
            (user_id, 540.0, "Entertainment", today.replace(day=14).isoformat(), "Weekend movie tickets"),
            (user_id, 2150.0, "Shopping", today.replace(day=17).isoformat(), "Casual shirt and essentials"),
            (user_id, 280.0, "Other", today.replace(day=21).isoformat(), "Courier and stationery"),
            (user_id, 780.0, "Food", today.replace(day=25).isoformat(), "Weekly groceries"),
        ]

        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            sample_expenses,
        )
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# User Queries                                                        #
# ------------------------------------------------------------------ #

def get_user_by_email(email):
    """Return the user row matching a normalized email address, or None."""
    normalized_email = email.strip().lower()
    conn = get_db()
    try:
        return conn.execute(
            """
            SELECT id, name, email, password_hash, created_at
            FROM users
            WHERE LOWER(email) = ?
            """,
            (normalized_email,),
        ).fetchone()
    finally:
        conn.close()


def create_user(name, email, password_hash):
    """Insert a new user record and return the created user ID."""
    clean_name = name.strip()
    normalized_email = email.strip().lower()
    conn = get_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (clean_name, normalized_email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()
