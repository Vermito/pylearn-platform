async def test_get_me_without_token(client):
    response = await client.get("/users/me")

    assert response.status_code in (401, 403)
    
async def test_get_me_with_token(client):
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

    response = await client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "ahmad"
    assert data["email"] == "ahmad@example.com"
    
