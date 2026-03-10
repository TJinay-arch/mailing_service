from django.contrib import admin

from .models import User

admin.site.register(User)


@admin.action(description="Заблокировать пользователей")
def block_users(modeladmin, request, queryset):

    queryset.update(is_active=False)


class UserAdmin(admin.ModelAdmin):

    actions = [block_users]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
