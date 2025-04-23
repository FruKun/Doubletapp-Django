from ninja import ModelSchema

from app.internal.db.models.bank_data import BankCard


class BankCardSchema(ModelSchema):
    class Meta:
        model = BankCard
        fields = ["number", "account"]
