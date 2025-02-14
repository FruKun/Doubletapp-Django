from django.db import models


class UserData(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True, null=True)
    phone_number = models.CharField(max_length=30, unique=True, null=True)

    def __str__(self):
        return self.full_name
