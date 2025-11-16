import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.dependencies import get_db
from app.db.database import Base
from app.db.models import User as UserModel

# 1. In-memory SQLite for fast, isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Fixture to create a fresh database for every test
@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    # Teardown: drop tables after test
    session.close()
    Base.metadata.drop_all(bind=engine)

# 3. Fixture for the TestClient with DB override
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Clear overrides after test
    app.dependency_overrides.clear()

# 4. Fixture to create a standard test user
@pytest.fixture(scope="function")
def test_user(db_session):
    user = UserModel(
        email="test@example.com",
        hashed_password="fake_hashed_password", # This MUST be present and not null
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user