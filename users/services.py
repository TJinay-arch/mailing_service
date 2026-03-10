def is_manager(user):
    return user.groups.filter(name="manager").exists()
