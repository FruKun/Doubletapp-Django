from django.contrib import admin

from app.internal.presentation.admin.admin_bank import BankAccountAdmin, BankCardAdmin
from app.internal.presentation.admin.admin_history import TransactionHistoryAdmin
from app.internal.presentation.admin.admin_user import TelegramUserAdmin

admin.site.site_title = "Backend course"
admin.site.site_header = "Backend course"
