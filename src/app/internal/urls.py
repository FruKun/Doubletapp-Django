from django.urls import path

from app.internal.transport.rest.handlers import get_user

urlpatterns = [
    path("get_user", get_user),
]
