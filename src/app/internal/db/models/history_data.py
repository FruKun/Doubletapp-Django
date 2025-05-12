from django.db import models


class TransactionHistory(models.Model):
    from_account = models.ForeignKey("BankAccount", on_delete=models.CASCADE, related_name="transactionhistory_from")
    to_account = models.ForeignKey("BankAccount", on_delete=models.CASCADE, related_name="transactionhistory_to")
    amount_money = models.DecimalField(max_digits=20, decimal_places=3, default=0)
    photo_name = models.CharField(default=None, blank=True, null=True, unique=True)
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Transaction History"
        verbose_name_plural = "Transaction Histories"

    def __str__(self):
        return "record " + str(self.id)
