from django.contrib import admin

from app.internal.models.history_data import TransactionHistory


@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ("from_account", "to_account", "amount_money", "date", "time")
    readonly_fields = ("from_account", "to_account", "amount_money", "date", "time")

    def has_add_permission(self, request):
        return False
