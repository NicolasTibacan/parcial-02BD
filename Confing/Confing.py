import os
import sqlite3
from sqlite3 import Connection
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "etl_data.db")
SQLITE_URL = f"sqlite:///{DB_FILE}"

def get_engine() -> Engine:
    """Devuelve un SQLAlchemy Engine apuntando al archivo SQLite."""
    return create_engine(SQLITE_URL, future=True)

def get_sqlite_connection() -> Connection:
    """Devuelve una conexión sqlite3 tradicional (si es necesaria)."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db: Engine | Connection):
    """Crea la tabla 'sentiments' si no existe. Acepta Engine (recomendado) o sqlite3.Connection."""
    ddl = """
    CREATE TABLE IF NOT EXISTS sentiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        ticker TEXT,
        text_original TEXT,
        cleaned_text TEXT,
        sentiment_label TEXT,
        sentiment_score REAL
    );
    """
    # Si es un Engine de SQLAlchemy
    if hasattr(db, "begin") and not isinstance(db, sqlite3.Connection):
        with db.begin() as conn:
            conn.execute(text(ddl))
    else:
        # sqlite3 connection
        cur = db.cursor()
        cur.execute(ddl)
        db.commit()
