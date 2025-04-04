from http import HTTPStatus

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_api_ok(client, setup_db):
    response = client.get("/api/get_user", {"user_id": "10"})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["username"] == "test10"


@pytest.mark.django_db
def test_api_not_found(client):
    response = client.get("/api/get_user", {"user_id": "666666666666"})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["error"] == "User does not exist"


@pytest.mark.django_db
def test_api_bad_request(client):
    response = client.get("/api/get_user", {"user_id": ""})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["error"] == "Dont have user_id"
