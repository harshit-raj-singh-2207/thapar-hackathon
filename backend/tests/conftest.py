import pytest
from app.core.database import Base, engine, SessionLocal, sync_database_schema
from app.main import startup_event

@pytest.fixture(scope="session", autouse=True)
def init_schema():
    Base.metadata.create_all(bind=engine)
    sync_database_schema(engine)

@pytest.fixture(autouse=True)
def reset_db_data():
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    startup_event()

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


