from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from users.mixins import OwnerCreateMixin, OwnerQuerysetMixin
from users.services import is_manager

from .forms import MailingForm, MessageForm
from .models import Mailing, Message
from .services import MailingSenderService


class MailingListView(OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"mailings_list_{user.id}"

        mailings = cache.get(cache_key)

        if not mailings:

            if is_manager(self.request.user):
                mailings = Mailing.objects.all()
            else:
                mailings = Mailing.objects.filter(owner=user)

            cache.set(cache_key, mailings, 60)

        return mailings


class MailingDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mailing = self.object

        # Обновляем статус при открытии страницы
        mailing.update_status()

        # Подгружаем попытки с получателями
        context["attempts"] = mailing.attempts.select_related("recipient")

        return context

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(OwnerCreateMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user

        return super().form_valid(form)


class MailingUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не имеете права редактировать этот продукт")
        return obj


class MailingDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:list")

    def form_valid(self, form):
        messages.success(self.request, "Рассылка успешно удалена.")
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status == Mailing.Status.ACTIVE:
            messages.error(request, "Нельзя удалить активную рассылку.")
            return redirect("mailings:detail", pk=obj.pk)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не имеете права удалить этот продукт")
        return obj


def start_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.status == Mailing.Status.FINISHED:
        messages.error(request, "Рассылка уже завершена.")
        return redirect("mailings:list")

    try:
        # 1️⃣ Переводим в ACTIVE
        mailing.status = Mailing.Status.ACTIVE
        mailing.save()

        # 2️⃣ Запускаем сервис
        MailingSenderService.send_mail(mailing)

        # 3️⃣ После завершения → FINISHED
        mailing.status = Mailing.Status.FINISHED
        mailing.save()

        messages.success(request, "Рассылка успешно завершена!")

    except ValueError as e:
        mailing.status = Mailing.Status.CREATED
        mailing.save()
        messages.error(request, str(e))

    except Exception as e:
        mailing.status = Mailing.Status.CREATED
        mailing.save()
        messages.error(request, f"Ошибка: {str(e)}")

    return redirect("mailings:detail", pk=mailing.pk)


class MessageListView(OwnerQuerysetMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, OwnerCreateMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("mailings:message_list")


class MessageUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не имеете права редактировать этот продукт")
        return obj


class MessageDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        messages.success(self.request, "Сообщение успешно удалено.")
        return super().form_valid(form)

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не имеете права удалить этот продукт")
        return obj


@login_required
@require_POST
def disable_mailing(request, mailing_id):
    if not is_manager(request.user):
        raise PermissionDenied

    mailing = get_object_or_404(Mailing, id=mailing_id)

    if mailing.status != Mailing.Status.FINISHED:
        mailing.status = Mailing.Status.FINISHED
        mailing.save()

    return redirect("mailings:list")
