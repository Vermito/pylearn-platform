async def test_login_success(client):
    await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
async def test_login_wrong_password(client):
    await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": "ahmad@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid email or password"
    )
    
async def test_login_user_not_found(client):
    response = await client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 401
    
