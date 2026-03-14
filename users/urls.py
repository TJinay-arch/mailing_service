from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .forms import StyledPasswordResetForm, StyledSetPasswordForm
from .views import (ConfirmEmailView, CustomLoginView, CustomLogoutView,
                    ManagerDashboardView, ProfileUpdateView, ProfileView,
                    RegisterView, UserListView, block_user)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("confirm/<uuid:token>/", ConfirmEmailView.as_view(), name="confirm_email"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            form_class=StyledPasswordResetForm,
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",
            subject_template_name="users/password_reset_subject.txt",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=StyledSetPasswordForm,
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("users/", UserListView.as_view(), name="user_list"),
    path("block/<int:user_id>/", block_user, name="block_user"),
    path(
        "dashboard/",
        ManagerDashboardView.as_view(),
        name="dashboard",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
