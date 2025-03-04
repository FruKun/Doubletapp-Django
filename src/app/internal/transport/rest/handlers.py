from django.http import JsonResponse

from app.internal.models.user_data import TelegramUser


def get_user(request):
    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Dont have user_id"}, status=400)

    try:
        user = TelegramUser.objects.get(id=user_id)
        bank_account = {
            i.number: {"balance": i.balance, "cards": [j.number for j in i.bankcard_set.all()]}
            for i in user.bankaccount_set.all()
        }
    except TelegramUser.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)
    data = {
        "user id": user.id,
        "full name": user.full_name,
        "username": user.username,
        "phone number": user.phone_number,
        "bank accounts": bank_account,
    }
    return JsonResponse(data)
