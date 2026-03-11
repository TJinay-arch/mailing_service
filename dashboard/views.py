from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from clients.models import Recipient
from mailings.models import Mailing
from users.services import is_manager


class DashboardView(TemplateView):

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = self.request.user

        if not user.is_authenticated:
            return context

        cache_key = f"dashboard_{user.id}"

        data = cache.get(cache_key)

        if not data:
            if is_manager(self.request.user):
                data = {
                    "total_mailings": Mailing.objects.all().count(),
                    "total_recipients": Recipient.objects.all().count(),
                    "active_mailings": Mailing.objects.filter(status="active").count(),
                }
            else:
                data = {
                    "total_mailings": Mailing.objects.filter(owner=user).count(),
                    "total_recipients": Recipient.objects.filter(owner=user).count(),
                    "active_mailings": Mailing.objects.filter(owner=user, status="active").count(),
                }

            cache.set(cache_key, data, 60)

        context.update(data)

        return context


@method_decorator(
    cache_control(public=True, max_age=3600),
    name="dispatch",
)
class HomeAdvertiseView(TemplateView):
    template_name = "dashboard/home_advertise.html"
