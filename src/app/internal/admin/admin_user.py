from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from app.internal.models.user_data import TelegramUser


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = TelegramUser
        fields = ("id", "username", "full_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = TelegramUser
        fields = ("id", "username", "full_name")


@admin.register(TelegramUser)
class TelegramUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ("id", "full_name", "username", "phone_number", "list_of_favourites", "is_superuser", "created_at")
    list_filter = ("is_superuser",)
    readonly_fields = ("created_at",)
    fieldsets = [
        (
            None,
            {"fields": ["id", "username", "full_name", "phone_number", "list_of_favourites", "password", "created_at"]},
        ),
        ("Permissions", {"fields": ["is_active", "is_superuser"]}),
    ]
    add_fieldsets = [
        (
            None,
            {"fields": ["id", "username", "full_name", "phone_number", "list_of_favourites", "password1", "password2"]},
        ),
        ("Permissions", {"fields": ["is_active", "is_superuser"]}),
    ]
