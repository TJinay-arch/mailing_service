from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from clients.models import Recipient
from users.models import User


class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True)

    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("can_disable_message", "Can disable message"),
        ]


class Mailing(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Создана"
        ACTIVE = "active", "Запущена"
        FINISHED = "finished", "Завершена"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True)

    start_time = models.DateTimeField(verbose_name="Начало рассылки")
    end_time = models.DateTimeField(verbose_name="Окончание рассылки")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, verbose_name="Статус")

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailings", verbose_name="Сообщение")

    recipients = models.ManyToManyField(Recipient, related_name="mailings", verbose_name="Получатели")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Рассылка #{self.id}"

    def clean(self):
        now = timezone.localtime()

        if self.start_time < now:
            raise ValidationError({"start_time": "Дата начала не может быть в прошлом"})

        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "Дата окончания должна быть позже даты начала"})

    def update_status(self):
        now = timezone.now()

        if now < self.start_time:
            new_status = self.Status.CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.Status.ACTIVE
        else:
            new_status = self.Status.FINISHED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    @property
    def total_attempts(self):
        return self.attempts.count()

    @property
    def successful_attempts(self):
        return self.attempts.filter(status=MailingAttempt.AttemptStatus.SUCCESS).count()

    @property
    def failed_attempts(self):
        return self.attempts.filter(status=MailingAttempt.AttemptStatus.FAILED).count()

    @property
    def success_rate(self):
        total = self.total_attempts
        if total == 0:
            return 0
        return round((self.successful_attempts / total) * 100, 2)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

        permissions = [
            ("disable_mailing", "Can disable mailing"),
        ]


class MailingAttempt(models.Model):
    class AttemptStatus(models.TextChoices):
        SUCCESS = "success", "Успешно"
        FAILED = "failed", "Не успешно"

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")

    status = models.CharField(max_length=10, choices=AttemptStatus.choices, verbose_name="Статус")

    server_response = models.TextField(blank=True, verbose_name="Ответ почтового сервера")

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="attempts", verbose_name="Рассылка")

    recipient = models.ForeignKey(
        Recipient, on_delete=models.CASCADE, related_name="attempts", verbose_name="Получатель"
    )

    def __str__(self):
        return f"{self.mailing} — {self.recipient.email} — {self.get_status_display()}"

    class Meta:
        verbose_name = "Попытка отправки письма"
        verbose_name_plural = "Попытки отправки писем"
        ordering = ["-attempt_time"]
