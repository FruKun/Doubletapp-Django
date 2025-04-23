from http import HTTPStatus

import pytest
from conftest import AuthorizedClient
from ninja_extra.testing import TestClient

from app.internal.presentation.rest.cards import Cards

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def unauthorized_client():
    return TestClient(Cards)


@pytest.fixture
def client(setup_admin):
    return AuthorizedClient(Cards)


@pytest.mark.parametrize("path", [("/"), ("/1")])
def test_api_cards_get_unauthorized(unauthorized_client, path):
    response = unauthorized_client.get(path=path)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_cards_get_cards_ok(setup_db, client):
    response = client.get(path="")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()[0]["number"]) == 16
    assert response.json()[0]["number"].isdigit()


def test_api_cards_get_card_ok(setup_db, client):
    response = client.get(path="1234567890123456")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["number"] == "1234567890123456"


def test_api_cards_get_card_not_found(client):
    response = client.get(path="1234567890123456")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_api_cards_get_card_not_valid_data(client):
    response = client.get(path="/aboba")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
