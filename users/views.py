from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, TemplateView, View

from mailings.models import Mailing, MailingAttempt

from .forms import UserLoginForm, UserRegisterForm
from .models import User
from .services import is_manager


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        confirm_link = self.request.build_absolute_uri(
            reverse_lazy("users:confirm_email", args=[str(user.email_token)])
        )

        html_message = render_to_string("users/email_confirmation.html", {"user": user, "confirm_link": confirm_link})

        plain_message = strip_tags(html_message)

        send_mail(
            subject="Подтверждение регистрации",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        )

        return super().form_valid(form)


class ConfirmEmailView(View):
    def get(self, request, token):
        user = get_object_or_404(User, email_token=token)
        user.is_active = True
        user.is_email_confirmed = True
        user.save()
        return redirect("users:login")


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = UserLoginForm


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


@login_required
@require_POST
def block_user(request, user_id):

    if not is_manager(request.user):
        raise PermissionDenied

    user = get_object_or_404(User, id=user_id)

    if user != request.user:
        user.is_active = False
        user.save()

    return redirect("users:user_list")


class ManagerDashboardView(TemplateView):

    template_name = "users/dashboard.html"

    def dispatch(self, request, *args, **kwargs):

        if not is_manager(request.user):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["users_count"] = User.objects.count()

        context["active_mailings"] = Mailing.objects.filter(status=Mailing.Status.ACTIVE).count()

        context["sent_emails"] = MailingAttempt.objects.filter(status=MailingAttempt.AttemptStatus.SUCCESS).count()

        context["failed_emails"] = MailingAttempt.objects.filter(status=MailingAttempt.AttemptStatus.FAILED).count()

        return context
