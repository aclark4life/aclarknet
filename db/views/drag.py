from django.http import JsonResponse


def save_positions(request):
    if request.method == "POST":
        profile = request.user.profile
        positions = request.POST.get("positions")
        profile.draggable_positions = positions
        profile.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})
