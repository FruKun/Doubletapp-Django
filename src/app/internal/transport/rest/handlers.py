from django.http import JsonResponse

from app.internal.models.user_data import UserData


def get_user(request):
    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Dont have user_id"}, status=400)

    try:
        user = UserData.objects.get(id=user_id)
    except UserData.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)
    data = {
        "user_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "phone_number": user.phone_number,
    }
    return JsonResponse(data)
