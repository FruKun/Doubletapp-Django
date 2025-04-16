from django.contrib import admin

from app.internal.admin.admin_bank import BankAccountAdmin, BankCardAdmin
from app.internal.admin.admin_history import TransactionHistoryAdmin
from app.internal.admin.admin_user import TelegramUserAdmin

admin.site.site_title = "Backend course"
admin.site.site_header = "Backend course"
