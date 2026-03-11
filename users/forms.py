from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm, UserCreationForm)

from .models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "avatar", "country", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Введите email"})

        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите имя пользователя"}
        )

        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Введите пароль"})

        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Повторите пароль"})

        self.fields["country"].widget.attrs.update({"class": "form-control", "placeholder": "Укажите страну"})

        self.fields["avatar"].widget.attrs.update({"class": "form-control"})

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Изображение не должно превышать 2 МБ.")
            if not avatar.content_type.startswith("image/"):
                raise forms.ValidationError("Файл должен быть изображением.")
        return avatar


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Введите email"})

        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "Введите пароль"})


class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Введите email"})


class StyledSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
