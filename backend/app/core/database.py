import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    # Normalize path for SQLite on Windows & POSIX
    if db_url.startswith("sqlite:///."):
        rel_subpath = db_url.replace("sqlite:///.", "").lstrip("/\\")
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", rel_subpath))
        abs_path = abs_path.replace("\\", "/")
        db_url = f"sqlite:///{abs_path}"
    elif db_url.startswith("sqlite:///") and not os.path.isabs(db_url.replace("sqlite:///", "")):
        rel_subpath = db_url.replace("sqlite:///", "")
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", rel_subpath))
        abs_path = abs_path.replace("\\", "/")
        db_url = f"sqlite:///{abs_path}"
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    db_url, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_database_schema(target_engine=None):
    """Automatically add missing columns to existing SQLite tables when models evolve."""
    if target_engine is None:
        target_engine = engine
    from sqlalchemy import inspect, text
    inspector = inspect(target_engine)
    with target_engine.begin() as conn:
        for table_name, table in Base.metadata.tables.items():
            if inspector.has_table(table_name):
                existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
                for col in table.columns:
                    if col.name not in existing_cols:
                        col_type = col.type.compile(target_engine.dialect)
                        default_val = None
                        if col.default is not None and hasattr(col.default, 'arg') and not callable(col.default.arg):
                            default_val = col.default.arg
                            if isinstance(default_val, bool):
                                default_val = 1 if default_val else 0
                            elif isinstance(default_val, str):
                                default_val = f"'{default_val}'"
                        default_clause = f" DEFAULT {default_val}" if default_val is not None else ""
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type}{default_clause}"
                        conn.execute(text(sql))

