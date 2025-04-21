from datetime import timedelta
from http import HTTPStatus

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from app.internal.models.user_data import TelegramUser
from app.internal.serializers import CustomTokenObtainPairSerializer

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]
client = APIClient()


def test_api_login(setup_user):
    response = client.post("/api/login/", {"id": "100"}, format="json")
    assert response.status_code == HTTPStatus.OK
    assert "access" in response.json()
    assert "refresh" in response.json()


def test_api_login_not_found():
    response = client.post("/api/login/", {"id": "100"}, format="json")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_api_login_not_valid_data():
    response = client.post("/api/login/")
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_api_login_not_valid_method():
    response = client.get("/api/login/")
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_api_unauthorized():
    response = client.get("/api/get_user")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_get_user_ok(setup_user):
    user = TelegramUser.objects.get(id="100")
    refresh = CustomTokenObtainPairSerializer.get_token(user)
    response = client.get("/api/get_user", {"user_id": "100"}, HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["username"] == "test100"


def test_api_get_user_not_found(setup_user):
    user = TelegramUser.objects.get(id="100")
    refresh = CustomTokenObtainPairSerializer.get_token(user)
    response = client.get(
        "/api/get_user", {"user_id": "1234"}, HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["error"] == "User does not exist"


def test_api_get_user_bad_request(setup_user):
    user = TelegramUser.objects.get(id="100")
    refresh = CustomTokenObtainPairSerializer.get_token(user)
    response = client.get("/api/get_user", {"user_id": ""}, HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["error"] == "Dont have user_id"


def test_api_get_user_expired(setup_user):
    with freeze_time("2025-01-01 12:00:00"):
        user = TelegramUser.objects.get(id="100")
        refresh = CustomTokenObtainPairSerializer.get_token(user)
    with freeze_time("2025-01-01 14:00:00"):
        response = client.get(
            "/api/get_user", {"user_id": "100"}, HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_token_refresh_ok(setup_user):
    user = TelegramUser.objects.get(id="100")
    refresh = CustomTokenObtainPairSerializer.get_token(user)
    response = client.post("/api/token/refresh/", {"refresh": str(refresh)}, format="json")
    assert response.status_code == HTTPStatus.OK
    assert "access" in response.json()


def test_api_token_refresh_expired(setup_user):
    with freeze_time("2025-01-01 12:00:00"):
        user = TelegramUser.objects.get(id="100")
        refresh = CustomTokenObtainPairSerializer.get_token(user)
    with freeze_time("2025-03-01 12:00:00"):
        response = client.post("/api/token/refresh/", {"refresh": str(refresh)}, format="json")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
