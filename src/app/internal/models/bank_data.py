from django.db import models


class BankCard(models.Model):
    number = models.CharField(max_length=20, primary_key=True)
    account = models.ForeignKey("BankAccount", on_delete=models.PROTECT)
    available_balance = models.DecimalField(max_digits=20, decimal_places=3, default=0)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Bank card"
        verbose_name_plural = "Bank cards"

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

    def __str__(self):
        return self.number
