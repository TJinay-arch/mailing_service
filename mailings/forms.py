from django import forms

from clients.models import Recipient

from .models import Mailing, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["message", "start_time", "end_time", "recipients"]

        widgets = {
            "message": forms.Select(attrs={"class": "form-select"}),
            "start_time": forms.DateTimeInput(attrs={"class": "form-control datetimepicker"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control datetimepicker"}),
            "recipients": forms.SelectMultiple(
                attrs={
                    "class": "form-select select2",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Показываем только сообщения пользователя
            self.fields["message"].queryset = Message.objects.filter(owner=user)

            # Показываем только получателей пользователя
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
        }


