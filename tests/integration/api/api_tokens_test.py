from http import HTTPStatus

import pytest
from freezegun import freeze_time
from ninja_extra.testing import TestClient
from ninja_jwt.tokens import RefreshToken

from app.internal.db.models.user_data import TelegramUser
from app.internal.presentation.rest.tokens import Tokens

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def client():
    return TestClient(Tokens)


def test_api_tokens_login(setup_user, client):
    response = client.post(path="/login/", json={"id": 100})
    print(response.json())
    assert response.status_code == HTTPStatus.OK
    assert "access" in response.json()
    assert "refresh" in response.json()


def test_api_tokens_login_not_found(client):
    response = client.post(path="/login/", json={"id": 100})
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_api_tokens_login_not_valid_data(client):
    response = client.post("/login/", json={"id": "aboba"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_tokens_login_no_data(client):
    response = client.post("/login/")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_tokens_login_not_valid_method(client):
    response = client.get("/login/")
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_api_tokens_refresh_ok(setup_user, client):
    user = TelegramUser.objects.get(id="100")
    refresh = RefreshToken.for_user(user)
    response = client.post("/refresh/", json={"refresh": str(refresh)})
    assert response.status_code == HTTPStatus.OK
    assert "access" in response.json()


def test_api_tokens_refresh_not_valid_data(client):
    response = client.post("/refresh/", json={"refresh": "refresh"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_tokens_refresh_no_refresh(client):
    response = client.post("/refresh/", json={"refresh": ""})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_api_tokens_refresh_no_data(client):
    response = client.post("/refresh/")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_tokens_refresh_expired(setup_user, client):
    with freeze_time("2025-01-01 12:00:00"):
        user = TelegramUser.objects.get(id="100")
        refresh = RefreshToken.for_user(user)
        response = client.post("/refresh/", json={"refresh": str(refresh)})
        print(response.json())
    with freeze_time("2025-03-01 12:00:00"):
        response = client.post("/refresh/", json={"refresh": str(refresh)})
        print(response.json())
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_api_tokens_refresh_not_valid_method(client):
    response = client.get("/refresh/")
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
