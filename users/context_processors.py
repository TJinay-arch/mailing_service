def manager_status(request):
    if request.user.is_authenticated:
        is_manager = request.user.groups.filter(name="manager").exists()
    else:
        is_manager = False

    return {"is_manager": is_manager}
