from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.internal.transport.rest.handlers import TelegramLoginView, UserView

urlpatterns = [
    path("login/", TelegramLoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("get_user", UserView.as_view()),
]
