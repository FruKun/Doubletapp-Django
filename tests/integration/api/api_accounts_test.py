from http import HTTPStatus

import pytest
from conftest import AuthorizedClient
from ninja_extra.testing import TestClient

from app.internal.db.models.bank_data import BankAccount
from app.internal.presentation.rest.accounts import Accounts

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def unauthorized_client():
    return TestClient(Accounts)


@pytest.fixture
def client(setup_admin):
    return AuthorizedClient(Accounts)


@pytest.mark.parametrize("path", [(""), ("1")])
def test_api_accounts_get_unauthorized(unauthorized_client, path):
    response = unauthorized_client.get(path=path)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_accounts_post_unauthorized(unauthorized_client):
    response = unauthorized_client.get(path="/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_accounts_get_accounts_ok(setup_db, client):
    response = client.get(path="")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()[0]["number"]) == 20
    assert response.json()[0]["number"].isdigit()


def test_api_accounts_get_account_ok(setup_db, client):
    response = client.get(path="12345678901234567890")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["balance"] == "10000.000"


def test_api_accounts_get_account_not_found(client):
    response = client.get(path="100")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Account does not exist"


def test_api_accounts_post_ok_created(setup_db, client):
    response = client.post(path="", json={"number": "12345678901234567895", "user_id": 10, "balance": 1234})
    BankAccount.objects.get(number=12345678901234567895)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "account created"
    assert response.json()["number"] == "12345678901234567895"


def test_api_accounts_post_ok_exist(setup_db, client):
    response = client.post(path="", json={"number": "12345678901234567890", "user_id": 10, "balance": 1234})
    BankAccount.objects.get(number=12345678901234567890)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "account already exist"
    assert response.json()["number"] == "12345678901234567890"


#
def test_api_accounts_post_not_enough_data(client):
    response = client.post(path="", json={"number": "12345678901234567890", "balance": 1234})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["msg"] == "Field required"


def test_api_accounts_post_not_valid_data(client):
    response = client.post(path="", json={"number": 123})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"


def test_api_accounts_post_no_data(client):
    response = client.post(path="")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["msg"] == "Field required"
