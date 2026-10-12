async def test_refresh_token_success(client):
    await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    
    
async def test_access_token_cannot_be_used_as_refresh(
    client,
):
    await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    access_token = login_response.json()["access_token"]

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": access_token
        },
    )

    assert response.status_code == 401