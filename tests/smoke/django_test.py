import pytest

from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser


def test_admin_page(client):
    response = client.get("/admin/")
    assert response.status_code == 302


@pytest.mark.django_db
def test_db_connection():
    user = TelegramUser.objects.create(
        id=1, full_name="test user", username="test", phone_number="+78005553530", list_of_favourites=["100", "test100"]
    )
    account = BankAccount.objects.create(number="92345678901234567890", balance=10000, user=user)
    BankCard.objects.create(number="9234567890123456", account=account, expiration_date="2020-05-15", cvv="123")
    assert "test" == TelegramUser.objects.get(id=1).username
    assert "92345678901234567890" == BankAccount.objects.get(user__username="test").number
    assert "9234567890123456" == BankCard.objects.get(account__number="92345678901234567890").number
