from django.contrib import admin

from app.internal.db.models.bank_data import BankAccount, BankCard


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "balance", "created_at")
    readonly_fields = ("created_at",)


@admin.register(BankCard)
class BankCardAdmin(admin.ModelAdmin):
    list_display = ("number", "account", "account__balance", "expiration_date", "cvv", "created_at")
    readonly_fields = ("created_at",)
