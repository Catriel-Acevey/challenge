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

# 2. Si la DB de test no existe en el contenedor, Python la crea sola
if not database_exists(settings.DATABASE_URL):
    create_database(settings.DATABASE_URL)

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# 3. Fixture de Base de Datos
# @pytest.fixture(scope="module")
# def db():
#     # Crea las tablas en challenge_db_test
#     Base.metadata.create_all(bind=engine)

#     connection = engine.connect()
#     transaction = connection.begin()
#     session = TestingSessionLocal(bind=connection)

#     yield session  # Entrega la sesión a los tests

#     session.close()
#     transaction.rollback()
#     connection.close()
#     # Limpia las tablas al terminar la suite de tests
#     Base.metadata.drop_all(bind=engine)

# 1. Las tablas se crean UNA sola vez para toda la ejecución de pytest
@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# 2. Cada test abre una transacción y hace rollback al terminar (vacío instantáneo)
@pytest.fixture(scope="function")
def db(setup_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback() # 👈 Desecha todo lo creado en el test sin tocar la estructura
    connection.close()


# 4. Fixture del Cliente HTTP (Acá se define 'client')
@pytest.fixture(scope="function")
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    # Interceptamos get_db para que use la DB de prueba en FastAPI
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    
@pytest.fixture(autouse=True)
def mock_pokeapi(mocker):
    fake_client = FakePokeAPIClient()
    
    # Reemplaza la instancia real importada en tu service
    # (Asegurate de ajustar la ruta al módulo exacto donde importás poke_api_client)
    mocker.patch("app.services.user_service.poke_api_client", fake_client)
    
    return fake_client