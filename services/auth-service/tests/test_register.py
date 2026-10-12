async def test_register_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "ahmad"
    assert data["email"] == "ahmad@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True

    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data
    
async def test_register_invalid_email(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "not-an-email",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 422

async def test_register_short_password(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "ahmad@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422
    
async def test_register_duplicate_email(client):
    user = {
        "username": "ahmad",
        "email": "ahmad@example.com",
        "password": "StrongPassword123",
    }

    first_response = await client.post(
        "/auth/register",
        json=user,
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/auth/register",
        json={
            "username": "another_user",
            "email": "ahmad@example.com",
            "password": "AnotherPassword123",
        },
    )

    assert second_response.status_code == 409
    
async def test_register_duplicate_username(client):
    first_response = await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "ahmad@example.com",
            "password": "StrongPassword123",
        },
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/auth/register",
        json={
            "username": "ahmad",
            "email": "another@example.com",
            "password": "AnotherPassword123",
        },
    )

    assert second_response.status_code == 409