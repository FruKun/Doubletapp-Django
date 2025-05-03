from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.history_data import TransactionHistory
from app.internal.db.models.user_data import TelegramUser
from app.internal.db.repositories.account_repository import AccountRepository
from app.internal.db.repositories.transaction_repository import TransactionHistoryRepository
from app.internal.domain.services import CustomErrors


class TransactionService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionHistoryRepository()

    async def get_account_by_number(self, number: str) -> BankAccount:
        if account := await self.account_repo.aget_account_by_number(number):
            return account
        raise BankAccount.DoesNotExist

    async def aget_transactions_by_account(self, account: BankAccount) -> list[TransactionHistory]:
        return await self.transaction_repo.aget_transactions_by_account(account)

    async def aget_usernames_by_user_id(self, id: int) -> list[dict]:
        return await self.account_repo.aget_usernames_by_user_id(id)

    async def account_history(self, user: TelegramUser, account_number: str) -> list[TransactionHistory]:
        if not account_number.isdigit() or not len(account_number) == 20:
            raise CustomErrors.InvalidFieldValue
        account = await self.get_account_by_number(account_number)
        if user != account.user:
            raise CustomErrors.Sender
        return await self.aget_transactions_by_account(account)

    async def all_usernames(self, user: TelegramUser) -> list[str]:
        account_list = await self.aget_usernames_by_user_id(user.id)
        uniq_usernames = set()
        for account in account_list:
            uniq_usernames.add(account["transactionhistory_from__to_account__user__username"])
            uniq_usernames.add(account["transactionhistory_to__from_account__user__username"])
        uniq_usernames.remove(None)
        return uniq_usernames

    async def unseen_receipts(self, user: TelegramUser) -> list[TransactionHistory]:
        accounts = await self.account_repo.aget_accounts_by_user_id(user.id)
        histories = []
        for account in accounts:
            extend = await self.transaction_repo.aget_unviewed_transactions_by_account(account)
            histories.extend(extend)
        return histories

    async def amark_is_viewed(self, history: TransactionHistory):
        history.is_viewed = True
        await history.asave()
