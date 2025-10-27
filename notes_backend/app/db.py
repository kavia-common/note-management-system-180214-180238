import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance (initialized in init_db)
db = SQLAlchemy()


def get_database_uri() -> str:
    """
    Resolve the database URI from environment variable or use default sqlite.
    """
    # Prefer DATABASE_URL if present, else default to sqlite file in container
    return os.getenv("DATABASE_URL", "sqlite:///notes.db")


# PUBLIC_INTERFACE
def init_db(app: Flask) -> None:
    """Initialize database bindings for the Flask app.

    Binds SQLAlchemy to the app and creates tables if they do not exist.

    Notes:
    - Uses DATABASE_URL env var if provided; otherwise defaults to sqlite:///notes.db.
    - Does not run migrations; if Flask-Migrate is added later, it will work with this setup.
    """
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", get_database_uri())
    # Avoid tracking modifications overhead
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)

    # Create tables on first run (safe no-op if already present)
    with app.app_context():
        db.create_all()
