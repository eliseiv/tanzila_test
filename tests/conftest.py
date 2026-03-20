import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.database as db_module
from app.database import Base, get_db
from app.models import Message

TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

_original_engine = db_module.engine
_original_session = db_module.SessionLocal


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    db_module.engine = test_engine
    db_module.SessionLocal = TestSessionLocal

    Base.metadata.create_all(bind=test_engine)

    db = TestSessionLocal()
    if db.query(Message).count() == 0:
        for i in range(1, 13):
            db.add(Message(id=i, text=f"Test message {i}"))
        db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    db_module.engine = _original_engine
    db_module.SessionLocal = _original_session


@pytest.fixture()
def client():
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
