from unittest.mock import AsyncMock

import pytest
from django.test import Client

from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser


@pytest.fixture
def setup_db():
    user = TelegramUser.objects.create(
        id=10,
        username="test10",
        full_name="test user",
        phone_number="+78005553501",
        list_of_favourites=[
            "test11",
            "12345678901234567891",
            "12345678901234567892",
            "1234567890123450",
            "1234567890123458",
        ],
    )
    account = BankAccount.objects.create(number="12345678901234567890", balance=10000, user=user)
    BankCard.objects.create(number="1234567890123456", account=account, expiration_date="2024-02-02", cvv="123")
    BankCard.objects.create(number="1234567890123457", account=account, expiration_date="2024-02-02", cvv="123")
    account = BankAccount.objects.create(number="12345678901234567891", balance=10000, user=user)
    BankCard.objects.create(number="1234567890123458", account=account, expiration_date="2024-02-02", cvv="123")
    BankCard.objects.create(number="1234567890123459", account=account, expiration_date="2024-02-02", cvv="123")
    user = TelegramUser.objects.create(
        id=11, username="test11", full_name="test user", phone_number="+78005553502", list_of_favourites=[]
    )
    account = BankAccount.objects.create(number="12345678901234567892", balance=10000, user=user)
    BankCard.objects.create(number="1234567890123450", account=account, expiration_date="2024-02-02", cvv="123")


@pytest.fixture
def setup_user():
    TelegramUser.objects.create(
        id=100, username="test100", full_name="test wphone", phone_number="8 (800) 555-35-45", list_of_favourites=[]
    )
    TelegramUser.objects.create(id=200, username="test200", full_name="test wphone", list_of_favourites=[])


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def update():
    update = AsyncMock()
    update.message = AsyncMock()
    update.message.from_user = AsyncMock()

    update.message.from_user.language_code = "RU"
    return update


@pytest.fixture
def context():
    context = AsyncMock()
    context.args = []
    return context
