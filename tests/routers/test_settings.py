import pytest
from app.main import app
from app.service.auth.dependencies import get_current_user_or_api_key
from app.db.models import UserSettings

# --- Authentication Override Helper ---
# This tells FastAPI: "Whenever an endpoint asks for 'get_current_user_or_api_key',
# just give it this specific 'user' object instead."
def mock_auth_dependency(user):
    def override():
        return user
    return override

# --- Tests ---

def test_create_settings_success(client, test_user):
    # Arrange: Override auth to use our test_user
    app.dependency_overrides[get_current_user_or_api_key] = mock_auth_dependency(test_user)
    
    payload = {
        "native_language_code": "en",
        "target_language_code": "es"
    }

    # Act: POST to create
    response = client.post("/api/settings/", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["user_email"] == test_user.email
    assert data["native_language_code"] == "en"
    assert data["target_language_code"] == "es"

def test_read_settings_success(client, test_user, db_session):
    # Arrange: Auth override AND pre-seed the DB with settings
    app.dependency_overrides[get_current_user_or_api_key] = mock_auth_dependency(test_user)
    
    settings = UserSettings(
        user_id=test_user.id,
        native_language_code="fr",
        target_language_code="de"
    )
    db_session.add(settings)
    db_session.commit()

    # Act: GET the settings
    response = client.get("/api/settings/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["native_language_code"] == "fr"
    assert data["target_language_code"] == "de"

def test_read_settings_not_found(client, test_user):
    # Arrange: Auth override, but DO NOT seed any settings
    app.dependency_overrides[get_current_user_or_api_key] = mock_auth_dependency(test_user)

    # Act
    response = client.get("/api/settings/")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "User settings not found. Please create them first."

def test_update_settings_success(client, test_user, db_session):
    # Arrange: Seed initial settings
    app.dependency_overrides[get_current_user_or_api_key] = mock_auth_dependency(test_user)
    initial_settings = UserSettings(
        user_id=test_user.id,
        native_language_code="en",
        target_language_code="es"
    )
    db_session.add(initial_settings)
    db_session.commit()

    # Act: POST new settings to update
    update_payload = {
        "native_language_code": "en",
        "target_language_code": "jp" # Changed target to Japanese
    }
    response = client.post("/api/settings/", json=update_payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["target_language_code"] == "jp"

def test_unauthenticated_access_fails(client):
    # Arrange: Ensure NO auth overrides are active for this test
    app.dependency_overrides.pop(get_current_user_or_api_key, None)

    # Act
    response = client.get("/api/settings/")

    # Assert
    # Assuming your actual auth dependency returns 401 or 403 when missing credentials
    assert response.status_code in [401, 403]