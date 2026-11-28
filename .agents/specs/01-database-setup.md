# Spendly — Step 1: SQLite Database Implementation

## 1. Objective

Replace the existing stub in `database/db.py` with a working SQLite implementation.

This establishes the data layer foundation for Spendly. Future features such as authentication, user profiles, and expense tracking will depend on this implementation.

Read and follow the instructions in `AGENTS.md` before making any changes.

## 2. Depends On

Nothing — this is the first implementation step.

## 3. Routes

- No new routes.
- Existing placeholder routes in `app.py` remain unchanged.

## 4. Files to Modify

Modify only these existing files:

- `database/db.py`
- `app.py`

Do not create any new files.

Do not modify existing routes, frontend files, templates, or unrelated code.

## 5. Database Configuration

Use SQLite with the database file:

`spendly.db`

Store the database in the project root directory.

Use only:

- `sqlite3` from the Python standard library
- `werkzeug.security` for password hashing

No new dependencies are required.

Do not use an ORM or SQLAlchemy.

## 6. Database Schema

### A. users

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | DEFAULT datetime('now') |

### B. expenses

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users.id |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL |
| description | TEXT | Nullable |
| created_at | TEXT | DEFAULT datetime('now') |

Additional requirements:

- Use `ON DELETE CASCADE` for the expense-to-user foreign key.
- The `date` column must store dates in `YYYY-MM-DD` format.
- Use `CREATE TABLE IF NOT EXISTS` for both tables.

## 7. Functions to Implement (`database/db.py`)

### A. `get_db()`

Implement a function that:

- Opens a connection to `spendly.db` in the project root.
- Sets `connection.row_factory = sqlite3.Row`.
- Enables foreign key enforcement using `PRAGMA foreign_keys = ON`.
- Returns the SQLite connection.

Foreign key enforcement must be enabled on every connection.

### B. `init_db()`

Implement a function that:

- Creates both tables using `CREATE TABLE IF NOT EXISTS`.
- Uses the schema defined above.
- Is safe to call multiple times.
- Closes the database connection after initialization.

### C. `seed_db()`

Implement a function that inserts demo data.

Before inserting anything:

- Check whether the `users` table already contains a user.
- If a user already exists, return immediately without inserting anything.

Insert one demo user:

- Name: `Demo User`
- Email: `demo@spendly.com`
- Password: `demo123`

Hash the password using Werkzeug:

    from werkzeug.security import generate_password_hash

Never store the plaintext password in the database.

Insert exactly 8 sample expenses linked to the demo user.

Requirements for the sample expenses:

- Use all 7 fixed categories.
- Include one additional expense in any category.
- Use dates spread across the current month.
- Store dates in `YYYY-MM-DD` format.
- Include realistic amounts and descriptions.
- Ensure every expense belongs to the demo user.

Use parameterized SQL queries for all inserts.

## 8. Changes to `app.py`

Modify `app.py` only as necessary to initialize the database.

Import:

- `get_db`
- `init_db`
- `seed_db`

Inside the existing Flask application setup, call `init_db()` and `seed_db()` within `app.app_context()`.

Ensure the database is initialized before the application starts serving requests.

Preserve all existing placeholder routes and application behavior.

## 9. Fixed Expense Categories

Use exactly these category values:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

Do not introduce additional categories.

## 10. Security and Implementation Rules

- Use parameterized SQL queries exclusively.
- Never use string formatting or string concatenation to construct SQL queries.
- Enable `PRAGMA foreign_keys = ON` on every database connection.
- Store expense amounts using SQLite `REAL`.
- Hash passwords using Werkzeug.
- Do not expose password hashes through routes or responses.
- Do not introduce unnecessary abstractions or dependencies.
- Follow the existing project structure and coding style.
- Keep the implementation simple and beginner-friendly.
- Do not modify unrelated files.

## 11. Expected Behavior

After implementation:

- Starting the Flask application creates `spendly.db` automatically.
- Both tables are created with the correct schema.
- The demo user exists with a hashed password.
- Exactly 8 demo expenses exist.
- All 7 categories are represented.
- Running initialization repeatedly does not duplicate seed data.
- Duplicate emails are rejected by SQLite.
- Expenses with invalid user IDs are rejected by SQLite.
- Foreign key enforcement works correctly.

## 12. Verification

After implementing the changes:

1. Check that the application starts without errors.
2. Verify that both tables exist.
3. Verify that the demo user's password is hashed.
4. Verify that exactly 8 sample expenses exist.
5. Verify that all 7 categories are represented.
6. Run initialization and seeding again to confirm no duplicate records are created.
7. Verify that foreign key enforcement works.
8. Confirm that all SQL queries use parameterized statements.

Do not claim that a test passed unless you actually ran it.

## 13. Definition of Done

The implementation is complete when:

- [ ] The database is created on app startup.
- [ ] Both tables have the correct schema and constraints.
- [ ] Demo data is inserted correctly.
- [ ] Repeated initialization does not duplicate data.
- [ ] Foreign key enforcement works.
- [ ] All SQL queries are parameterized.
- [ ] Existing routes remain unchanged.
- [ ] Only `database/db.py` and `app.py` have been modified.

Before finishing, provide a concise summary of the changes and the verification results.