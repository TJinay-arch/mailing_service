from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import MailingAttempt


class MailingSenderService:

    @staticmethod
    def send_mail(mailing, ignore_time=False):

        if not ignore_time:
            now = timezone.localtime()
            if not (mailing.start_time <= now <= mailing.end_time):
                raise ValueError("Рассылка не может быть запущена в данный период")

        recipients = mailing.recipients.all()

        if not recipients.exists():
            raise ValueError("Нет получателей для рассылки")

        for recipient in recipients:
            try:
                response = send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.AttemptStatus.SUCCESS,
                    server_response=f"Sent: {response}",
                )

            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.AttemptStatus.FAILED,
                    server_response=str(e),
                )
