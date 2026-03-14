from django.urls import path

from .views import (AttemptListView, MailingCreateView, MailingDeleteView,
                    MailingDetailView, MailingListView, MailingUpdateView,
                    MessageCreateView, MessageDeleteView, MessageListView,
                    MessageUpdateView, disable_mailing, start_mailing, MailingReportView)

app_name = "mailings"

urlpatterns = [
    path("", MailingListView.as_view(), name="list"),
    path("<int:pk>/", MailingDetailView.as_view(), name="detail"),
    path("create/", MailingCreateView.as_view(), name="create"),
    path("<int:pk>/update/", MailingUpdateView.as_view(), name="update"),
    path("mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailings/<int:mailing_id>/disable/", disable_mailing, name="disable"),
    path("mailings/<int:pk>/start/", start_mailing, name="start"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("attempts/", AttemptListView.as_view(), name="attempts"),
    path("reports/", MailingReportView.as_view(), name="reports"),

]
