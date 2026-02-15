# Pytest configuration and fixtures for PKCE Demo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.pkce_client import User, OAuth2Client
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create demo user
    user = User(
        username="demo",
        email="demo@example.com",
        hashed_password=get_password_hash("demo123"),
        full_name="Demo User"
    )
    db.add(user)

    # Create public client
    client = OAuth2Client(
        client_id="pkce-test-client",
        client_secret=None,
        name="Test PKCE Client",
        redirect_uris="http://localhost:3000/callback",
        scopes="read write",
        is_public=1
    )
    db.add(client)
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture
def pkce_pair():
    """Generate a PKCE pair for testing"""
    from app.utils.pkce_helpers import generate_code_verifier, create_code_challenge
    verifier = generate_code_verifier()
    challenge = create_code_challenge(verifier)
    return verifier, challenge
