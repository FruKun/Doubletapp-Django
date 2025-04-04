import pytest

from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser

pytestmark = pytest.mark.smoke


def test_admin_page(client):
    response = client.get("/admin/")
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_db_connection(setup_db):
    assert "test10" == TelegramUser.objects.get(id=10).username
    assert "12345678901234567890" == BankAccount.objects.get(number="12345678901234567890").number
    assert "1234567890123456" == BankCard.objects.get(number="1234567890123456").number
