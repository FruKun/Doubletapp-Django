from ninja import ModelSchema, Schema

from app.internal.db.models.bank_data import BankAccount


class BankAccountSchema(ModelSchema):
    class Meta:
        model = BankAccount
        fields = ["number", "user", "balance"]


class MessageAccountSchema(Schema):
    message: str
    number: str


class PostBankAccountSchema(Schema):
    number: str
    user_id: int
    balance: int
