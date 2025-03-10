from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.internal.models.admin_user import AdminUser
from app.internal.models.user_data import TelegramUser


@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    pass


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "username", "phone_number", "created_at")
    readonly_fields = ("created_at",)
