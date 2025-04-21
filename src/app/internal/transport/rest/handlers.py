from http import HTTPStatus

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from app.internal.models.user_data import TelegramUser
from app.internal.serializers import CustomTokenObtainPairSerializer


class TelegramLoginView(APIView):
    def post(self, request):
        id = request.data.get("id")
        if not id:
            return Response({"error": "id required"}, status=HTTPStatus.BAD_REQUEST)
        try:
            user = TelegramUser.objects.get(id=id)
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
        except TelegramUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=HTTPStatus.NOT_FOUND)


class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.GET.get("user_id")
        if not user_id:
            return Response({"error": "Dont have user_id"}, status=HTTPStatus.BAD_REQUEST)

        try:
            user = TelegramUser.objects.prefetch_related("bankaccount_set", "bankaccount_set__bankcard_set").get(
                id=user_id
            )
            data = {
                i.number: {
                    "balance": i.balance,
                    "cards": {"number": j.number for j in i.bankcard_set.all()},
                }
                for i in user.bankaccount_set.all()
            }
        except TelegramUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=HTTPStatus.NOT_FOUND)

        data = {
            "user id": user.id,
            "full name": user.full_name,
            "username": user.username,
            "phone number": user.phone_number,
            "bank accounts": data,
        }

        return Response(data, status=HTTPStatus.OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
