from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from users.mixins import OwnerCreateMixin, OwnerQuerysetMixin
from users.services import is_manager

from .forms import RecipientForm
from .models import Recipient


class RecipientListView(OwnerQuerysetMixin, ListView):
    model = Recipient
    template_name = "clients/recipient_list.html"
    context_object_name = "recipients"
    paginate_by = 10

    def get_queryset(self):

        user = self.request.user
        page = self.request.GET.get("page", 1)

        # уникальный ключ кеша
        cache_key = f"recipients_{user.id}_{page}"

        recipients = cache.get(cache_key)

        if recipients is None:

            qs = super().get_queryset()

            if user.groups.filter(name="manager").exists():
                recipients = qs
            else:
                recipients = qs.filter(owner=user)

            cache.set(cache_key, recipients, 60)

        return recipients


class RecipientDetailView(OwnerQuerysetMixin, DetailView):
    model = Recipient
    template_name = "clients/recipient_detail.html"
    context_object_name = "recipient"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(owner=self.request.user)


class RecipientCreateView(OwnerCreateMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "clients/recipient_form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user

        return super().form_valid(form)


class RecipientUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "clients/recipient_form.html"
    success_url = reverse_lazy("clients:list")

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не имеете права редактировать этот продукт")
        return obj


class RecipientDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Recipient
    template_name = "clients/recipient_confirm_delete.html"
    success_url = reverse_lazy("clients:list")

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не имеете права удалить этот продукт")
        return obj
