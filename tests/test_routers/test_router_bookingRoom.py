import pytest
from fastapi.testclient import TestClient
from main import app
from firebase_admin import auth

client = TestClient(app)

@pytest.fixture
def cleanup(request):
    # Clean database avec an action was made
    def remove_test_users():
        users = auth.list_users().iterate_all()
        for user in users:
            # Ajoutez votre logique de filtrage pour identifier les utilisateurs de test
            if user.email.startswith("test_"):
                auth.delete_user(user.uid)
    
    # Cleaner after each action
    request.addfinalizer(remove_test_users)

# test with cleanup (good response)
def test_create_account_success(cleanup):
    response = client.post("/auth/signup", json={"email": "test_japhet@example.com", "password": "password123"})
    assert response.status_code == 201
    assert "New user added" in response.json()["message"]
    # @pytest.fixture

# test with cleanup (error response)
def test_create_account_conflict(cleanup):
    response = client.post("/auth/signup", json={"email": "japhet.doe@example.com", "password": "password1234"})
    assert response.status_code == 409  # Not Acceptable

def test_login(cleanup):
    # connection test by creating a new user 
    response_create = client.post("/auth/signup", json={"email": "test_test@example.com", "password": "testpassword"})
    assert response_create.status_code == 201

    # connection test by using an existing user's information 
    response_login = client.post("/auth/login", data={"username": "test_test@example.com", "password": "testpassword"})
    assert response_login.status_code == 200
    assert "access_token" in response_login.json()

def test_login_user_not_exists():
    # connection test with a non existing user 
    response = client.post("/auth/login", data={"username": "utilisateur_inconnu@example.com", "password": "mot_de_passe_incorrect"})
    assert response.status_code == 401
    assert "Invalid Credentials" == response.json()["detail"]
def test_login_missing_username():
    # connection test with missing username
    response = client.post("/auth/login", data={"password": "testpassword"})
    assert response.status_code == 422  # Unprocessable Entity

def test_login_missing_password():
    # connection test with missing password
    response = client.post("/auth/login", data={"username": "test_test@example.com"})
    assert response.status_code == 422  # Unprocessable Entity

def test_login_empty_credentials():
    # connection test with empty credentials
    response = client.post("/auth/login", data={"username": "", "password": ""})
    assert response.status_code == 422  # Unprocessable Entity


@pytest.fixture
def auth_token():
    # connection test with a user's information that was created 
    response_login = client.post("/auth/login", data={"username": "counttest@gmail.com", "counttest": "testpassword"})
    assert response_login.status_code == 200
    assert "access_token" in response_login.json()
    return response_login.json()["access_token"]