import pytest
from app.core.security import verify_password
from app.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_register_creates_user(test_client):
    payload = {
        "email": "analyst@example.com",
        "password": "StrongPassword123!",
        "name": "Jane Analyst",
    }
    response = await test_client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "analyst@example.com"
    assert data["user"]["name"] == "Jane Analyst"


@pytest.mark.asyncio
async def test_password_is_hashed():
    user_repo = UserRepository()
    user = user_repo.create_user(
        email="security@example.com",
        password="MySecretPassword99!",
        name="Security Auditor",
    )
    assert user["hashed_password"] != "MySecretPassword99!"
    assert user["hashed_password"].startswith("$2b$") or user["hashed_password"].startswith("$2a$")
    assert verify_password("MySecretPassword99!", user["hashed_password"]) is True


@pytest.mark.asyncio
async def test_login_returns_valid_token(test_client):
    # Register first
    reg_payload = {
        "email": "login_test@example.com",
        "password": "Password12345!",
        "name": "Test User",
    }
    await test_client.post("/api/auth/register", json=reg_payload)

    # Login
    login_payload = {
        "email": "login_test@example.com",
        "password": "Password12345!",
    }
    response = await test_client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login_test@example.com"


@pytest.mark.asyncio
async def test_protected_endpoint_rejects_unauthenticated(test_client):
    response = await test_client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_accepts_valid_token(test_client):
    # Register to obtain token
    reg_payload = {
        "email": "me_test@example.com",
        "password": "Password12345!",
        "name": "Profile Owner",
    }
    reg_res = await test_client.post("/api/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "me_test@example.com"
    assert user_data["name"] == "Profile Owner"
