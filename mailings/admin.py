from django.contrib import admin

from .models import Mailing, MailingAttempt, Message

admin.site.register(Message)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "status",
        "start_time",
        "end_time",
    )

    list_filter = ("status",)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name="manager").exists():
            return False

        return super().has_change_permission(request, obj)


admin.site.register(MailingAttempt)
