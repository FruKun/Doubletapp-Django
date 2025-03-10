from django.http import JsonResponse

from app.internal.models.user_data import TelegramUser


def get_user(request):
    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Dont have user_id"}, status=400)

    try:
        user = TelegramUser.objects.prefetch_related("bankaccount_set", "bankaccount_set__bankcard_set").get(id=user_id)
        data = {
            i.number: {
                "balance": i.balance,
                "cards": {j.number: {"available_balance": j.available_balance} for j in i.bankcard_set.all()},
            }
            for i in user.bankaccount_set.all()
        }
    except TelegramUser.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)

    data = {
        "user id": user.id,
        "full name": user.full_name,
        "username": user.username,
        "phone number": user.phone_number,
        "bank accounts": data,
    }

    return JsonResponse(data)
