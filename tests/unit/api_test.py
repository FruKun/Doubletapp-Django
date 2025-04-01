import pytest


@pytest.mark.django_db
def test_api(client):
    from app.internal.models.user_data import TelegramUser

    TelegramUser.objects.create(
        id=2, full_name="test user", username="test2", phone_number="+78005553531", list_of_favourites=[]
    )
    response = client.get("/api/get_user", {"user_id": "2"})
    assert response.status_code == 200
    response = client.get("/api/get_user", {"user_id": "666666666666"})
    assert response.status_code == 404
    response = client.get("/api/get_user", {"user_id": ""})
    assert response.status_code == 400
