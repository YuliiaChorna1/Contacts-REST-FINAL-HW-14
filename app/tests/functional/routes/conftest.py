import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.src.database.models import Base
from app.src.database.db import get_db
from app.main import app
from src.conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool", "email": "deadpool@example.com", "password": "123456789"}
