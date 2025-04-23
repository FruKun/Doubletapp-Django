from http import HTTPStatus

import pytest
from conftest import AuthorizedClient
from ninja_extra.testing import TestClient

from app.internal.db.models.user_data import TelegramUser
from app.internal.presentation.rest.users import Users

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def unauthorized_client():
    return TestClient(Users)


@pytest.fixture
def client(setup_admin):
    return AuthorizedClient(Users)


@pytest.mark.parametrize("path", [("/"), ("/1")])
def test_api_users_get_unauthorized(unauthorized_client, path):
    response = unauthorized_client.get(path=path)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_users_post_unauthorized(unauthorized_client):
    response = unauthorized_client.get(path="/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_users_put_unauthorized(unauthorized_client):
    response = unauthorized_client.get(path="/1")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_users_delete_unauthorized(unauthorized_client):
    response = unauthorized_client.get(path="/1")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_users_get_users_ok(setup_user, client):
    response = client.get(path="")
    assert response.status_code == HTTPStatus.OK
    assert response.json()[0]["username"] == "test100"
    assert response.json()[1]["full_name"] == "test wphone"


def test_api_users_get_user_ok(setup_user, client):
    response = client.get(path="100")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["username"] == "test100"


def test_api_users_get_user_not_found(client):
    response = client.get(path="/100")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_api_users_get_user_not_valid_data(client):
    response = client.get(path="/aboba")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_users_post_ok_created(client):
    response = client.post(path="", json={"id": 1, "username": "test", "full_name": "test"})
    TelegramUser.objects.get(id=1)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "user created"
    assert response.json()["username"] == "test"


def test_api_users_post_ok_exist(setup_user, client):
    response = client.post(path="", json={"id": 100, "username": "test", "full_name": "test"})
    TelegramUser.objects.get(id=100)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "user already exist"
    assert response.json()["username"] == "test100"


def test_api_users_post_not_enough_data(client):
    response = client.post(path="", json={"id": 1, "username": "test"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "db error"


def test_api_users_post_not_valid_data(client):
    response = client.post(path="", json={"id": "aboba"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_users_post_no_data(client):
    response = client.post(path="")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_users_put_ok_created(client):
    response = client.put(path="1", json={"username": "test", "full_name": "test"})
    TelegramUser.objects.get(id=1)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "user created"
    assert response.json()["username"] == "test"


def test_api_users_put_ok_updated(setup_user, client):
    response = client.put(path="100", json={"username": "test", "full_name": "test"})
    TelegramUser.objects.get(id=100)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "user updated"
    assert response.json()["username"] == "test"


def test_api_users_put_not_enough_data(client):
    response = client.put(path="1", json={"username": "test"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "db error"


def test_api_users_put_not_valid_data(client):
    response = client.put(path="aboba")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_users_put_no_data(client):
    response = client.put(path="1")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_users_delete_ok(setup_user, client):
    response = client.delete(path="100")
    with pytest.raises(TelegramUser.DoesNotExist):
        TelegramUser.objects.get(id=100)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "user 100 deleted"


def test_api_users_delete_not_valid_data(client):
    response = client.delete(path="aboba")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_users_delete_no_user(client):
    response = client.delete(path="100")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User does not exist"
