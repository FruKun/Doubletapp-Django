from django.contrib.postgres.fields import ArrayField
from django.db import models


class TelegramUser(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True, null=True)
    phone_number = models.CharField(max_length=30, unique=True, null=True)
    list_of_favourites = ArrayField(models.CharField(max_length=255, unique=True), blank=True, default=list)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self):
        return self.full_name
