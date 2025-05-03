from decimal import Decimal
from typing import Optional

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.user_data import TelegramUser
from app.internal.db.repositories.account_repository import AccountRepository
from app.internal.db.repositories.transaction_repository import TransactionHistoryRepository
from app.internal.db.repositories.user_repository import UserRepository
from app.internal.domain.services import CustomErrors


class AccountService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionHistoryRepository()

    def get_account_by_card_number(self, number: str) -> BankAccount:
        if account := self.account_repo.get_account_by_card_number(number):
            return account
        raise BankAccount.DoesNotExist

    def get_account_by_number(self, number: str) -> BankAccount:
        if account := self.account_repo.get_account_by_number(number):
            return account
        raise BankAccount.DoesNotExist

    def get_account_by_user_id(self, id: int) -> BankAccount:
        if account := self.account_repo.get_account_by_user_id(id):
            return account
        raise BankAccount.DoesNotExist

    def get_account_by_user_username(self, username: str) -> BankAccount:
        if account := self.account_repo.get_account_by_user_username(username):
            return account
        raise BankAccount.DoesNotExist

    async def aget_accounts_by_user(self, user: TelegramUser) -> list[BankAccount]:
        return await self.account_repo.aget_accounts_by_user_id(user.id)

    def get_accounts(self) -> list[BankAccount]:
        return self.account_repo.get_accounts()

    def save_transaction(
        self, from_account: BankAccount, to_account: BankAccount, amount_money: Decimal, photo_name: Optional[str] = None
    ) -> None:
        self.transaction_repo.save_transaction(from_account, to_account, amount_money, photo_name)

    def get_or_create_account(self, number: str, user_id: int, balance: Decimal) -> tuple((BankAccount, bool)):
        return self.account_repo.get_or_create_account(number, self.user_repo.get_user_by_id(user_id), balance)

    @sync_to_async
    def send_money(
        self,
        payment_sender: str,
        payee: str,
        amount: str,
        message_sender: TelegramUser,
        photo_name: Optional[str] = None,
    ) -> None:
        def get_obj(obj):
            if len(obj) == 16 and obj.isdigit():
                response = self.get_account_by_card_number(obj)
            elif len(obj) == 20 and obj.isdigit():
                response = self.get_account_by_number(obj)
            elif obj.isdigit():
                response = self.get_account_by_user_id(int(obj))
            else:
                response = self.get_account_by_user_username(obj)
            return response

        amount = Decimal(amount)
        if amount < 0:
            raise CustomErrors.AmountMoney
        payment_sender = get_obj(payment_sender)
        if payment_sender.user != message_sender:
            raise CustomErrors.Sender
        payee = get_obj(payee)
        with transaction.atomic():
            payment_sender.balance = F("balance") - amount
            payee.balance = F("balance") + amount
            payment_sender.save()
            payee.save()
            self.save_transaction(
                from_account=payment_sender, to_account=payee, amount_money=amount, photo_name=photo_name
            )
