async def test_user_cannot_access_admin_users(client):
    await client.post(
        "/auth/register",
        json={
            "username": "student",
            "email": "student@example.com",
            "password": "StudentPassword123",
        },
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "student@example.com",
            "password": "StudentPassword123",
        },
    )

    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/admin/users",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 403
    
async def test_admin_can_access_users(
    client,
    admin_token,
):
    response = await client.get(
        "/admin/users",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1