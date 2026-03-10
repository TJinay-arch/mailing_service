from django.utils import timezone
from django.views.generic import TemplateView

from clients.models import Recipient
from mailings.models import Mailing


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()

        context["total_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status=Mailing.Status.ACTIVE,
        ).count()
        context["total_recipients"] = Recipient.objects.count()

        return context
