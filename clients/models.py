from django.db import models

from users.models import User


class Recipient(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="clients",
        null=True,
        blank=True,
        verbose_name="Владелец",
    )
    email = models.EmailField(verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"

        constraints = [models.UniqueConstraint(fields=["owner", "email"], name="unique_recipient_per_user")]
