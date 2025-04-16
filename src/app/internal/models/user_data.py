from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models


class TelegramUserManager(BaseUserManager):
    def create_user(self, id, username, full_name, password=None):
        user = self.model(id=id, username=username, full_name=full_name)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, id, username, full_name, password=None):
        user = self.create_user(id, username, full_name, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class TelegramUser(AbstractUser, PermissionsMixin):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True, null=True)
    phone_number = models.CharField(max_length=30, unique=True, null=True)
    list_of_favourites = ArrayField(models.CharField(max_length=255, unique=True), blank=True, default=list)
    created_at = models.DateField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    password = models.CharField(default=None, max_length=128, null=True, verbose_name="password")
    email = None

    objects = TelegramUserManager()

    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ["username", "full_name"]

    def has_usable_password(self):
        return bool(self.password)

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self):
        return self.full_name
