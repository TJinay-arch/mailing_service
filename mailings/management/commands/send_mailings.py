from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing
from mailings.services import send_mail


class Command(BaseCommand):

    help = "Отправка активных рассылок"

    def handle(self, *args, **kwargs):

        now = timezone.now()

        mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
        )

        for mailing in mailings:

            send_mail(mailing)

        self.stdout.write("Рассылки отправлены")