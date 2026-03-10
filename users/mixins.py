from django.core.exceptions import PermissionDenied


class ManagerRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="manager").exists():
            raise PermissionDenied("Требуются права менеджера")

        return super().dispatch(request, *args, **kwargs)


class OwnerQuerysetMixin:
    owner_field = "owner"

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.groups.filter(name="manager").exists():
            return qs

        return qs.filter(**{self.owner_field: self.request.user})


class OwnerCreateMixin:

    owner_field = "owner"

    def form_valid(self, form):

        setattr(form.instance, self.owner_field, self.request.user)

        return super().form_valid(form)
