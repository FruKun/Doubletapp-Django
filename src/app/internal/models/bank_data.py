from decimal import Decimal

from django.db import models
from django.db.models.functions import Length

models.CharField.register_lookup(Length)


class BankCard(models.Model):
    number = models.CharField(max_length=16, primary_key=True)
    account = models.ForeignKey("BankAccount", on_delete=models.PROTECT)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Bank card"
        verbose_name_plural = "Bank cards"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(number__length__gte=16),
                name="bankcard_number_length",
            )
        ]

    def __str__(self):
        return self.number


class BankAccount(models.Model):
    number = models.CharField(max_length=20, primary_key=True)
    balance = models.DecimalField(max_digits=20, decimal_places=3, default=0)
    user = models.ForeignKey("TelegramUser", on_delete=models.PROTECT)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Bank account"
        verbose_name_plural = "Bank accounts"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(number__length__gte=20),
                name="bankaccount_number_length",
            ),
            models.CheckConstraint(condition=models.Q(balance__gte=Decimal("0")), name="price_gte_0"),
        ]

    def __str__(self):
        return self.number
