from django.http import JsonResponse

from app.internal.models.bank_data import BankAccount, BankCard


def get_user(request):
    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Dont have user_id"}, status=400)

    try:
        cards = list(BankCard.objects.select_related("account", "account__user").filter(account__user__id=user_id))
        accounts = BankAccount.objects.filter(user__id=user_id)
    except BankAccount.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)
    data = {
        "user id": cards[0].account.user.id,
        "full name": cards[0].account.user.full_name,
        "username": cards[0].account.user.username,
        "phone number": cards[0].account.user.phone_number,
        "bank accounts": {i.number: f"balance:{i.balance}" for i in accounts},
        "bank cards": {i.number: {"account": i.account.number, "balance": i.available_balance} for i in cards},
    }
    return JsonResponse(data)
