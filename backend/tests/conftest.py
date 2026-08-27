import os
import sys
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from tests.mocks.pokeapi_mock import FakePokeAPIClient

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

if not settings.POSTGRES_DB.endswith("_test"):
    sys.exit(
        f"\n❌ CRITICAL SECURITY ERROR:\n"
        f"Attempted to run Pytest pointing to database '{settings.POSTGRES_DB}'.\n"
        f"Tests MUST ONLY be executed against databases ending with '_test'.\n"
        f"Execution canceled to protect your development data.\n"
    )

# 2. If the test database does not exist in the container, Python creates it.
if not database_exists(settings.DATABASE_URL):
    create_database(settings.DATABASE_URL)

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# 1. Create the tables once for the entire pytest run.
@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# 2. Each test opens a transaction and rolls it back when it finishes.
@pytest.fixture(scope="function")
def db(setup_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()  # Discard test data without changing the schema.
    connection.close()


# 4. HTTP client fixture.
@pytest.fixture(scope="function")
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    # Override get_db so FastAPI uses the test database.
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    payload = {
        "email": "auth_user@example.com",
        "username": "authuser",
        "password": "securepassword123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    token = response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
    
@pytest.fixture(autouse=True)
def mock_pokeapi(mocker):
    fake_client = FakePokeAPIClient()
    
    # Replace the real instance imported by the service.
    # Adjust the path if the client is imported from another module.
    mocker.patch("app.services.user_service.poke_api_client", fake_client)
    
    return fake_client