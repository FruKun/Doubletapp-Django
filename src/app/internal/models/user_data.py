from django.db import models


class UserData(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name
